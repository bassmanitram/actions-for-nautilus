# actions-for-nautilus
A "replacement" for the now defunct filemanager/nautilus-actions project.

While this does not claim to be as full function as the defunct extension, and it doesn't
have a configuration UI yet, it does do the common stuff:

* structuring context menu items for Nautilus File Manager selections including nested sub menus
* filtering the displayed items based on number of items in the selection, and mime-types of the selected items,
* execution of an arbitrary command/script when a menu item is activated

The included sample `config.json` file shows how to set up a config. When you change it you will need to restart
Nautilus - `nautilus -q` from a command line or prompt.

# Instalation
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

On the otherhand, I don't want to invade your privacy, so these are NOT installed in an executable location by the installation process.

So, if you want to fully use the delivered config you'll need to do the following:

* Copy the contents of the folder `sample-scripts` to a location that is in your normal `PATH` environment variable setting (e.g. `${HOME}/bin`)
* Make the scripts executable
  * Select them in Nautilus/Files
  * Right click, then click on `Properties`
  * Select the `Permissions` tab
  * Ensure that the `Execute` checkbox is checked

You'll also need to install the following from your package manager if you want _all_ the actions to fully work
* `git` (you probably have that already if you followed the installation instructions above :))
* `nodejs` - you likely know what that is - but, just in case, it is a framework for executing Javascript programs outside of a browser.
* `xclip` - a command line tool for managing the X clipboards 
* `zenity` - a Gnome UI toolkit for shell scripts

Finally, the `Folder Actions/Start HTTP Server Here` action uses the NodeJS `http-server` NPM module: 
* after installing NodeJS, install that module either from your package manager
  or by running the command `sudo npm install -g http-server`

# Acknowledments
The main acknowledgement is of [Christoforos Aslanov](https://github.com/chr314) whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for my own extension, and whose project structure, installation procedure and doc I mercilessly 
ripped off :)... and I'm even disrespectful enough to have provided an alternative to his extension in my own sample config and scripts! Thanks
and apologies, Christoforos.
