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

#
# Menu provider interface implementation
#
    def get_file_items(self, *args):
        files = args[-1]
        if afn_config.debug:
            print(f'GET FILES: {" ".join(f.get_location().get_path() for f in files)}')

        if len(files) < 1:
            if afn_config.debug:
                print("NO FILE")
            return None

        menu = afn_menu.create_menu_items(self.config, files, "File", _run_command)
        if afn_config.debug:
            print(f"END GET FILES")
        return menu

    def get_background_items(self, *args):
        file = args[-1]
        if afn_config.debug:
            print(f'GET BACKGROUND: {file.get_location().get_path()}')
        menu = afn_menu.create_menu_items(self.config, [file], "Background", _run_command)
        if afn_config.debug:
            print(f"END BACKGROUND")
        return menu

#
# Command execution
#
def _run_command(menu, action, files):
    use_shell = action.use_shell

    count = 1 if action.cmd_behaviour == afn_place_holders.PLURAL else len(files)

    if afn_config.debug:
        print(action)
        print(files)

    context = None
    for i in range(count):
        cwd = None if action.cwd is None else afn_place_holders.resolve(action.cwd, 0, [files[i]], False, None)[0]
        if afn_config.debug: 
            print(f'cwd: {cwd}')

        if len(action.command_line_parts) < 1:
            # Old command line interpolation
            (final_command_line, context) = afn_place_holders.resolve(action.command_line, i, files, True, context)

            if not use_shell:
                #
                # Split into args and lose any shell escapes
                #
                final_command_line = list(map(lambda arg: arg.replace("\\\\","!§ESCBACKSLASH§µ").replace("\\", "").replace("!§ESCBACKSLASH§µ","\\"),shlex.split(final_command_line)))
        else:
            # New command line interpolation
           (final_command_line, context) = afn_place_holders.resolve2(action.command_line_parts, i, files, False, context)                

        if afn_config.debug:
            print(f"COMMAND {str(i)}: {final_command_line}")
            print(f'Cwd: {cwd}')
            print(f'Use shell: {use_shell}')

        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)
