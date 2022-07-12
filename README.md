# actions-for-nautilus
A "replacement" for the now defunct `filemanager/nautilus-actions` project.

The extension supports many of the most commonly used features of that project,
including:

* structuring context menu items for Nautilus File Manager selections including
  nested sub menus
* filtering the displayed items based on:
   * number of files in the selection, 
   * mimetypes of the selected files (matching and non-matching conditions
     supported, as well as mimetype globs)
   * basic filetypes of the selected files - e.g. 'file', 'directory',
     'symbolic-link' ... - (matching and non-matching conditions supported)
* execution of an arbitrary command/script when a menu item is activated, with
  the same "PLURAL" and "SINGULAR" semantics as the 
  `filemanager/nautilus-actions` project
* support for all the command line placeholders implemented by the 
  `filemanager/nautilus-actions` project, with the same semantics

The included sample `config.json` file shows how to set up a config. When you
change it you will need to restart Nautilus - `nautilus -q` from a command line
or prompt.

# Installation
## Install Dependencies

Fedora `sudo dnf install nautilus-python python3-gobject`

Ubuntu `sudo apt install python3-nautilus python3-gi`

Arch `sudo pacman -S python-nautilus python-gobject`

## Download & Install the Extension

1. `git clone https://github.com/bassmanitram/actions-for-nautilus.git`

2. `cd actions-for-nautilus`

3. `make install`

4. Restart the Nautilus (`nautilus -q`) if not seeing the options.

## Uninstallation

1. `cd path/to/actions-for-nautilus`
   
2. `make uninstall`
   
3. Restart the Nautilus (`nautilus -q`) if still seeing the options after
   uninstall.

# Sample Scripts
The delivered sample `config.json` (found in 

```
${HOME}/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json
```

after installation) is, obviously, highly tailored to my own set-up and to
testing and feature demonstration. But in order to make things work upon
installation, I deliver the scripts that are referenced by that configuration 
in the folder [sample-scripts](./sample-scripts). 

On the other hand, I don't want to invade your privacy, so these are NOT
installed in an executable location by the installation process.

So, if you want to fully use the delivered config you'll need to do the 
following:

* Copy the contents of the folder `sample-scripts` to a location that is in your
  normal `PATH` environment variable setting (e.g. `${HOME}/bin`)
* Make the scripts executable
  * Select them in Nautilus/Files
  * Right click, then click on `Properties`
  * Select the `Permissions` tab
  * Ensure that the `Execute` checkbox is checked

You'll also need to install the following from your package manager if you want
_all_ the actions to fully work

* `gedit` - the standard Gnome editor
* `git` - (you probably have that already if you followed the installation 
  instructions above :))
* `nodejs` - you likely know what that is - but, just in case, it is a framework
  for executing Javascript programs outside of a browser.
* `xclip`  - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

Finally, the `Folder Actions/Start HTTP Server Here` action uses the NodeJS
`http-server` NPM module: 

* after installing NodeJS, install that module either from your package manager
  or by running the command `sudo npm install -g http-server`

# Configuration
The configuration is specified in a JSON text file named `config.json` locate in

```
${HOME}/.local/share/nautilus-python/extensions/actions-for-nautilus
```

As yet there is no UI for creating this configurations, however the semantics
are pretty simple if you know JSON.

Additionally, the extension is delivered with a strict valid 
[JSON Schema](./extensions/actions-for-nautilus/actions-for-nautilus.schema.json) 
that describes exactly how the configuration file needs to be built. Eventually
this will form the basis of a generated UI, and, indeed, can already be used 
with online JSON Schema-based JSON editors such as 
[JSON Editor](https://json-editor.github.io/json-editor/).

## Top level structure
The top level structure in the configuration file must be a JSON object which is 
expected to contain a property named `actions` whose value is, itself, an array of 
objects:

```
{
  "actions": [
    {
      ...
    },
    ...
  ]
}
```

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
      ]
    },
    ...
```

Menu actions are expected to contain one addition property:

* `actions` - REQUIRED - an array of elements each of which follows the same
  pattern as the elements contained by the configuration's root `actions` 
  property

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
      max_items: 1,
      "mimetypes": [
        ...
      ],
      "filetypes": [
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

* `max_items` - OPTIONAL - the maximum number of items in the selection for 
  which this action will be displayed.

  For example, if the command is expected to, say, start an HTTP server in a 
  selected directory, it doesn't make sense for the action to be displayed when 
  more than one directory is in the selection. Therefore, in this case, you 
  would set the value of this property would be set to `1`, which would prevent 
  the action from appearing in the context menu when more than one directory is
  in the selection.

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

  All files in the selection must match an actions's mimetype rules for that action
  to be displayed. Mixing "not" rules with ... well, "not not" rules, can be
  confusing.

  Only the first appearance of a specific rule (regardless of any `!` "not"
  prefix) is taken into account.

  *Default* - all mimetypes 

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

  *Default* - all filetypes

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
functionality (outside of a configuration UI) was possible using Python and 
the glue to Nautilus found in the `nautilus-python` framework, and by using a 
far more semantically relevant configuration format such as JSON.

I think I have proved my point :)

The other big acknowledgement is of [Christoforos Aslanov](https://github.com/chr314)
whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for the original POC of this 
extension, and whose project structure, installation procedure and doc I 
mercilessly ripped off :)... and I'm even disrespectful enough to have provided 
an alternative to his extension in my own sample config and scripts! 

Thanks and apologies, Christoforos.
