#
# Create context menu items
#
import logging
import os
import traceback
import subprocess
from urllib.parse import urlparse
from gi.repository import Nautilus
from collections import deque

# Set up logging
logger = logging.getLogger('actions_for_nautilus')

class MenuCacheItem:
    def __init__(self, group, path, mtime, ctime, menu):
        self.group = group
        self.path = path
        self.mtime = mtime
        self.ctime = ctime
        self.menu = menu

class MenuCache:
    def __init__(self):
        self.cache = deque([])

    def get_menu(self, group, path, mtime, ctime):
        return next((item.menu for item in reversed(self.cache) if item.group == group and item.path == path and item.mtime == mtime and item.ctime == ctime), None)

    def put_menu(self, group, path, mtime, ctime, menu):
        exists = next((index for (index, item) in enumerate(self.cache) if item.group == group and item.path == path), len(self.cache))
        if exists < len(self.cache):
            self.cache[exists].mtime = mtime
            self.cache[exists].ctime = ctime
            self.cache[exists].menu = menu
        else:
            self.cache.append(MenuCacheItem(group, path, mtime, ctime, menu))

        while len(self.cache) > 5:
            self.cache.popleft()

    def clear(self):
        self.cache = deque([])

menu_cache = MenuCache()
last_config_time = None

#
# Consolidate background and selection calls to create menus
#
# files is a list of __gi__.NautilusVFSFile instances
#
def create_menu_items(config, files, group, act_function):
    global menu_cache
    global last_config_time
    # Clear cache if the config has been updated
    if last_config_time is None or last_config_time < config.mtime:
        menu_cache.clear()
        last_config_time = config.mtime

    try:
        # For single files get any cached menu and return that
        single_file_path = files[0].get_location().get_path() if len(files) == 1 else None
        mtime = None
        ctime = None
        if single_file_path is not None:
            stat = os.stat(single_file_path)
            mtime = stat.st_mtime
            ctime = stat.st_ctime
            cached_menu = menu_cache.get_menu(group, single_file_path, mtime, ctime)
            if cached_menu is not None:
                logger.debug(f"RETURNING CACHED MENU FOR {single_file_path}: {cached_menu}")
                return cached_menu
        # for f in files:
        #   logger.debug(f.get_uri())
        #   loc = f.get_location()
        #   logger.debug(f"  {f.get_file_type()}")
        #   logger.debug(f"  {f.get_mime_type()}")
        #   logger.debug(f"  {loc.get_basename()}")
        #   logger.debug(f"  {loc.get_parent()}")
        #   logger.debug(f"  {loc.get_parse_name()}")
        #   logger.debug(f"  {loc.get_path()}")
        #   logger.debug(f"  {loc.get_uri()}")
        #   logger.debug(f"  {loc.get_uri_scheme()}")

        my_files = list(filter(None, map(lambda file: {
                "mimetype": file.get_mime_type(),
                "filetype": file.get_file_type(),
                "basename": os.path.basename(file.get_location().get_path()),
                "filepath": file.get_location().get_path(),
                "folder": os.path.dirname(file.get_location().get_path()),
                "uri": urlparse(file.get_uri())
            } if file.get_location().get_path() is not None else None, files)))

        actions = list(filter(None, map(lambda action: _create_menu_item(action, my_files, group, act_function), config.actions)))
        menu = sorted(actions, key=lambda element: element.props.label) if config.sort else actions

        # For single files cache the menu
        if single_file_path is not None:
            menu_cache.put_menu(group, single_file_path, mtime, ctime, menu)

        return menu

    except Exception as e:
        logger.error(f"Error constructing menu items - Group: {group}, Files: {files}, Exception: {e}\nTraceback: {traceback.format_exc()}")
        return []

#
# Triage the menu item creation based on type
#
def _create_menu_item(action, files, group, act_function):
    if len(files) > 0:
        if type(action).__name__ == "MenuAction":
            return _create_submenu_menu_item(action, files, group, act_function)
        else:
            return _create_command_menu_item(action, files, group, act_function)
    else:
        return []

#
# Generate an item that has a submenu attached, with its own actions recursively added
#
def _create_submenu_menu_item(action, files, group, act_function):
    actions = list(filter(None, map(lambda action: _create_menu_item(action, files, group, act_function), action.actions)))

    if len(actions) > 0:
        menu = Nautilus.Menu()
        menu_item = Nautilus.MenuItem(
            name="Actions4Nautilus: :Menu" + action.idString + group,
            label=action.label,
        )
        menu_item.set_submenu(menu)
        for menu_sub_item in (sorted(actions, key=lambda element: element.props.label) if action.sort else actions):
            menu.append_item(menu_sub_item)
        return menu_item

def _is_command_true(cmd):
    try:
        logger.debug(f"Running show_if_true command <{cmd}>")
        process = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        logger.debug(f"show_if_true_command {cmd} returned: stdout={process.stdout}, stderr={process.stderr}")
        if process.stdout.rstrip() == "true":
            return True

    except Exception as e:
        logger.error(f"show_if_true_command failed: {cmd}", exc_info=e)

    return False
#
# Generate a command item that is connected to the activate signal
#
def _create_command_menu_item(action, files, group, activate_function):
    #
    # Eliminate all other conditions before the very expensive "call a program" option
    # Optimized short-circuit evaluation: cheapest checks first, most expensive last
    files_count = len(files)
    if not (
        # Phase 1: Fastest - Simple integer comparisons (cost: ~1-2 operations)
        action.min_items <= files_count and
        (action.max_items == 0 or action.max_items >= files_count) and
        
        # Phase 2: Fast - Enum comparisons (cost: ~2-5 operations per file)
        _applicable_to_filetype(action, files) and
        
        # Phase 3: Medium - String operations (cost: ~5-15 operations per file)
        _applicable_to_mimetype(action, files) and
        
        # Phase 4: Expensive - Regex operations (cost: ~10-30 operations per file)
        _applicable_to_path_patterns(action, files) and
        
        # Phase 5: Most Expensive - Filesystem calls (cost: ~50-200 operations per file)
        (action.permissions == "" or _applicable_to_permissions(action, files))
    ):
        return None

    if len(action.show_if_true) > 0:
        cmd = action.show_if_true
        if '%F' in cmd:
            cmd = cmd.replace('%F', ' '.join(f"'{f['filepath']}'" for f in files))
        if '%f' in cmd:
            for file in files:
                if not _is_command_true(cmd.replace('%f', f"'{file['filepath']}'")):
                    return None
        else:
            if not _is_command_true(cmd):
                return None

    name = "Actions4Nautilus: :Item" + action.idString + group
    label = action.label
    logger.debug(f"Attaching menu item: file={files[0]} name={name}, label={label}")
    menu_item = Nautilus.MenuItem(name=name, label=label)
    menu_item.connect("activate", activate_function, action, files)
    return menu_item

#
#  In the following, the relevant attributes of the selected files
#  are compared to the "p_rules" (positive rules) and "n_rules"(negative rules) of
#  each class of attribute. At least one p_rule must match while no n_rules must
#  match, for all files in the selection
#

#
# Compares each file mimetype to the action mimetypes
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_mimetype(action, files):
    if len(files) > 1 and action.mimetypes_strict_match:
        # Strict match - the first file is checked for type acceptability,
        # then all other files must have the same type as the first file
        file_0_type = files[0]["mimetype"]
        return (_all_applicable_to_mimetype(action, [files[0]])
        and all(file_0_type == file["mimetype"] for file in files[1: ]))

    return _all_applicable_to_mimetype(action, files)

def _all_applicable_to_mimetype(action, files):
    return True if action.all_mimetypes else (all(map(lambda file: (
        (len(action.mimetypes["p_rules"]) == 0 or any(getattr(file["mimetype"], p_rule["comparator"])(p_rule["mimetype"]) for p_rule in action.mimetypes["p_rules"])) and
        not any(getattr(file["mimetype"], n_rule["comparator"])(n_rule["mimetype"]) for n_rule in action.mimetypes["n_rules"])), files)))

#
# Compares each file type to the action filetypes
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_filetype(action, files):
    if len(files) > 1 and action.filetypes_strict_match:
        # Strict match - the first file is checked for type acceptability,
        # then all other files must have the same type as the first file
        file_0_type = files[0]["filetype"]
        return (_all_applicable_to_filetype(action, [files[0]])
        and all(file_0_type == file["filetype"] for file in files[1: ]))

    return _all_applicable_to_filetype(action, files)

def _all_applicable_to_filetype(action, files):
    return True if (action.all_filetypes) else all(map(lambda file: (
        (len(action.filetypes["p_rules"]) == 0 or any((file["filetype"] == p_rule["filetype"]) for p_rule in action.filetypes["p_rules"])) and
        not any((file["filetype"] == n_rule["filetype"]) for n_rule in action.filetypes["n_rules"])), files))

#
# Compares each file path to the action path_patterns
# Returns True if a match is found for every one, otherwise False
#
# Strict match is far more complex here!
#
# Firstly, the action has to have a none-empty set of p_rules (otherwise there is nothing
# more strict that we can apply)
#
# The FIRST file must pass all the rules, and we must get the p_rule it passed.
#
# All other files must pass that same p_rule AND pass all the n_rules.
#
# So, since everything must always be passed through any n_rules, we check those first
#
def _applicable_to_path_patterns(action, files):
    if action.all_path_patterns:
        return True
    if not (len(action.path_patterns["n_rules"]) == 0 or
        all(all((_test_rule(n_rule, file["filepath"]) is None) for n_rule in action.path_patterns["n_rules"]) for file in files)):
        return False

    if len(action.path_patterns["p_rules"]) == 0:
        return True

    # everything passes the n_rules and there are p_rules to use.
    # for the p_rules, we pick the rule set to compare against - if it's
    # a case where strict match doesn't apply (only one file, or flag is off) we apply
    # all the rules to everything. Otherwise we apply the first rule that the first file
    # passes (if any) to everything else
    #
    # This can be done with lots of embedded comprehensions but then, ironically, the
    # logic becomes incomprehensible!
    #
    if len(files) < 2 or not action.path_patterns_strict_match:
        p_rules = action.path_patterns["p_rules"]
        p_files = files
    else:
        p_files = files[1: ]
        p_rule = next((p_rule for p_rule in action.path_patterns["p_rules"] if _test_rule(p_rule, files[0]["filepath"])), None)
        if p_rule is None:
            return False
        p_rules = [p_rule]

    return len(p_rules) > 0 and all(any(_test_rule(p_rule, file["filepath"]) is not None for p_rule in p_rules) for file in p_files)

def _test_rule(rule, string):
    return rule["comparator"](string)

# def _test_rule(rule, string):
#   logger.debug(rule, string)
#   result = rule["comparator"](string)
#   logger.debug(result)
#   return result

#
# Ensures that the user has at least the stated permissions to access each file (or
# does NOT have the stated permissions if we are "notting")
# Returns True if OK for every one, otherwise False
#
# Note that the user must always have read access if permissions are being checked
#
def _applicable_to_permissions(action, files):
    if action.permissions_not:
        return all(map(lambda file: (os.access(file["filepath"], os.R_OK) and not os.access(file["filepath"], action.permissions)), files))
    else:
        return all(map(lambda file: os.access(file["filepath"], action.permissions), files))
