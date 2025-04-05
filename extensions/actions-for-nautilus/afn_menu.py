#
# Create context menu items
#
import os, afn_config
import subprocess
from urllib.parse import urlparse
from gi.repository import Nautilus, Gio

#
# Consolidate background and selection calls to create menus
#
# files is a list of __gi__.NautilusVFSFile instances
#
def create_menu_items(config, files, group, act_function):
#	if (len(files) > 0):
#		print(files[0].__class__)
#		print(files[0].__class__.__name__)
#		for base in files[0].__class__.__bases__:
#			print(base.__name__, base)
#		print(dir(files[0]))
	try:
		my_files = list(filter(None, map(lambda file: {
				"mimetype": file.get_mime_type(),
				"filetype": file.get_file_type(),
				"basename": os.path.basename(file.get_location().get_path()),
				"filepath": file.get_location().get_path(),
				"folder": os.path.dirname(file.get_location().get_path()),
				"uri": urlparse(file.get_uri())
			} if file.get_location().get_path() is not None else None, files)))
		actions = list(filter(None, map(lambda action: _create_menu_item(action, my_files, group, act_function), config["actions"])))
		return sorted(actions, key=lambda element: element.props.label) if config.get("sort","manual") == "auto" else actions
	except Exception as e:
		print("Error constructing file descriptors")
		print(group)
		print(files)
		print(e)
		return []

#
# Triage the menu item creation based on type
#
def _create_menu_item(action, files, group, act_function):
	if len(files) > 0:
		if action["type"] == "menu":
			return _create_submenu_menu_item(action, files, group, act_function)
		else:
			return _create_command_menu_item(action, files, group, act_function)
	else:
		return []

#
# Generate an item that has a submenu attached, with its own actions recursively added
#
def _create_submenu_menu_item(action, files, group, act_function):
	actions = list(filter(None, map(lambda action: _create_menu_item(action, files, group, act_function), action["actions"])))

	if len(actions) > 0:
		menu = Nautilus.Menu()
		menu_item = Nautilus.MenuItem(
			name="Actions4Nautilus::Menu" + action["idString"] + group,
			label=action["label"],
		)
		menu_item.set_submenu(menu)
		for menu_sub_item in (sorted(actions,key=lambda element: element.props.label) if action["sort"] else actions):
			menu.append_item(menu_sub_item)
		return menu_item

def _is_command_true(cmd):
	try:
		afn_config.debug_print(f"Running show_if_true command <{cmd}>")
		process = subprocess.run(
			cmd,
			shell=True,
			capture_output=True,
			text=True
		)
		if process.stdout.rstrip() == "true":
			return True
		afn_config.debug_print(f"show_if_true_command {cmd} returned non-'true': stdout={process.stdout}, stderr={process.stderr}")
		
	except Exception as e:
		print(f"show_if_true_command {cmd} failed: {e}")
	
	return False
#
# Generate a command item that is connected to the activate signal
#
def _create_command_menu_item(action, files, group, activate_function):
	if action["max_items"] > 0 and action["max_items"] < len(files):
		return None

	if action["min_items"] > len(files):
		return None

	if not ((action["permissions"] == "" or _applicable_to_permissions(action, files)) and
	    (action["all_mimetypes"] or _applicable_to_mimetype(action, files)) and
	    (action["all_filetypes"] or _applicable_to_filetype(action, files)) and
	    (action["all_path_patterns"] or _applicable_to_path_patterns(action, files))):
		return None
	
	if len(action["show_if_true"]) > 0:
		cmd = action["show_if_true"]
		if '%F' in cmd:
			cmd = cmd.replace('%F', ' '.join(f"'{f['filepath']}'" for f in files)) 
		if '%f' in cmd:
			for file in files:
				if not _is_command_true(cmd.replace('%f', file["filepath"])):
					return None
		else:
			if not _is_command_true(cmd):
				return None

	name = "Actions4Nautilus::Item" + action["idString"] + group
	label = action["label"]
	afn_config.debug_print(f"Attaching menu item: file={files[0]} name={name}, label={label}")
	menu_item = Nautilus.MenuItem(name=name, label=label)
	menu_item.connect("activate", activate_function, action, files)
	return menu_item

###
### In the following, the relevant attributes of the selected files
### are compared to the "p_rules" (positive rules) and "n_rules"(negative rules) of
### each class of attribute. At least one p_rules must match while no n_rules must 
### match, for all files in the selection
###

#
# Compares each file mimetype to the action mimetypes
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_mimetype(action, files):
	return all(map(lambda file: (
		(len(action["mimetypes"]["p_rules"]) == 0 or any(getattr(file["mimetype"],p_rule["comparator"])(p_rule["mimetype"]) for p_rule in action["mimetypes"]["p_rules"])) and
		not any(getattr(file["mimetype"],n_rule["comparator"])(n_rule["mimetype"]) for n_rule in action["mimetypes"]["n_rules"])), files))

#
# Compares each file type to the action filetypes
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_filetype(action, files):
	return all(map(lambda file: (
		(len(action["filetypes"]["p_rules"]) == 0 or any((file["filetype"] == p_rule["filetype"]) for p_rule in action["filetypes"]["p_rules"])) and
		not any((file["filetype"] == n_rule["filetype"]) for n_rule in action["filetypes"]["n_rules"])), files))


#
# Compares each file path to the action path_patterns
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_path_patterns(action, files):
	return all(map(lambda file: (
		(len(action["path_patterns"]["p_rules"]) == 0 or any((getattr(p_rule["re"],p_rule["comparator"])(file["filepath"]) is not None) for p_rule in action["path_patterns"]["p_rules"])) and
		(len(action["path_patterns"]["n_rules"]) == 0 or all((getattr(n_rule["re"],n_rule["comparator"])(file["filepath"]) is None) for n_rule in action["path_patterns"]["n_rules"]))), files))

#
# Ensures that the user has at least the stated permissions to access each file
# Returns True if OK for every one, otherwise False
#
def _applicable_to_permissions(action, files):
	return all(map(lambda file: os.access(file["filepath"], action["permissions"]), files))
