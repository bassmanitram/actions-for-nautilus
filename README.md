# actions-for-nautilus
A "replacement" for the now defunct filemanager/nautilus-actions project.

While this does not claim to be as full function as the defunct extension, and it doesn't
have a configuration UI yet, it does do the common stuff:

* structuring context menu items for Nautilus File Manager selections including nested sub menus
* filtering the displayed items based on:
   * number of items in the selection, 
   * mimetypes of the selected items (matching and non-matching conditions supported, as well as mimetype groups)
   * basic filetypes of the selected items - e.g. 'file', 'directory', 'symbolic-link' ... - (matching and non-matching conditions supported)
* execution of an arbitrary command/script when a menu item is activated, with "PLURAL" and "SINGULAR" semantics drawn from
  the filemanager/nautilus-actions project
* support for all the command line placeholders supported by the filemanager/nautilus-actions project, with the same semantics

The included sample `config.json` file shows how to set up a config. When you change it you will need to restart
Nautilus - `nautilus -q` from a command line or prompt.

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
   
3. Restart the Nautilus (`nautilus -q`) if still seeing the options after uninstall.

# Sample Scripts
The delivered sample `config.json` (found in `${HOME}/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json` after installation)
is, obviously, highly tailored to my own set-up. But in order to make things work upon installation, I deliver the three scripts that
are referenced by that configuration in the folder [sample-scripts](./sample-scripts). 

On the other hand, I don't want to invade your privacy, so these are NOT installed in an executable location by the installation process.

So, if you want to fully use the delivered config you'll need to do the following:

* Copy the contents of the folder `sample-scripts` to a location that is in your normal `PATH` environment variable setting (e.g. `${HOME}/bin`)
* Make the scripts executable
  * Select them in Nautilus/Files
  * Right click, then click on `Properties`
  * Select the `Permissions` tab
  * Ensure that the `Execute` checkbox is checked

You'll also need to install the following from your package manager if you want _all_ the actions to fully work
* `gedit` - the standard Gnome editor
* `git` - (you probably have that already if you followed the installation instructions above :))
* `nodejs` - you likely know what that is - but, just in case, it is a framework for executing Javascript programs outside of a browser.
* `xclip`  - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

Finally, the `Folder Actions/Start HTTP Server Here` action uses the NodeJS `http-server` NPM module: 
* after installing NodeJS, install that module either from your package manager
  or by running the command `sudo npm install -g http-server`

# Configuration
The configuration is specified in a JSON text file named `config.json` locate in `${HOME}/.local/share/nautilus-python/extensions/actions-for-nautilus`.

As yet there is no UI for creating this configurations, however the semantics are pretty simple if you know JSON.

The top level JSON object is expect to contain a property named `items` whose value is an array.

Each element of the array is then an object which, primarily, must have a property named `type` whose value is either `item` or `menu`, and
a property named `label` whose value is the text that you wish to see in the Nautilus context menu.

## Item elements
Elements with a `type` property of `item` define "action" items that, when clicked on, execute a command.

They are expected to have the following additional properties:

* `command_line` - REQUIRED - the system command the should be executed when 
  the item is clicked on, expressed as a string. 
  
  The command may contain place holder expressions that are expanded to hold 
  details of the selected files that are passed as arguments to the command.
  
  The full set of placeholders implemented by the filemanager/nautilus-actions 
  project are supported, with the same semantics - these are further documented 
  below.

* `cwd` - OPTIONAL - the working directory that the command should "run in" expressed as a string
  
  This too can contain place holder expressions, though obviously they should resolve to a single
  valid directory name

  *Default* - undefined

* `use_shell` - OPTIONAL - a boolean value (`true` or `false`) that indicates whether
  the command should be run by the default system shell. If the command is a shell script
  you should set the value of this property to `true`

  *Default* - `false`

* `max_items` - OPTIONAL - the maximum number of items in the selection for which this item
  will be displayed.

  For example, if the command is expected to, say, start an HTTP server in a selected directory,
  it doesn't make sense for the item to be displayed when more than one directory is in the
  selection. Therefore, in this case, the value of this property would be set to `1`.

  *Default* - unlimited

* `mimetypes` - OPTIONAL - the mimetypes of the selected files for which this item is to be
  displayed (or for which the item is not to be displayed)

  The values should be a JSON list of strings in the following format:

  * `*/*` or `*` - meaning that the item can be displayed for all mimetypes
  * `type/subtype` - to display the item to a files of a specific mimetype
  * `type/*` - to display the item files whose mimetypes are subtypes of a specific type
  * `!type/subtype` - to _not_ display the item to a files of a specific mimetype
  * `!type/*` - to _not_ display the item files whose mimetypes are subtypes of a specific type

  All files in the selection must match the mimetype rules for an item in order for that item
  to be displayed. Mixing not rules with ... well, not not rules, can be confusing!

  Duplicate rules are ignored.

  *Default* - all mimetypes 

* `filetypes` - OPTIONAL - the general filetypes of the selected files for which this 
  item is to be displayed (or for which the item is not to be displayed)

  The values should be a JSON list of strings each one of which should have one of the
  following values:

  * `unknown` - for files of an unknown type
  * `directory` - for directories
  * `file` - for standard files
  * `symbolic-link` - for symbolic links
  * `special` - for special file types (pipes, devices, ...)
  * `standard` - for directories, standard files, and symbolic links
  
  Again, these can be prefixed with a `!` character to indicate that the selected files
  should _not_ be of that type.

  Duplicate entries are ignored (e.g. a "not" following a "not not").

  *Default* - all filetypes

## Place holders
TO BE COMPLETED

## Execution behavior
TO BE COMPLETED

# Acknowledgments
The main acknowledgement is of [Christoforos Aslanov](https://github.com/chr314) whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for my own extension, and whose project structure, installation procedure and doc I mercilessly 
ripped off :)... and I'm even disrespectful enough to have provided an alternative to his extension in my own sample config and scripts! Thanks
and apologies, Christoforos.
