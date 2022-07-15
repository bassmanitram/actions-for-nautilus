#
# Config management
#
import os, json, threading, time
import afn_place_holders
from gi.repository import Gio, GLib

HOME = os.environ.get('HOME')
_config_path = HOME + "/.local/share/actions-for-nautilus/config.json"

_default_config = {
    "actions": []
}

#
# The config dict
#
_config = _default_config

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

class ActionsForNautilusConfig():

    def __init__(self):
        self.reset_config()
        self.update_config()
        GLib.timeout_add_seconds(30, _check_config_change, self)
#        threading.Thread(target=_watch_config_change, args=(self,), daemon=True).start()
        print("Initialized")

    def get_config(self):
        return self.__config

    def get_mtime(self):
        return self.__mtime

    def update_config(self):
        my_config = {
            "actions": []
        }

        try:
            if os.path.exists(_config_path):
                self.__mtime = os.path.getmtime(_config_path)
                with open(_config_path) as json_file:
                    my_config.update(json.load(json_file))
                    actions = my_config.get("actions", [])
                    if type(actions) == list:
                        my_config["actions"] = list(filter(None, map(lambda action: _check_action(str(action[0]), action[1]), enumerate(actions))))    
                    else:
                        my_config["actions"] = []
                    self.__config = my_config
            else:
                print("Config file " + _config_path + " does not exist")
        except Exception as e:
            print("Config file " + _config_path + " load failed", e)
    
        print(json.dumps(self.__config))


    def reset_config(self):
        self.__config = {
            "actions": []
        }
        self.__mtime = None

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
#    else:
#        print("WATCHER THREAD: config not changed")
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
