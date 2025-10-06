import logging
import shlex
import subprocess
from gi.repository import GObject
from gi.repository import Nautilus
import afn_config
import afn_menu
import afn_shell_tools

# Set up logging configuration
def setup_logging():
    """Setup logging configuration for the extension"""
    # Create logger
    logger = logging.getLogger('actions_for_nautilus')

    # Avoid duplicate handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()

        # Create formatter
        formatter = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger

def update_logging_level(debug_enabled):
    """Update the logging level based on config debug flag"""
    logger = logging.getLogger('actions_for_nautilus')
    level = logging.DEBUG if debug_enabled else logging.WARNING
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

# Initialize logging
logger = setup_logging()

#
#  A multi-version alternative to require_version
#
if not (Nautilus._version.startswith("3.") or 
        Nautilus._version.startswith("4.")):
    raise ValueError('Namespace %s not available for versions %s' %
                     ("Nautilus", "3 or 4"))

#
#  The MenuProvider implementation
#
class ActionsForNautilus(Nautilus.MenuProvider, GObject.GObject):

    def __init__(self):
        self.config = afn_config.ActionsForNautilusConfig()

#
# Menu provider interface implementation
#
    def get_file_items(self, *args):
        files = args[-1]

        if len(files) < 1:
            logger.debug("NO FILE")
            return None

        logger.debug(
            f'GET FILES: {" ".join(f.get_location().get_path() for f in files)}'
        )
        menu = afn_menu.create_menu_items(
            self.config, files, "File", _run_command
        )
        logger.debug("END GET FILES")
        return menu

    def get_background_items(self, *args):
        file = args[-1]
        logger.debug(f'GET BACKGROUND: {file.get_location().get_path()}')
        menu = afn_menu.create_menu_items(
            self.config, [file], "Background", _run_command
        )
        logger.debug("END BACKGROUND")
        return menu

#
# Command execution
#
def _run_command(menu, action, files):

    logger.debug(
        f"Command execution - Menu: {menu}, Action: {action}, Files: {files}"
    )

    use_shell = action.use_shell
    count = 1 if action.cmd_is_plural else len(files)

    context = None
    for i in range(count):
        cwd = (None if action.cwd is None else 
               afn_shell_tools.resolve(action.cwd, 0, [files[i]], False, None)[0])
        logger.debug(f'Working directory: {cwd}')

        if len(action.command_line_parts) < 1:
            # Old command line interpolation
            logger.debug(f"Using original parsing for action {action.idString}")
            (final_command_line, context) = afn_shell_tools.resolve(
                action.command_line, i, files, True, context
            )

            if not use_shell:
                #
                # Split into args and lose any shell escapes
                #
                escape_backslash = "!§ESCBACKSLASH§µ"
                final_command_line = list(map(
                    lambda arg: (arg.replace("\\\\", escape_backslash)
                               .replace("\\", "")
                               .replace(escape_backslash, "\\")),
                    shlex.split(final_command_line)
                ))
        else:
            # New command line interpolation
            logger.debug(f"Using improved parsing for action {action.idString}")
            (final_command_line, context) = afn_shell_tools.resolve2(
                action.command_line_parts, i, files, 
                True if use_shell else False, context
            )
            if use_shell:
                #
                # Join the arguments
                #
                final_command_line = "".join(final_command_line)

        logger.debug(
            f"Executing COMMAND {i}: {final_command_line} | "
            f"Cwd: {cwd} | Use shell: {use_shell}"
        )

        subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)