#
# Create context menu items
#
import os
from urllib.parse import urlparse
from gi.repository import Nautilus

#
# Consolidate background and selection calls to create menus
#
def create_menu_items(config, files, group, act_function):
	my_files = list(map(lambda file: {
			"mimetype": file.get_mime_type(),
			"basename": os.path.basename(file.get_location().get_path()),
			"filename": file.get_location().get_path(),
			"folder": os.path.dirname(file.get_location().get_path()),
			"uri": urlparse(file.get_uri())
		}, files))

	return sorted(list(filter(None, map(lambda item: _create_menu_item(item, my_files, group, act_function), config["items"]))), key=lambda element: element.props.label)
	
#
# Triage the menu item creation config item based on type
#
def _create_menu_item(config_item, files, group, act_function):
	if config_item["type"] == "menu":
		return _create_menu_menu_item(config_item, files, group, act_function)
	else:
		return _create_item_menu_item(config_item, files, group, act_function)

#
# Generate an item that has a submenu attached, with its own items
# recursively added
#
def _create_menu_menu_item(config_item, files, group, act_function):
	sub_items = list(filter(None, map(lambda item: _create_menu_item(item, files, group, act_function), config_item["items"])))

	if len(sub_items) > 0:
		menu = Nautilus.Menu()
		menu_item = Nautilus.MenuItem(
			name="Actions4Nautilus::Menu" + config_item["idString"] + group,
			label=config_item["label"],
		)
		menu_item.set_submenu(menu)
		for menu_sub_item in sorted(sub_items,key=lambda element: element.props.label):
			menu.append_item(menu_sub_item)
		return menu_item

#
# Generate a leaf item that is connected to the activate signal
#
def _create_item_menu_item(config_item, files, group, act_function):
	if ("max_items" in config_item and 
		isinstance(config_item["max_items"], int) and 
		config_item["max_items"] < len(files)):
			return None

	if config_item["all_mimetypes"] or _applicable_to_mime(config_item, files):
		menu_item = Nautilus.MenuItem(
			name="NautilusCopyPath::Item" + config_item["idString"] + group,
			label=config_item["label"],
		)
		menu_item.connect("activate", act_function, config_item, files)
		return menu_item

#
# Compares each file mimetype to the config item mimetypes
# Returns True if a match is found for every one, otherwise False
#
def _applicable_to_mime(config_item, files):
	return all(map(lambda file: any(getattr(file["mimetype"],mimetype["comparator"])(mimetype["mimetype"]) for mimetype in config_item["mimetypes"]), files))
