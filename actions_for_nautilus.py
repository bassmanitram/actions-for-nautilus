import os, subprocess, json, re, shlex
from urllib.parse import urlparse
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
            "b": self.__expand_percent_b, 
            "B": self.__expand_percent_B, 
            "c": self.__expand_percent_c, 
            "d": self.__expand_percent_d, 
            "D": self.__expand_percent_D, 
            "f": self.__expand_percent_f, 
            "F": self.__expand_percent_F, 
            "h": self.__expand_percent_h, 
            "m": self.__expand_percent_m, 
            "M": self.__expand_percent_M, 
            "n": self.__expand_percent_n, 
            "o": self.__expand_percent_o, 
            "O": self.__expand_percent_O, 
            "p": self.__expand_percent_p, 
            "s": self.__expand_percent_s, 
            "u": self.__expand_percent_u, 
            "U": self.__expand_percent_U, 
            "w": self.__expand_percent_w, 
            "W": self.__expand_percent_W,
            "x": self.__expand_percent_x, 
            "X": self.__expand_percent_X,
            "%": self.__expand_percent_percent
        }

        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path) as json_file:
            try:
                self.config.update(json.load(json_file))
            except:
                print("Config file " + config_path + " not found")

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
        cwd = self.__resolve_place_holders(config_item["cwd"], 0, [files[0]], False) if "cwd" in config_item else None
        use_shell = bool(config_item["use_shell"]) if "use_shell" in config_item else False

        final_command_line = self.__resolve_place_holders(config_item["command_line"], 0, files, True)

        if not use_shell:
            #
            # Split into args and lose any shell escapes
            #
            final_command_line = list(map(lambda arg: arg.replace("\\\\","!§ESCBACKSLASH§µ").replace("\\", "").replace("!§ESCBACKSLASH§µ","\\"),shlex.split(final_command_line)))

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
        config_item["label"] = config_item["label"].strip() if "label" in config_item and type(config_item["label"]) == str else ""
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
        config_item["label"] = config_item["label"].strip() if "label" in config_item and type(config_item["label"]) == str else ""
        config_item["command_line"] = config_item["command_line"].strip() if "command_line" in config_item and type(config_item["command_line"]) == str else ""
        if (len(config_item["label"]) > 0 and
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
                "basename": os.path.basename(file.get_location().get_path()),
                "filename": file.get_location().get_path(),
                "folder": os.path.dirname(file.get_location().get_path()),
                "uri": urlparse(file.get_uri())
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
### Place holder replacement functions
###
    def __resolve_place_holders(self, string, file_index, files, escape):
        next_index = 0
        place_holder_list = "".join(self.place_holders.keys())
        while True:
            match = re.search( "%["+place_holder_list+"]", string[next_index:])
            if match is None:
                break
            span = match.span()
            start_index = next_index+span[0]
            end_index = next_index+span[1]
            replacement = self.place_holders[match.group()[1:]](file_index, files, escape)
            string = string[:start_index] + replacement + string[end_index:]
            next_index = (start_index + len(replacement))
        return string

    def __expand_percent_percent(self, index, files, escape):
        return "%"

    def __expand_percent_b(self, index, files, escape):
        return files[index]["basename"].replace(" ","\\ ")  if escape else files[index]["basename"]

    def __expand_percent_B(self, index, files, escape):
        return " ".join(map(lambda file: file["basename"].replace(" ","\\ ") if escape else file["basename"], files))

    def __expand_percent_c(self, index, files, escape):
        return str(len(files))

    def __expand_percent_d(self, index, files, escape):
        return files[index]["folder"].replace(" ","\\ ") if escape else files[index]["folder"]

    def __expand_percent_D(self, index, files, escape):
        return " ".join(map(lambda file: file["folder"].replace(" ","\\ ") if escape else file["folder"], files))

    def __expand_percent_f(self, index, files, escape):
        return files[0]["filename"].replace(" ","\\ ") if escape else files[0]["filename"]

    def __expand_percent_F(self, index, files, escape):
        return " ".join(map(lambda file: file["filename"].replace(" ","\\ ") if escape else file["filename"], files))

    def __expand_percent_h(self, index, files, escape):
        h = files[index]["uri"].hostname
        return "" if h is None else h.replace(" ","\\ ") if escape else h

    def __expand_percent_m(self, index, files, escape):
        return files[index]["mimetype"].replace(" ","\\ ") if escape else files[index]["mimetype"]

    def __expand_percent_M(self, index, files, escape):
        return " ".join(map(lambda file: file["mimetype"].replace(" ","\\ ") if escape else file["mimetype"], files))

    def __expand_percent_n(self, index, files, escape):
        n = files[index]["uri"].username
        return "" if n is None else n.replace(" ","\\ ") if escape else n

    def __expand_percent_o(self, index, files, escape):
        return ""

    def __expand_percent_O(self, index, files, escape):
        return ""

    def __expand_percent_p(self, index, files, escape):
        p = files[index]["uri"].port
        return "" if p is None else p

    def __expand_percent_s(self, index, files, escape):
        return files[index]["uri"].scheme

    def __expand_percent_u(self, index, files, escape):
        return files[index]["uri"].geturl().replace(" ","\\ ") if escape else files[index]["uri"].geturl()

    def __expand_percent_U(self, index, files, escape):
        return " ".join(map(lambda file: file["uri"].geturl().replace(" ","\\ ") if escape else file["uri"].geturl(), files))

    def __expand_percent_w(self, index, files, escape):
        return self.__name_extension(files[index]["basename"])["name"].replace(" ","\\ ") if escape else self.__name_extension(files[index]["basename"])["name"]
 
    def __expand_percent_W(self, index, files, escape):
        return " ".join(map(lambda file: self.__name_extension(file["basename"])["name"].replace(" ","\\ ") if escape else self.__name_extension(file["basename"])["name"], files))

    def __expand_percent_x(self, index, files, escape):
        return self.__name_extension(files[index]["basename"])["extension"].replace(" ","\\ ") if escape else self.__name_extension(files[index]["basename"])["extension"]

    def __expand_percent_X(self, index, files, escape):
        return " ".join(map(lambda file: self.__name_extension(file["basename"])["extension"].replace(" ","\\ ") if escape else self.__name_extension(file["basename"])["extension"], files))

    def __name_extension(self, basename):
        w = basename.rpartition(".")
        return {"name": w[0], "extension": w[2]} if w[1] == "." else {"name": w[2], "extension": ""}