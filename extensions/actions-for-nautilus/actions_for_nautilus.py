import subprocess, shlex, inspect
from gi.repository import Nautilus, GObject
import afn_place_holders, afn_config, afn_menu, os

###
### A multi-version alternative to require_version
###
if not (Nautilus._version.startswith("3.") or Nautilus._version.startswith("4.")):
    raise ValueError('Namespace %s not available for versions %s' %
                         ("Nautilus", "3 or 4"))

###
### The MenuProvider implementation
###
class ActionsForNautilus(Nautilus.MenuProvider, GObject.GObject):

    def __init__(self):
        self.config = afn_config.ActionsForNautilusConfig()
        self.previous_background_path = None
        self.previous_background_menu = None
        self.previous_selection_path = None
        self.previous_selection_menu = None

#
# Menu provider interface implementation
#
    def get_file_items(self, *args):
        files = args[-1]
        if len(files) < 1:
            return None
        id = None
        # Debouncing double clicks
        if len(files) == 1:
            file_path = files[0].get_location().get_path()
            mod_time = os.path.getmtime(file_path)
            id = f'{file_path}-{mod_time}'
            if id == self.previous_selection_path:
                afn_config.debug_print(f'FILES: Using previous selection menu for "{file_path}"')
                return self.previous_background_menu

        afn_config.debug_print(f'FILES: {" ".join(f.get_location().get_path() for f in files)}')
        menu = afn_menu.create_menu_items(self.config, files, "File", _run_command)
        if id is not None:
            self.previous_selection_path = id
            self.previous_selection_menu = menu
        return menu

    def get_background_items(self, *args):
        file = args[-1]
        file_path = file.get_location().get_path()
        mod_time = os.path.getmtime(file_path)
        id = f'{file_path}-{mod_time}'
        # Debouncing background calls
        if id == self.previous_background_path:
            afn_config.debug_print(f'BACKGROUND: Using previous background menu for "{file_path}"')
            return self.previous_background_menu
        # Debouncing double clicks
        if id == self.previous_selection_path:
            afn_config.debug_print(f'BACKGROUND: Using previous selection menu for "{file_path}"')
            self.previous_background_path = self.previous_selection_path
            self.previous_background_menu = self.previous_selection_menu
            return self.previous_selection_menu
        afn_config.debug_print(f'BACKGROUND: "{file_path}"')
        menu = afn_menu.create_menu_items(self.config, [file], "Background", _run_command)
        self.previous_background_path = id
        self.previous_background_menu = menu
        return menu


#
# Command execution
#
def _run_command(menu, config_item, files):
    cwd = afn_place_holders.resolve(config_item["cwd"], 0, [files[0]], False) if "cwd" in config_item else None
    use_shell = bool(config_item["use_shell"]) if "use_shell" in config_item else False

    count = 1 if config_item["cmd_behavior"] == afn_place_holders.PLURAL else len(files)

    if afn_config.debug:
        print(config_item)
        print(files)
        print(cwd)

    for i in range(count):
        #
        # This is innefficient at the moment because the plural and agnostic place holder
        # expansions are recalculated every time
        #
        final_command_line = afn_place_holders.resolve(config_item["command_line"], i, files, True)

        if not use_shell:
            #
            # Split into args and lose any shell escapes
            #
            final_command_line = list(map(lambda arg: arg.replace("\\\\","!§ESCBACKSLASH§µ").replace("\\", "").replace("!§ESCBACKSLASH§µ","\\"),shlex.split(final_command_line)))
        if afn_config.debug:
            print("COMMAND " + str(i))
            print(final_command_line)
        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)
