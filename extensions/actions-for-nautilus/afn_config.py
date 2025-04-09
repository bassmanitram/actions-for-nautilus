#
# Config management
#
import os, json, threading, time, fnmatch, re
import afn_place_holders
from gi.repository import Gio, GLib

HOME = os.environ.get('HOME')
_config_path = HOME + "/.local/share/actions-for-nautilus/config.json"

def _dump_dict(o) -> str:
    attrs = o.__dict__
    return ', '.join("%s: %s" % item for item in sorted(attrs.items(), key=lambda i: i[0]))

_filetypes = {
    "unknown":       [Gio.FileType(0)],
    "file":          [Gio.FileType(1)],
    "directory":     [Gio.FileType(2)],
    "symbolic-link": [Gio.FileType(3)],
    "special":       [Gio.FileType(4)],
    "shortcut":      [Gio.FileType(5)],
    "mountable":     [Gio.FileType(6)],
    "standard":      [Gio.FileType(1), Gio.FileType(2), Gio.FileType(3)]
}

_permissions = {
    "read": os.R_OK,
    "read-write": os.R_OK | os.W_OK,
    "read-execute": os.R_OK | os.X_OK,
    "read-write-execute": os.R_OK | os.W_OK | os.X_OK
}

debug = False
def debug_print(str):
    if debug:
        print(str)

class CommandAction():
    def __init__(self):
        self.label  = ""
        self.command_line = ""
        self.cmd_behaviour = ""
        self.cwd = ""
        self.show_if_true = ""
        self.permissions = ""
        self.use_shell = False
        self.min_items = 1
        self.max_items = 0
        self.all_mimetypes = True
        self.mimetypes = []
        self.all_filetypes = True
        self.filetypes = []
        self.all_path_patterns = True
        self.path_patterns = []
        self.idString = ""

    def __repr__(self) -> str:
        return _dump_dict(self)

class MenuAction():
    def __init__(self):
        self.label  = ""
        self.sort = True
        self.actions = []
        self.idString = ""

    def __repr__(self) -> str:
        return _dump_dict(self)
        
class ActionsForNautilusConfig():

    def __init__(self):
        self.reset_config()
        self.update_config()
        GLib.timeout_add_seconds(30, _check_config_change, self)
#        threading.Thread(target=_watch_config_change, args=(self,), daemon=True).start()
        if debug:
            print("Initialized")

    def get_mtime(self):
        return self.mtime

    def update_config(self):
        my_actions = []

        try:
            if os.path.exists(_config_path):
                self.mtime = os.path.getmtime(_config_path)
                with open(_config_path) as json_file:
                    file_config = json.load(json_file)
                    global debug
                    debug = file_config.get("debug", False)
                    self.sort = file_config.get("sort", "manual") == "auto"
                    json_actions = file_config.get("actions", [])
                    if type(json_actions) == list:
                        my_actions = list(filter(None, map(lambda action: _check_action(str(action[0]), action[1]), enumerate(json_actions))))    
                    else:
                        my_actions = []
                    self.actions = my_actions
            else:
                print("Config file " + _config_path + " does not exist")
        except Exception as e:
            print("Config file " + _config_path + " load failed", e)
    
        if debug:
            print(_dump_dict(self))

    def reset_config(self):
        self.actions = []
        self.sort = False
        self.mtime = None
###
### fix non-JSON-able objects
###
def _fix_json(value):
    return "not-serializable"

###
### Private functions and values
###
def _check_config_change(config_object):
    last_mtime = config_object.get_mtime()
    this_mtime = os.path.getmtime(_config_path) if os.path.exists(_config_path) else None
    if last_mtime is not None and (last_mtime is None or last_mtime != this_mtime):
        print("WATCHER THREAD: updating config")
        config_object.update_config()
    elif this_mtime is None and last_mtime is not None:
        print("WATCHER THREAD: resetting config")
        config_object.reset_config()
    else:
        debug_print("WATCHER THREAD: config not changed")
    return True

#
# Wraps the config checker in a poll loop intended for Thread execution
#
# NOT USED - GLib timers work better
#
def _watch_config_change(config_object):
    print("WATCHER THREAD: starting watch loop")
    while True:
        sleep_time = int(time.time())
        _check_config_change(config_object)
        print("WATCHER THREAD: sleeping at", sleep_time)
        time.sleep(30)
        print("WATCHER THREAD: slept time", int(time.time()) - sleep_time)

#
# Update the config from the config file
#
#
# Triage the action based on type
#
def _check_action(idString, json_action):
    config_type = json_action.get("type")
    if config_type == "menu":
        return _check_menu_action(idString, json_action)
    elif config_type == "command":
        return _check_command_action(idString, json_action)

    print("Ignoring action: missing/invalid type property", json_action)

#
# Normalize a menu action
#
def _check_menu_action(idString, json_action):
    if json_action.get("disabled", False):
        debug_print("Ignoring menu action: disabled; {json_action}")
        return
    action = MenuAction()
    action.label = json_action["label"].strip() if type(json_action.get("label","")) == str else ""
    action.sort = json_action.get("sort", "manual") == "auto"
    if (len(action.label) > 0 and
    "actions" in json_action and 
    type(json_action["actions"]) == list):
        action.actions = list(filter(None, map(lambda sub_action: _check_action(idString + "_" + str(sub_action[0]), sub_action[1]), enumerate(json_action["actions"]))))
        action.idString = idString
        if len(action.actions) > 0:
            return action

        print("Ignoring action menu: no valid sub actions", json_action)
        return None

    print("Ignoring menu action: missing properties", json_action)

#
# Normalize a command action
#
def _check_command_action(idString, json_action):
    if "disabled" in json_action and json_action["disabled"]:
        debug_print(f"Ignoring command action: disabled; {json_action}")
        return
    action = CommandAction()
    action.label = json_action["label"].strip() if "label" in json_action and type(json_action["label"]) == str else ""
    action.command_line = json_action["command_line"].strip() if "command_line" in json_action and type(json_action["command_line"]) == str else ""
    if (len(action.label) > 0 and
    len(action.command_line) > 0):

        if type(json_action.get("mimetypes")) == list:
            action.all_mimetypes = ( "*/*" in json_action["mimetypes"] or "*" in json_action["mimetypes"])
            if not action.all_mimetypes:
                action.mimetypes = _split_rules(_remove_duplicates_by_key(list(filter(None, map(_gen_mimetype, json_action["mimetypes"]))),"mimetype"))
                action.all_mimetypes = len(action.mimetypes["n_rules"]) + len(action.mimetypes["p_rules"]) < 1

        if type(json_action.get("filetypes")) == list:
            action.filetypes = _split_rules(_remove_duplicates_by_key(_flatten_list(list(filter(None, map(_gen_filetype, json_action["filetypes"])))),"filetype"))
            action.all_filetypes = len(action.filetypes["n_rules"]) + len(action.filetypes["p_rules"]) < 1

        if type(json_action.get("path_patterns")) == list:
            action.path_patterns = _split_rules(_remove_duplicates_by_key(_flatten_list(list(filter(None, map(_gen_pattern, json_action["path_patterns"])))),"path_pattern"))
            action.all_path_patterns = len(action.path_patterns["n_rules"]) + len(action.path_patterns["p_rules"]) < 1

        if type(json_action.get("permissions")) == str:
            perm = json_action["permissions"].strip()
            action.permissions = _permissions[perm] if perm in _permissions else ""
 
        if type(json_action.get("show_if_true")) == str:
            action.show_if_true = json_action["show_if_true"].strip()
 
        action.cwd = None if type(json_action.get("cwd")) != str or len(json_action["cwd"].strip()) == 0 else json_action["cwd"].strip()
 
        if type(json_action.get("use_shell")) == bool:
            action.use_shell = json_action["use_shell"]
 
        action.idString = idString
        action.cmd_behaviour = afn_place_holders.get_behavior(action.command_line)

        #
        # Checking max_items and min_items
        #
        #    * max_items = 0 means unlimited, otherwise it must be greater than 0 - forced to 0 otherwise 
        #    * min_items must be greater than 0 - forced to 1 otherwise
        #    * min_items must be less than or equal to max_items if max_items is greater than 1 - force to equal if otherwise
        #
        if type(json_action.get("max_items", None)) == int and json_action["max_items"] > 0:
            action.max_items = json_action["max_items"]

        if type(json_action.get("min_items", None)) == int and json_action["min_items"] > 1:
            action.min_items = json_action["min_items"]

        if action.max_items == 0 or (action.min_items <= action.max_items):
            pass
        else:
            action.min_items = action.max_items

        return action

    print("Ignoring command action: missing properties", json_action)

#
# Generates an object that facilitates fast mimetype checks
#
def _gen_mimetype(mimetype):
    if type(mimetype) == str and len(mimetype := mimetype.lower().strip()) > 3 and mimetype.find("/") > 0:
        comparison = not mimetype.startswith("!")
        if not comparison:
            mimetype = mimetype[1:]
        return {"comparator": "startswith", "mimetype": mimetype[:len(mimetype)-1], "comparison": comparison} if mimetype.endswith("/*") else {"comparator":"__eq__", "mimetype":mimetype, "comparison": comparison}

    print("Ignoring mimetype: invalid format", mimetype)

def _gen_filetype(filetype):
    if type(filetype) == str and len(filetype := filetype.lower().strip()) > 3:
        comparison = not filetype.startswith("!")
        if not comparison:
            filetype = filetype[1:]
        return list(map(lambda gio_filetype: {"filetype": gio_filetype, "comparison": comparison}, _filetypes.get(filetype, [])))

    print("Ignoring filetype: unrecognized", filetype)

def _gen_pattern(pattern):
    if type(pattern) == str and len(pattern := pattern.strip()) > 0:
        comparison = not pattern.startswith("!")
        if not comparison:
            pattern = pattern[1:]
        re = (pattern.startswith("re:"))
        patternRE = _gen_pattern_re_from_re(pattern, comparison) if re else _gen_pattern_re_from_glob(pattern, comparison)
        if patternRE is not None:
            return {"re": patternRE, "comparator": "search" if re else "fullmatch", "path_pattern": pattern, "comparison": comparison}

    print("Ignoring pattern: unrecognized", pattern)

def _gen_pattern_re_from_re(pattern, comparison):
    try:
        return re.compile(pattern[3:])
    except Exception as e:
        print("Failed regular expression compilation", e)

def _gen_pattern_re_from_glob(pattern, comparison):
    try:
        return re.compile(fnmatch.translate(pattern))
    except Exception as e:
        print("Failed glob compilation", e)


def _flatten_list(lst):
    lst1 = []
    for i in lst:
        lst1.append(i) if type(i) is not list else lst1.extend(_flatten_list(i))
    return lst1

def _remove_duplicates_by_key(lst,key):
    memo = set()
    return list(filter(None,map(lambda element: None if element[key] in memo else _add_to_set(memo, element, key), lst)))
 
def _add_to_set(set, element, key):
    set.add(element[key])
    return element

def _split_rules(lst):
    rc = {
        "p_rules": list(filter(lambda element: element["comparison"], lst)),
        "n_rules": list(filter(lambda element: not element["comparison"], lst))
    }
    if debug:
        print(rc)
    return rc
