const iconNames = {
	"command": "fa-chevron-right",
	"menu": "fa-bars"
}

const infoText = {
	"#action:toolbar": { "text": "Manage the menu", "help_label": "action-toolbar" },
	"#action": { "text": "An entry that will appear in the Nautilus context menu. Such an entry can be a Command or a nested Menu. Click for more info.", "help_label": "actions" },
	"#command:command_line": { "text": "The command line to execute when the action is clicked on.  Click for more info.", "help_label": "commands" },
	"#command:cwd": { "text": "The current working directory to set when executing the command. Placeholders are allowed. Click for more info.", "help_label": "cwd" },
	"#command:disabled": { "text": "If the command is marked as disabled it will not appear in the Gnome Files context menu", "help_label": "action-disable" },
	"#command:filetype": { "text": "A file type for which the action will be displayed, or not be displayed in the event of a '!' prefix. Click for more info.", "help_label": "file-types" },
	"#command:filetypes": { "text": "A list of file types for which the action will be displayed, or not be displayed in the event of a '!' prefix. Click for more info.", "help_label": "file-types" },
	"#command:label": { "text": "The label that will appear in the context menu for this command. Click for more info.", "help_label": "command-label" },
	"#command:interpolation": { "text": "How to interpolate placeholders into the command line. Click for more info.", "help_label": "placeholder-interpolation" },
	"#command:min_items": { "text": "The minimum number of items in the selection for which this action will be displayed. The default is 1. Must be less than or equal to max_items if max_items is greater than zero. Click for more info.", "help_label": "min-items" },
	"#command:min_items": { "text": "The minimum number of items in the selection for which this action will be displayed. The default is 1. Must be less than or equal to max_items if max_items is greater than zero. Click for more info.", "help_label": "min-items" },
	"#command:max_items": { "text": "The maximum number of items in the selection for which this action will be displayed. Zero indicates unlimited. The default is zero. If not zero, must be greater than or equal to min_items. Click for more info.", "help_label": "max-items" },
	"#command:mimetypes": { "text": "A list of standard mimetype specifications for which the action will be displayed, or not be displayed in the event of a '!' prefix. Click for more info.", "help_label": "mimetypes" },
	"#command:path_pattern": { "text": "A path pattern for which the action will be displayed, or not be displayed in the event of a '!' prefix. Click for more info.", "help_label": "path-patterns" },
	"#command:path_patterns": { "text": "A list of path patterns for which the action will be displayed, or not be displayed in the event of a '!' prefix. Click for more info.", "help_label": "path-patterns" },
	"#command:show_if_true": { "text": "A command to execute to determine if the action should be displayed. Click for more info.", "help_label": "show-if-true" },
	"#command:strict_match": { "text": "All selected files must match the same rule (which has different semantics depending on the rule type). Click for more info.", "help_label": "strict-match" },
	"#command:use_shell": { "text": "Instead of directly executing the command, execute it using the default shell command. Click for more info.", "help_label": "use-shell" },
	"#command": { "text": "An entry in the Nautilus context menu or sub menu that, when clicked on, results in a command being executed. Click for more info.", "help_label": "command-actions" },
	"#root:actions": { "text": "The list of command actions and/or submenus that will be added to the Nautilus context menu. Click for more info.", "help_label": "menu-actions" },
	"#root:debug": { "text": "When set to true, extra debugging information is sent to the Nautilus stdout/stderr destinations. Click for more info.", "help_label": "root-sort-debug" },
	"#root:sort": { "text": "Whether actions should be sorted automatically or left in the configured order. Click for more info.", "help_label": "root-sort-debug" },
	"#submenu:actions": { "text": "The list of command and/or menu actions that will be displayed when this menu action is clicked on. Click for more info.", "help_label": "menu-actions" },
	"#submenu:disabled": { "text": "If the menu is marked as disabled it and its items will not appear in the Gnome Files context menu", "help_label": "action-disable" },
	"#submenu:label": { "text": "The label that will appear in the context menu for this sub menu. Click for more info.", "help_label": "submenu-label" },
	"#submenu:sort": { "text": "Whether actions should be sorted automatically or left in the configured order. Click for more info.", "help_label": "submenu-sort" },
	"#submenu:toolbar": { "text": "Manage the menu", "help_label": "menu-toolbar" },
	"#submenu": { "text": "An entry in the Nautilus context menu or sub menu that, when clicked on, results in a sub menu being displayed. Click for more info.", "help_label": "menu-actions" },
	"#command:permissions": { "text": "The minimum access permissions that you must have for the selected files in order for the command to be displayed. Click for more info.", "help_label": "permissions" }
}
