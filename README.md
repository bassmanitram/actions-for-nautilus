# Actions For Nautilus
An extension to the Gnome **Files** file manager (otherwise known as Nautilus) that allows 
you to add arbitrary actions to the Gnome Files selection context menu.

This extension is a "replacement" for the now-defunct Nautilus file manager functionality
of the `filemanager/nautilus-actions` project.

The extension supports many of the most commonly used features of the original extension project,
including:

* structuring context menu items for Nautilus File Manager selections including
  nested sub menus
* filtering the displayed items based on:
  * number of files in the selection, 
  * mimetypes of the selected files (matching and non-matching conditions
    supported, as well as mimetype globs)
  * basic filetypes of the selected files - e.g. 'file', 'directory',
    'symbolic-link' ... - (matching and non-matching conditions supported)
  * full path pattern matching, expressed as glob patterns or regular expressions, again
    with support for matching and non-matching conditions
* execution of an arbitrary command/script when a menu item is activated, with
  the same "PLURAL" and "SINGULAR" semantics as the 
  `filemanager/nautilus-actions` project
* support for all the command line placeholders implemented by the 
  `filemanager/nautilus-actions` project, with the same semantics

It is also _much_ better at executing commands in a shell than the original
extension, allowing for the construction of pipelines and loops, as well as the 
use of more complex shell expressions, without the need for writing wrapper scripts.

[A configuration application](#configuration-ui) by the name "Actions For Nautilus 
Configurator" is installed into your desktop applications collection. When you
first use the configurator, if no existing configuration file is found, the delivered
[sample configuration](./configurator/sample-config.json) will be installed.

# Installation
## Debian-based systems

Debian packages of the most recent releases are provided in the [dist](./dist) folder.

Simply download the package, install with your package installer, then launch the
**Actions For Nautilus Configurator** application from your applications list in
order to start building a configuration based upon the delivered 
[sample](#sample-configuration).

The Debian package specifies the following **Suggests** dependencies that will
greatly enhance the utility of the extension as well as allow the delivered sample
configuration to work on first launch:

* `xclip`  - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

It is highly recommended to install these extra packages.

To enable the extension after installation, you will need to restart Nautilus/Files:

* `Alt F2`
* `nautilus -q`

should do it.

## Manual Installation
### Install Dependencies

Firstly, of course, the extension relies upon GNOME and GNOME Files (aka
Nautilus) being installed.

Then it relies on `python 3+`, `nautilus-python`, and certain
process management tools (which are likely already installed but
just in case :)).

* Fedora `sudo dnf install nautilus-python python3-gobject procps-ng`
* Ubuntu `sudo apt install python3-nautilus python3-gi procps`
* Arch `sudo pacman -S python-nautilus python-gobject procps-ng`

### Download & Install the Extension

To install the extension manually, then, you will need to
follow these steps:

1. `git clone https://github.com/bassmanitram/actions-for-nautilus.git`
2. `cd actions-for-nautilus`
3. `make install` to install for only your use, or `sudo make install_global`
   to install for all users.
5. You _may_ have to restart the Gnome shell in order to see the configuration
   application in your desktop applications list
   
If you don't have the `git` or `make` commands in your system, simply install them
in the same way you installed the [other dependencies](#install-dependencies).

On _first_ installation, you won't see anything different in the Nautilus context 
menus, because you need to have a working configuration for anything to change. 
The sample configuration will be installed for the user simply by starting the 
[configuration UI](#configuration-ui).

### Uninstallation

1. `cd path/to/actions-for-nautilus`   
2. `make uninstall` if you installed for only your use, or `sudo make uninstall_global`
   if you installed for all users.
3. You _may_ have to restart the Gnome shell in order to remove the configuration
   application from your desktop applications list


## Sample configuration
The delivered [sample configuration file](./configurator/sample-config.json) is copied to 

```
${HOME}/.local/share/actions-for-nautilus/config.json
```

when you first start the configuration UI, if there is no existing configuration. 

The configuration contains examples of command and menu construction, 
including:

* contextual submenus, 
* mimetype, file type, and selection count conditions, 
* the use of command pipelines, 
* exploiting `$(...)`/backtick command and argument substitution.
* ...

The configured commands rely on a few extra dependencies that need to be installed
if you want to see the sample configuration working properly:

* `gedit` - the standard Gnome editor - you probably already have this
* `gnome-terminal` - the standard Gnome terminal emulator (for now) - you probably have
  this too.
* `xclip`  - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

Again, these can be installed using your platform package manager as shown above.

It is also possible that the semantics of the more complex command structures rely
upon shell features, if you are not using BASH as your system shell, will not
work for you.

### The Gnome Terminal "No Close" profile
When executing the `gnome-terminal` command, the sample configuration references a 
`gnome-terminal` profile named "No Close".

This is not a standard profile, but is a useful one to define in that the terminal
doesn't close when the command it is running ends, allowing you to see command output
and/or to relaunch the command.
  
You can create this profile as follows:
  
* Open the `gnome-terminal` application
* Find the `Preferences` dialog (either a menu item or click on the `...` button, then
  on `Preferences`)
* Click on the **+** next to the word `Profiles`
* Give the new profile the name `No Close`
* Click on the `Command` tab
* Ensure that the `When command exits:` option is set to `Hold terminal open`
* Configure anything else you need concerning the profile behavior and look and feel

# Configuration UI
When you install this extension, a configuration application is installed into 
your local desktop Applications collection.

To start the application:
* Open your Applications collection navigator (menu, panel, ...)
* Find **Actions For Nautilus Configurator**
* Click on it

The application will open in your default Web Browser. It will present the
current configuration (creating one from the [delivered sample](./configurator/sample-config.json) 
if no configuration yet exists for the user).

The UI _should_ be pretty self-explanatory - you can add, delete, move and
modify Menus and Commands at will.

Simply close the web page to quit the configurator.

*NOTE* the configurator web application NEVER communicates outside of your own
system unless you click on an external link referenced in the help information.

## Configurator help
The UI includes integrated help that can be accessed in one of two ways:

* Click on the `Show Help` button to open the help viewport to the right of the
  main configurator UI, positioned at the beginning of the help information.
* Click on any of the &#9432; icons to open the help viewport to the right of the
  main configurator UI, positioned at the information pertaining to the UI element
  to which the &#9432; icon is attached.

When both the configurator and the help information are displayed, the viewport
sizes can be adjusted by dragging the line that separates them.

To close the help information, simply click on the `Hide Help` button (which is
the `Show Help` button with the label modified when the help information is being displayed).

## Saving your changes
In order to save configuration changes, click on the **Save Config** button. 
Your changes should be visible in Nautilus after about 30 seconds (the timeout
for the internal config file change watcher).

The existing configuration file is backed up before being overridden by a saved
configuration. You can reinstate an older configuration by opening Nautilus/Files,
navigating to the folder...

```
${HOME}/.local/share/nautilus-python/extensions/actions-for-nautilus
```

and replacing your current `config.json` file with any of the backed up
copies. Again, changes will take effect after a maximum of about 30
seconds.

# Configuration reference
The configuration is specified in a JSON text file named `config.json` located in

```
${HOME}/.local/share/actions-for-nautilus
```

The extension is delivered with a strict valid 
[JSON Schema](./configurator/actions-for-nautilus.schema.json) 
that describes exactly how the configuration file needs to be built.

## Top level structure
The top level structure in the configuration file must be a JSON object which is 
expected to contain a property named `actions` whose value is, itself, an array of 
objects, and a string property named `sort`:

```
{
  "actions": [
    {
      ...
    },
    "sort": "manual or auto"
  ]
}
```

The `sort` property is optional and indicates the approach to use for sorting 
the actions presented by the top level menu. The allowed values are:
* `manual` - The extension leaves the items in the order in which they appear 
  in the configuration
* `auto` - The extension sorts the items in alphanumeric order

The default value is - `manual`

The `actions` array contains the configuration of each action to be presented
in the top level menu

Each element of the array is then an object (and *action*) which, primarily, must have a 
property named `type` whose value is either `command` or `menu`, and a property 
named `label` whose value is the text that you wish to see in the Nautilus 
context menu.

```
    {
      "type": "command",
      "label": "My Command",
      ...
    },
    {
      "type": "menu",
      "label": "My Sub Menu",
      ...
    },
    ...

```

The subsequent sections describe these action objects in detail.

## Menu actions
Actions with a `type` property of `menu` define "sub menu" actions that, when 
clicked on, expose a nested menu of further actions, themselves being command 
actions or further nested menus.

```
    ...
    {
      "type": "menu",
      "label": "My Sub Menu",
      "actions": [
        ...
      ],
      "sort": "manual or auto"
    },
    ...
```

Menu actions are expected to contain two additional properties:

* `actions` - REQUIRED - an array of elements each of which follows the same
  pattern as the elements contained by the configuration's root `actions` 
  property

* `sort` - OPTIONAL - The approach to use for sorting the actions
  presented by the menu
  * `manual` - The extension leaves the items in the order in which they appear 
    in the configuration
  * `auto` - The extension sorts the items in alphanumeric order

  *Default* - `manual`

When the Nautilus/Files context menu is activated for a selection, the extension assesses 
all the commands configured within a menu to establish if the commands are relevant for the current 
selection. If no commands are found to be relevant, then the menu does not appear in the Nautilus/Files 
context menu.

## Command actions
Actions with a `type` property of `command` define actions that, when clicked on, execute a command.

```
    ...
    {
      "type": "command",
      "label": "My Command",
      command_line: "my-script.sh %F %c",
      cwd: "%d",
      use_shell: true,
      min_items: 1,
      max_items: 1,
      "mimetypes": [
        ...
      ],
      "filetypes": [
        ...
      ],
      "path_patterns": [
        ...
      ]
    },
    ...
```

These are expected to have the following additional properties:

* `command_line` - REQUIRED - the system command the should be executed when 
  the menu item is clicked on, expressed as a string. 
  
  The command may contain place holder expressions that are expanded to hold 
  details of the selected files that are passed as arguments to the command.
  
  The full set of placeholders implemented by the `filemanager/nautilus-actions` 
  project are supported, with the same semantics - these are further documented 
  below.

  Note that, when using the `use_shell` option (below), the command line can
  be just about anything you can enter at a shell prompt - including the following 
  features:

  * Pipelines
  * `$(...)` or "backtick" command and argument generation/expansion
  * Environment variable resolution
  * Loops
  * ...

  See the [sample configuration](./configurator/sample-config.json) for a few examples.

* `cwd` - OPTIONAL - the working directory that the command should "run in"
  expressed as a string
  
  This too can contain place holder expressions, though obviously they should
  resolve to a single valid directory name

  *Default* - undefined

* `use_shell` - OPTIONAL - a boolean value (`true` or `false`) that indicates
  whether the command should be run by the default system shell. If the command
  is a shell script, or relies on any shell expansion semantics, you should set 
  the value of this property to `true`.

  *Default* - `false`

* `filetypes` - OPTIONAL - the general filetypes of the selected files for which
  this action is to be displayed (or for which the action is not to be displayed)

  The value should be a JSON list of strings each one of which should have one 
  of the following values:

  * `unknown` - for files of an unknown type
  * `directory` - for directories
  * `file` - for standard files
  * `symbolic-link` - for symbolic links
  * `special` - for special files (pipes, devices, ...)
  * `standard` - shorthand for directories, standard files, and symbolic links
  
  Again, these can be prefixed with a `!` character to indicate that the 
  selected files should _not_ be of that type.

  Only the first appearance of a specific filetype (regardless of any `!` "not"
  prefix) is taken into account.

  *Default* - all filetypes are accepted

* `min_items` - OPTIONAL - the minimum number of items in the selection for 
  which this action will be displayed.

  For example, if the command is expected to, say, compare a number of files,
  it doesn't make sense for the action to be displayed when less than two files
  are in the selection. In that case, you would set the value of this property
  to `2` which would prevent the action from appearing in the context menu when 
  only one file is in the selection. 

  If specified, the value must be greater than zero.

  If the value of `max_items` is greater than zero, the value of this property must 
  be less than or equal to the value of `max_items`.

  *Default* - 1

* `max_items` - OPTIONAL - the maximum number of items in the selection for 
  which this action will be displayed.

  For example, if the command is expected to, say, start an HTTP server in a 
  selected directory, it doesn't make sense for the action to be displayed when 
  more than one directory is in the selection. Therefore, in this case, you 
  would set the value of this property to `1`, which would prevent 
  the action from appearing in the context menu when more than one directory is
  in the selection.

  A value of zero denotes `unlimited`.

  If the value is greater than zero, the value of the `min_items` property must 
  be less than or equal to this value.

  *Default* - unlimited

* `mimetypes` - OPTIONAL - the mimetypes of the selected files for which this
  action is to be displayed (or for which the action is not to be displayed).

  The value should be a JSON list of strings in the following format:

  * `*/*` or `*` - meaning that the action can be displayed for all mimetypes
  * `type/subtype` - to display the action for files of a specific mimetype
  * `type/*` - to display the action for files whose mimetypes are any subtype of
    a specific type
  * `!type/subtype` - to _not_ display the action for files of a specific mimetype
  * `!type/*` - to _not_ display the action for files whose mimetypes are any 
    subtype of a specific type

  All files in the selection must match an action's mimetype rules for that action
  to be displayed. Mixing "not" rules with ... well, "not not" rules, can be
  confusing.

  Only the first appearance of a specific rule (regardless of any `!` "not"
  prefix) is taken into account.

  *Default* - all mimetypes are accepted

* `path_patterns` - OPTIONAL - a list of glob or regular expression patterns against
  which the full paths of the selected files are to be matched.

  The value should be a JSON list of strings, each in one of the following formats:

  * a "glob" expression - a simple but limited string pattern expression syntax that 
    is used by many UNIX shell commands as well as the shell itself, consisting of 
    the following placeholders:

    * `*` indicating zero or more characters
    * `?` indicating a single character
    * `[abc]` indicating one of the characters between the brackets
    * `[!abc]` indicating none of the characters between the brackets

    Quite often this syntax is all that you need in order to express the pattern
    you wish to match against.

    Note that globs inherently match against the whole path.

  * `re:` followed by a regular expression (WITHOUT `/` delimiters) - more complex 
    needs can be expressed as regular expressions.

    Note that regular expressions _do not_ inherently match against the whole path.
    
    This means that if any part of a selected file path matches the regular 
    expression, the path will be accepted.

    If you want to match against the whole path, start your regular expression with
    `^` and end it with `$`.
   
  Either pattern format can be prefixed with `!` in order to negate the pattern.

  All files in the selection must match an action's path pattern rules for that 
  action to be displayed. Mixing "not" rules with ... well, "not not" rules, can be
  confusing.

  Only the first appearance of a specific rule (regardless of any `!` "not"
  prefix) is taken into account.

  The accepted glob syntax is fully documented [here](https://docs.python.org/3/library/fnmatch.html).
  The accepted Regular Expression syntax is fully documented [here ](https://docs.python.org/3/library/re.html#regular-expression-syntax).

  *Default* - all file paths are accepted

With the `mimetypes`, `filetypes` and `path_patterns` filter lists, all selected files
must match at least one non-negated rule (if there are any non-negated rules), while 
matching none of the negated rules, in order for the associated action to appear in the 
context menu.

# Place holders
All the command line and `cwd` placeholders implemented by the 
`filemanager/nautilus-actions` project are implemented by this extension, with 
the same semantics:

| Placeholder | Description                                                                                                | Repetition |
|-------------|------------------------------------------------------------------------------------------------------------|------------|
| `%b`        | the basename of the first selected item (e.g. `my-file.txt`)                                               | SINGULAR   |
| `%B`        | space-separated list of the `%b` values of all selected items                                              | PLURAL     |
| `%c`        | the number of items in the selection                                                                       | ANY        |
| `%d`        | the full path to the directory holding the first selected item (e.g. `/home/me/my-first-dir/my-second-dir` | SINGULAR   |
| `%D`        | space-separated list of the `%d` values of all selected items                                              | PLURAL     |
| `%f`        | the full path of the first selected item (e.g. `/home/me/my-first-dir/my-second-dir/my-file.txt`           | SINGULAR   |
| `%F`        | space-separated list of the `%f` values of all selected items                                              | PLURAL     |
| `%h`        | the host name from the URI of the first selected item                                                      | ANY        |
| `%m`        | the mimetype of the first selected item (e.g. `text/plain`)                                                | SINGULAR   |
| `%M`        | space-separated list of the `%m` values of all selected items                                              | PLURAL     |
| `%n`        | the username from the URI of the first selected item                                                       | ANY        |
| `%o`        | no-op operator which forces a SINGULAR form of execution - see below for more details                      | SINGULAR   |
| `%O`        | no-op operator which forces a PLURAL form of execution - see below for more details                        | PLURAL     |
| `%p`        | the port from the URI of the first selected item                                                           | ANY        |
| `%s`        | the URI scheme from the URI of the first selected item (e.g. `file`)                                       | ANY        |
| `%u`        | the URI of the first selected item (e.g. `file:///home/me/my-first-dir/my-second-dir/my-file.txt`)         | SINGULAR   |
| `%U`        | space-separated list of the `%u` values of all selected items                                              | PLURAL     |
| `%w`        | the basename of the first selected item without it's extension (e.g. `my-file`)                            | SINGULAR   |
| `%W`        | space-separated list of the `%w` values of all selected items                                              | PLURAL     |
| `%x`        | the extension of the first selected item without it's extension (e.g. `txt`)                               | SINGULAR   |
| `%X`        | space-separated list of the `%x` values of all selected items                                              | PLURAL     |
| `%%`        | the `%` character                                                                                          | ANY        |

Any embedded spaces found in the individual values are 'escaped' to ensure that
the shell or system recognizes each value as an independent and complete 
argument to the command.

The meaning of the `Repetition` value is explained in the next section.

# Execution behavior
The `filemanager/nautilus-actions` project implemented a feature whereby a 
configured command could be executed once only, regardless of the number items 
in the selection, or once for each item in the selection.

This extension implements the same feature with the same semantics.

The decision as to which mode is desired is based upon the first placeholder 
found in the `command_line` property value for the activated action:

* If the placeholder has a `Repetition` property of `SINGULAR`, the command is
  executed once for each item in the selection.
* If the placeholder has a `Repetition` property of `PLURAL`, the command is
  executed once only.
* If the placeholder has a `Repetition` property of `ANY`, then the _next_
  placeholder is examined.
* If no placeholder with a `SINGULAR` or `PLURAL` repetition value is found in 
  the command, then the command is executed only once.

Additionally, if the command is to be executed once for each item in the 
selection then any placeholder with a `Repetition` value of `SINGULAR` is 
resolved to the corresponding value for the selected item for which the command
is being executed.

Placeholders with `Repetition` values that are not `SINGULAR` are resolved to 
their full values for each execution of the command.

## An example 

This example is taken directly from the `filemanager/nautilus-actions` project 
documentation:

> Say the current folder is `/data`, and the current selection contains the 
> three files `pierre`, `paul` and `jacques`.
> 
> If we have requested `echo %b`, then the following commands will be 
> successively run:
> 
> ```
> echo pierre
> echo paul
> echo jacques
> ```
> 
> This is because `%b` marks a SINGULAR parameter. The command is then run once
> for each of the selected items.
> 
> Contrarily, if we have requested `echo %B`, then the following command will 
> be run:
> 
> ```
> echo pierre paul jacques
> ```
> 
> This is because `%B` marks a PLURAL parameter. The command is then run only 
> once, with the list of selected items as arguments.
> 
> If we have requested `echo %b %B`, then the following commands will be 
> successively run:
> 
> ```
> echo pierre pierre paul jacques
> echo paul pierre paul jacques
> echo jacques pierre paul jacques
> ```
> 
> This is because the first relevant parameter is `%b`, and so the command 
> is run once for each selected item, replacing at each occurrence the `%b` 
> parameter with the corresponding item. The second parameter is computed and 
> added as arguments to the executed command.
> 
> And if we have requested `echo %B %b`, then the following command will be 
> run:
> 
> ```
> echo pierre paul jacques pierre
> ```
> 
> This is because the first relevant parameter here is `%B`. The command is 
> then run only once, replacing `%B` with the space-separated list of 
> basenames. As the command is only run once, the `%b` is substituted only once
> with the (first) basename.

# Diagnostics
Error messages are sent to the Nautilus `stdout` or `stderr` - including errors
found in the configuration file (such as invalid JSON format).

Additionally, the property `debug` can be set in the top level object, with a
value of `true` or `false` (the default). When set to `true` further debug
information is printed to the Nautilus `stdout`.

In order to _see_ that output you will need to start Nautilus in a special way
from a terminal emulator (e.g. `gnome-terminal`):

```
# Stop Nautilus
nautilus -q  
# Restart with `stdout` and `stderr` being displayed at the terminal
nautilus --no-desktop
```

Note that, in order to stop this special execution mode, you will need to either
close the terminal emulator, or, from another emulator run the `nautilus -q`
command.

# Acknowledgments
The main acknowledgement is, of course, to the original Nautilus Actions 
extension, later renamed to [Filemanager Actions](https://gitlab.gnome.org/Archive/filemanager-actions) 
to reflect its wider applicability (Nemo, for example).

Unfortunately, this extension is no longer maintained and is no longer 
functional since Nautilus 42.2 (itself now renamed Gnome Files, though the 
underlying programming objects are still in the Nautilus namespace).

I was tempted to take over the maintenance of that project, but was put off by
its complex C implementation (I'm a perfectly competent C programmer, mind!).

I was convinced that a much less complex implementation of most of the main
functionality was possible using Python and the glue to Nautilus found in the 
`nautilus-python` framework, and by using a far more semantically relevant 
configuration format such as JSON and adapting an existing JSON editor UI rather
than building a configuration UI from scratch.

I think I have proved my point :)

The other big acknowledgement is of [Christoforos Aslanov](https://github.com/chr314)
whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for the original POC of this 
extension, and whose project structure, installation procedure and doc I 
mercilessly ripped off :)... and I'm even disrespectful enough to have provided 
an alternative to his extension in my own sample config! 

Thanks and apologies, Christoforos.
