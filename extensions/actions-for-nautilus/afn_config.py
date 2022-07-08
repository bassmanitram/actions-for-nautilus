#
# Config management
#
import os, json
import afn_place_holders
from gi.repository import Gio

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

###
### Exported functions
###
def get():
    return _config

def initialize():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path) as json_file:
            _config.update(json.load(json_file))
            config_items = _config.get("items", [])

    except Exception as e:
        print("Config file " + config_path + " load failed", e)
        _config["items"] = []
    
    if type(config_items) == list:
        _config["items"] = list(filter(None, map(lambda item: _check_item(str(item[0]), item[1]), enumerate(config_items))))    
    else:
        _config["items"] = []

    print(json.dumps(_config))

###
### Private functions and values
###

#
# The config dict
#
_config = {
    "items": {}
}

#
# Triage the config item based on type
#
def _check_item(idString, config_item):
    config_type = config_item.get("type")
    if config_type == "menu":
        return _check_menu_item(idString, config_item)
    elif config_type == "item":
        return _check_item_item(idString, config_item)

    print("Ignoring config item: missing/invalid type property", config_item)

#
# Normalize a menu item
#
def _check_menu_item(idString, config_item):
    config_item["label"] = config_item["label"].strip() if "label" in config_item and type(config_item["label"]) == str else ""
    if (len(config_item["label"]) > 0 and
        "items" in config_item and 
        type(config_item["items"]) == list):
        config_item["items"] = list(filter(None, map(lambda item: _check_item(idString + "_" + str(item[0]), item[1]), enumerate(config_item["items"]))))
        config_item["idString"] = idString
        if len(config_item["items"]) > 0:
            return config_item

        print("Ignoring config item menu: no valid sub items", config_item)
        return None

    print("Ignoring config item menu: missing properties", config_item)

#
# Normalize a leaf item
#
def _check_item_item(idString, config_item):
    config_item["label"] = config_item["label"].strip() if "label" in config_item and type(config_item["label"]) == str else ""
    config_item["command_line"] = config_item["command_line"].strip() if "command_line" in config_item and type(config_item["command_line"]) == str else ""
    if (len(config_item["label"]) > 0 and
        len(config_item["command_line"]) > 0):

        if "mimetypes" in config_item and type(config_item["mimetypes"]) == list:
            config_item["all_mimetypes"] = ( "*/*" in config_item["mimetypes"] or "*" in config_item["mimetypes"])
            if not config_item["all_mimetypes"]:
                config_item["mimetypes"] = _remove_duplicates_by_key(list(filter(None, map(_gen_mimetype, config_item["mimetypes"]))),"mimetype")
                config_item["all_mimetypes"] = len(config_item["mimetypes"]) < 1
        else:
            config_item["all_mimetypes"] = True

        if "filetypes" in config_item and type(config_item["filetypes"]) == list:
            config_item["filetypes"] = _remove_duplicates_by_key(_flatten_list(list(filter(None, map(_gen_filetype, config_item["filetypes"])))),"filetype")
            config_item["all_filetypes"] = len(config_item["filetypes"]) < 1
        else:
            config_item["all_filetypes"] = True

        config_item["idString"] = idString
        config_item["cmd_behavior"] = afn_place_holders.get_behavior(config_item["command_line"])

        return config_item

    print("Ignoring config item item: missing properties", config_item)

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

def _flatten_list(lst):
    lst1 = []
    for i in lst:
        lst1.append(i) if type(i) is not list else lst1.extend(_flatten_list(i))
    return lst1

def _remove_duplicates_by_key(lst,key):
    memo = set()
    return list(filter(None,map(lambda item: None if item[key] in memo else _add_to_set(memo, item, key), lst)))
 
def _add_to_set(set, item, key):
    set.add(item[key])
    return item

###
### Initialize on load
###
initialize()
