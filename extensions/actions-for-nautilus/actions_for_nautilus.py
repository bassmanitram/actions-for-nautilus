import subprocess, shlex
from gi.repository import Nautilus, GObject, Gtk, Gdk
from gi import require_version

import afn_place_holders, afn_config, afn_menu

require_version('Gtk', '3.0')
require_version('Nautilus', '3.0')

###
### The MenuProvider implementation
###
class ActionsForNautilus(Nautilus.MenuProvider, GObject.GObject):

    def __init__(self):
        self.config = afn_config.ActionsForNautilusConfig()

#
# Menu provider interface implementation
#
    def get_file_items(self, window, files):
        return afn_menu.create_menu_items(self.config.get_config(), files, "File", _run_command)

    def get_background_items(self, window, file):
        return afn_menu.create_menu_items(self.config.get_config(), [file], "Background", _run_command)

#
# Command execution
#
def _run_command(menu, config_item, files):
    cwd = afn_place_holders.resolve(config_item["cwd"], 0, [files[0]], False) if "cwd" in config_item else None
    use_shell = bool(config_item["use_shell"]) if "use_shell" in config_item else False

    count = 1 if config_item["cmd_behavior"] == afn_place_holders.PLURAL else len(files)

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
        print("COMMAND " + str(i))
        print(final_command_line)
        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)
