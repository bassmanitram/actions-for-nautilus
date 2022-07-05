import os
import subprocess
import json
from gi.repository import Nautilus, GObject, Gtk, Gdk
from gi import require_version

require_version('Gtk', '3.0')
require_version('Nautilus', '3.0')

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

    def get_file_items(self, window, files):
        return self._create_menu_items(files, "File")

    def get_background_items(self, window, file):
        return self._create_menu_items([file], "Background")

    def _create_menu_items(self, files, group):
        menu_items = []
        my_files = {
            "mimetypes": [],
            "names": [],
            "folders": [],
            "uris": [],
            "by_file": [],
            "file_count": len(files)
        }
        for file in files:
            this_file = {
                "mimetype": file.get_mime_type(),
                "name": os.path.basename(file.get_location().get_path()),
                "folder": os.path.dirname(file.get_location().get_path()),
                "uri": file.get_uri()
            }
            my_files["names"].append(this_file["name"])
            my_files["mimetypes"].append(this_file["mimetype"])
            my_files["folders"].append(this_file["folder"])
            my_files["uris"].append(this_file["uri"])
            my_files["by_file"].append(this_file)

        if "items" in self.config:
            config_items = self.config["items"]
            for idx, config_item in enumerate(config_items):
                menu_item = self._create_menu_item(str(idx), config_item, my_files, group)
                if menu_item is not None:
                    menu_items.append(menu_item)

        return sorted(menu_items,key=lambda element: element.props.label)
        
    def _create_menu_item(self, idString, config_item, files, group):
        if config_item["type"] == "menu":
            return self._create_menu_menu_item(idString, config_item, files, group)
        elif config_item["type"] == "item":
            return self._create_item_menu_item(idString, config_item, files, group)
        else:
            return None
                 
    def _create_menu_menu_item(self, idString, config_item, files, group):
        sub_items = []
        if "items" in config_item:
            for idx, sub_item in enumerate(config_item["items"]):
                menu_item = self._create_menu_item(idString + "_" + str(idx), sub_item, files, group)
                if menu_item is not None:
                    sub_items.append(menu_item)
            
            if len(sub_items) > 0:
                menu = Nautilus.Menu()
                menu_item = Nautilus.MenuItem(
                    name="Actions4Nautilus::Menu" + idString + group,
                    label=config_item["label"],
                )
                menu_item.set_submenu(menu)
                for menu_sub_item in sorted(sub_items,key=lambda element: element.props.label):
                    menu.append_item(menu_sub_item)
                return menu_item
            else:
                return None
        else:
            return None

    def _create_item_menu_item(self, idString, config_item, files, group):
        if ("max_items" in config_item and 
            isinstance(config_item["max_items"], int) and 
            config_item["max_items"] < files["file_count"]):
                return None

        if self._applicable_to_mime(config_item, files):
            menu_item = Nautilus.MenuItem(
                name="NautilusCopyPath::Item" + idString + group,
                label=config_item["label"],
            )
            menu_item.connect("activate", self._run_command, config_item, files)
            return menu_item
        else:
            return None

    def _applicable_to_mime(self, config_item, files):
        if "mimetypes" in config_item:
            intersection = [value for value in config_item["mimetypes"] if value in files["mimetypes"]]
            if len(intersection) == 0:
                return False
        return True


    def _run_command(self, menu, config_item, files):
        cwd = self._expand_token(config_item["cwd"], files["by_file"][0]) if "cwd" in config_item else None
        use_shell = bool(config_item["use_shell"]) if "use_shell" in config_item else False

        final_command_line = []
        for token in config_item["command_line"]:
            mod_token = token.replace("%%", "PERCENTPERCENT")
            if self._token_needs_expanding(token):
                for idx in range(files["file_count"]):
                    final_command_line.append(self._expand_token(mod_token, files["by_file"][idx]).replace("PERCENTPERCENT", "%"))
            else: 
                final_command_line.append(mod_token.replace("PERCENTPERCENT", "%"))

        if use_shell:
            final_command_line = " ".join(f'"{w}"' for w in map(lambda x: x.replace('"','\\"'), final_command_line))

        print(cwd)
        print(' '.join(final_command_line))
        print(files)
        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell) #creationflags=subprocess.DETACHED_PROCESS)

    def _token_needs_expanding(self, token):
        for pattern in self.place_holders.keys():
            if token.find(pattern) != -1:
                return True
        return False

    def _expand_token(self, token, file_detail):
        return_token = token
        for pattern in self.place_holders.keys():
            return_token = return_token.replace(pattern,file_detail[self.place_holders[pattern]])
        return return_token

