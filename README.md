# ANNOUNCEMENT

*Version 2 is coming*

It appears to be functioning very well but it would be helpful to have people test it and feed back via issues.

The version is in the [feature/strict-match](https://github.com/bassmanitram/actions-for-nautilus/tree/feature/strict-match) branch.
follow the installation instructions (no DEB installer yet).

The documentation is still being tweaked, but all major feature updates are explained and should be linkable from the
configurator.

Thank you

# IMPORTANT NOTE
All users of releases 1.6.0 and before should update their installations to release 1.6.1 as soon as possible
due to a security issue.

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
  * user's access permissions for the selected files,
  * mimetypes of the selected files (matching and non-matching conditions
    supported, as well as mimetype globs),
  * basic filetypes of the selected files - e.g. 'file', 'directory',
    'symbolic-link' ... - (matching and non-matching conditions supported),
  * full path pattern matching, expressed as glob patterns or regular expressions, again
    with support for matching and non-matching conditions.
  * even invoking an external program to decide if an action should be visible
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

The project has a [wiki](https://github.com/bassmanitram/actions-for-nautilus/wiki) that is used to share 
tips and tricks and useful configuration examples.

# Installation
## Debian-based systems

Debian packages of the most recent releases are provided in the [dist](./dist) folder.

Simply download the package, install with your package installer, then launch the
**Actions For Nautilus Configurator** application from your applications list in
order to start building a configuration based upon the delivered 
[sample](#sample-configuration).

To enable the extension after installation, you will need to restart Nautilus/Files:

* `Alt F2`
* `nautilus -q`

should do it.

### Suggested Additional Packages
The Debian package specifies the following **Suggests** dependencies that will
greatly enhance the utility of the extension as well as allow the delivered sample
configuration to work on first launch:

* `xclip`  - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

It is highly recommended to install these extra packages.

## Manual Installation
### Install Dependencies

Firstly, of course, the extension relies upon GNOME and GNOME Files (aka
Nautilus) being installed.

Then it relies on `python 3+`, `nautilus-python`, and certain
process management tools (which are likely already installed but
just in case :)).

* Fedora `sudo dnf install nautilus-python python3-gobject procps-ng js-jquery`
* Ubuntu `sudo apt install python3-nautilus python3-gi procps libjs-jquery`
* Arch `sudo pacman -S python-nautilus python-gobject procps-ng jquery`

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
upon shell features that, if you are not using BASH as your system shell, will not
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

There is also an embedded JSON source editor with syntax checking should you wish
to perform actions not supported by the main UI (such as copy/paste of actions).

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

That schema contains descriptions of objects and properties that may or must appear in the
connfiguration as it appears on disk, and as the Nautilus extension expects. 

(Note that there is also a _second_ [JSON Schema](./configurator/actions-for-nautilus.ui.schema.json)
delivered. This is for use by the configurator and should not be
considered a canonical description of the extension configuration file).

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

Another big acknowledgement is of [Christoforos Aslanov](https://github.com/chr314)
whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for the original POC of this 
extension, and whose project structure, installation procedure and doc I initially
mercilessly ripped off :)... and I'm even disrespectful enough to have provided 
an alternative to his extension in my own sample config! 

Thanks and apologies, Christoforos.

The JSON Schema-based editor [JSON-Editor](https://github.com/json-editor/json-editor) is an amazing find! 
The configurator is, in effect, an instance of that editor with a few tweaks to make it look and feel
a bit more natural for this use case! As of version 2, I use [my own fork of the project](https://github.com/bassmanitram/json-editor) 
because there are fixes and enhancements for which I have submitted PRs, but it takes a while to get these 
actually merged into the main project. You are welsome to submit your own PRs to that project as you see fit.

The embedded JSON source editor is the [ACE source editor](https://ace.c9.io/) - another amazing project
which was so easy to embed that one wonders why JSON-Editor doesn't use that for its own JSON source
editing feature - I feel another PR coming on :).

So, a BIG shout-out to those two projects!
