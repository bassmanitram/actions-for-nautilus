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
            actions = _config.get("actions", [])

    except Exception as e:
        print("Config file " + config_path + " load failed", e)
        _config["actions"] = []
    
    if type(actions) == list:
        _config["actions"] = list(filter(None, map(lambda action: _check_action(str(action[0]), action[1]), enumerate(actions))))    
    else:
        _config["actions"] = []

    print(json.dumps(_config))

###
### Private functions and values
###

#
# The config dict
#
_config = {
    "actions": {}
}

#
# Triage the action based on type
#
def _check_action(idString, action):
    config_type = action.get("type")
    if config_type == "menu":
        return _check_menu_action(idString, action)
    elif config_type == "command":
        return _check_command_action(idString, action)

    print("Ignoring action: missing/invalid type property", action)

#
# Normalize a menu action
#
def _check_menu_action(idString, action):
    action["label"] = action["label"].strip() if "label" in action and type(action["label"]) == str else ""
    if (len(action["label"]) > 0 and
        "actions" in action and 
        type(action["actions"]) == list):
        action["actions"] = list(filter(None, map(lambda sub_action: _check_action(idString + "_" + str(sub_action[0]), sub_action[1]), enumerate(action["actions"]))))
        action["idString"] = idString
        if len(action["actions"]) > 0:
            return action

        print("Ignoring action menu: no valid sub actions", action)
        return None

    print("Ignoring menu action: missing properties", action)

#
# Normalize a command action
#
def _check_command_action(idString, action):
    action["label"] = action["label"].strip() if "label" in action and type(action["label"]) == str else ""
    action["command_line"] = action["command_line"].strip() if "command_line" in action and type(action["command_line"]) == str else ""
    if (len(action["label"]) > 0 and
        len(action["command_line"]) > 0):

        if "mimetypes" in action and type(action["mimetypes"]) == list:
            action["all_mimetypes"] = ( "*/*" in action["mimetypes"] or "*" in action["mimetypes"])
            if not action["all_mimetypes"]:
                action["mimetypes"] = _remove_duplicates_by_key(list(filter(None, map(_gen_mimetype, action["mimetypes"]))),"mimetype")
                action["all_mimetypes"] = len(action["mimetypes"]) < 1
        else:
            action["all_mimetypes"] = True

        if "filetypes" in action and type(action["filetypes"]) == list:
            action["filetypes"] = _remove_duplicates_by_key(_flatten_list(list(filter(None, map(_gen_filetype, action["filetypes"])))),"filetype")
            action["all_filetypes"] = len(action["filetypes"]) < 1
        else:
            action["all_filetypes"] = True

        action["idString"] = idString
        action["cmd_behavior"] = afn_place_holders.get_behavior(action["command_line"])

        return action

    print("Ignoring command action: missing properties", action)

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
    return list(filter(None,map(lambda element: None if element[key] in memo else _add_to_set(memo, element, key), lst)))
 
def _add_to_set(set, element, key):
    set.add(element[key])
    return element

###
### Initialize on load
###
initialize()
