import os
import subprocess
import json
from gi.repository import Nautilus, GObject, Gtk, Gdk
from gi import require_version

require_version('Gtk', '3.0')
require_version('Nautilus', '3.0')

###
### The MenuProvider implementation
###
class Actions4Nautilus(Nautilus.MenuProvider, GObject.GObject):

    def __init__(self):
        self.config = {
            "items": {}
        }

        self.place_holders = {
            "%b": "name", 
            "%d": "folder", 
            "%m": "mimetype", 
            "%u": "uri", 
        }

        with open(os.path.join(os.path.dirname(__file__), "config.json")) as json_file:
            try:
                self.config.update(json.load(json_file))
            except:
                pass
        #
        # Optimize and normalize some aspects of the config
        #
        if "items" in self.config and type(self.config["items"]) == list:
            self.config["items"] = list(filter(None, map(lambda item: self.__check_item(str(item[0]), item[1]), enumerate(self.config["items"]))))
            
        else:
            self.config["items"] = []

        print(self.config)

#
# Menu provider interface implementation
#
    def get_file_items(self, window, files):
        return self.__create_menu_items(files, "File")

    def get_background_items(self, window, file):
        return self.__create_menu_items([file], "Background")

#
# Command execution
#
    def run_command(self, menu, config_item, files):
        cwd = self.__expand_token(config_item["cwd"], files[0]) if "cwd" in config_item else None
        use_shell = bool(config_item["use_shell"]) if "use_shell" in config_item else False

        final_command_line = []
        for token in config_item["command_line"]:
            mod_token = token.replace("%%", "PERCENTPERCENT")
            if self.__token_needs_expanding(token):
                for idx in range(len(files)):
                    final_command_line.append(self.__expand_token(mod_token, files[idx]).replace("PERCENTPERCENT", "%"))
            else: 
                final_command_line.append(mod_token.replace("PERCENTPERCENT", "%"))

        if use_shell:
            final_command_line = " ".join(f'"{w}"' for w in map(lambda x: x.replace('"','\\"'), final_command_line))

        print(cwd)
        print(final_command_line)
        print(config_item)
        print(files)
        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
###
### P R I V A T E   M E T H O D S
###
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

###
### Config optimization
###

    #
    # Triage the config item based on type
    #
    def __check_item(self, idString, config_item):
        if "type" in config_item:
            if config_item["type"] == "menu":
                return self.__check_menu_item(idString, config_item)
            elif config_item["type"] == "item":
                return self.__check_item_item(idString, config_item)

        print("Ignoring config item: no type property", config_item)

    #
    # Normalize a menu item
    #
    def __check_menu_item(self, idString, config_item):
        config_item["label"] = config_item["label"].strip() if "label" in config_item else ""
        if (len(config_item["label"]) > 0 and
            "items" in config_item and 
            type(config_item["items"]) == list):
            config_item["items"] = list(filter(None, map(lambda item: self.__check_item(idString + "_" + str(item[0]), item[1]), enumerate(config_item["items"]))))
            config_item["idString"] = idString
            if len(config_item["items"]) > 0:
                return config_item

            print("Ignoring config item menu: no valid sub items", config_item)
            return None

        print("Ignoring config item menu: missing properties", config_item)

    #
    # Normalize a leaf item
    #
    def __check_item_item(self, idString, config_item):
        config_item["label"] = config_item["label"].strip() if "label" in config_item else ""
        if (len(config_item["label"]) > 0 and
            "command_line" in config_item and
            type(config_item["command_line"]) == list and
            len(config_item["command_line"]) > 0):
            if "mimetypes" in config_item and type(config_item["mimetypes"]) == list:
                config_item["all_mimetypes"] = ( "*/*" in config_item["mimetypes"] or "*" in config_item["mimetypes"])
                if not config_item["all_mimetypes"]:
                    config_item["mimetypes"] = list(filter(None, map(self.__gen_mimetype, config_item["mimetypes"])))
                    config_item["all_mimetypes"] = len(config_item["mimetypes"]) < 1
            else:
                config_item["all_mimetypes"] = True
            config_item["idString"] = idString
            return config_item

        print("Ignoring config item item: missing properties", config_item)

    #
    # Generates an object that facilitates fast mimetype checks
    #
    def __gen_mimetype(self, mimetype):
        if type(mimetype) == str and len(mimetype := mimetype.lower().strip()) > 3 and mimetype.find("/") > 0:
            return {"comparator": "startswith", "mimetype": mimetype[:len(mimetype)-1]} if mimetype.endswith("/*") else {"comparator":"__eq__", "mimetype":mimetype}

        print("Ignoring mimetype: invalid format", mimetype)

###
### Menu generation
###
    #
    # Consolidate background and selection calls to create menus
    #
    def __create_menu_items(self, files, group):
        my_files = list(map(lambda file: {
                "mimetype": file.get_mime_type(),
                "name": os.path.basename(file.get_location().get_path()),
                "folder": os.path.dirname(file.get_location().get_path()),
                "uri": file.get_uri()
            }, files))

        return sorted(list(filter(None, map(lambda item: self.__create_menu_item(item, my_files, group), self.config["items"]))), key=lambda element: element.props.label)
        
    #
    # Triage the menu item creation config item based on type
    #
    def __create_menu_item(self, config_item, files, group):
        if config_item["type"] == "menu":
            return self.__create_menu_menu_item(config_item, files, group)
        else:
            return self.__create_item_menu_item(config_item, files, group)
    
    #
    # Generate an item that has a submenu attached, with its own items
    # recursively added
    #
    def __create_menu_menu_item(self, config_item, files, group):
        sub_items = list(filter(None, map(lambda item: self.__create_menu_item(item, files, group), config_item["items"])))

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
    def __create_item_menu_item(self, config_item, files, group):
        if ("max_items" in config_item and 
            isinstance(config_item["max_items"], int) and 
            config_item["max_items"] < len(files)):
                return None

        if config_item["all_mimetypes"] or self.__applicable_to_mime(config_item, files):
            menu_item = Nautilus.MenuItem(
                name="NautilusCopyPath::Item" + config_item["idString"] + group,
                label=config_item["label"],
            )
            menu_item.connect("activate", self.run_command, config_item, files)
            return menu_item

###
### Utilities
###

    #
    # Compares each file mimetype to the config item mimetypes
    # Returns True if a match is found for every one, otherwise False
    #
    def __applicable_to_mime(self, config_item, files):
        return all(map(lambda file: any(getattr(file["mimetype"],cmimetype["comparator"])(cmimetype["mimetype"]) for cmimetype in config_item["mimetypes"]), files))

    #
    # Examines a token for %-prefixed place holders
    #
    def __token_needs_expanding(self, token):
        return any(token.find(pattern) != -1 for pattern in self.place_holders.keys())

    #
    # Replaces %-prefixed place holders with appropriate values
    #
    def __expand_token(self, token, file_detail):
        return_token = token
        for pattern in self.place_holders.keys():
            return_token = return_token.replace(pattern,file_detail[self.place_holders[pattern]])
        return return_token

###
### Pattern replacement functions
###
    def __expand_percent_b(self, token, files):
        return files[0]["name"]

    def __expand_percent_B(self, token, files):
        return files[0]["name"]

    def __expand_percent_c(self, token, files):
        return len(files)

    def __expand_percent_d(self, token, files):
        return files[0]["folder"]

    def __expand_percent_D(self, token, files):
        return files[0]["name"]

    def __expand_percent_f(self, token, files):
        return files[0]["name"]

    def __expand_percent_F(self, token, files):
        return files[0]["name"]

    def __expand_percent_h(self, token, files):
        return files[0]["name"]

    def __expand_percent_m(self, token, files):
        return files[0]["name"]

    def __expand_percent_M(self, token, files):
        return files[0]["name"]

    def __expand_percent_n(self, token, files):
        return files[0]["name"]

    def __expand_percent_p(self, token, files):
        return files[0]["name"]

    def __expand_percent_s(self, token, files):
        return files[0]["name"]

    def __expand_percent_u(self, token, files):
        return files[0]["name"]

    def __expand_percent_w(self, token, files):
        return files[0]["name"]

    def __expand_percent_W(self, token, files):
        return files[0]["name"]

    def __expand_percent_x(self, token, files):
        return files[0]["name"]

    def __expand_percent_X(self, token, files):
        return files[0]["name"]
    
