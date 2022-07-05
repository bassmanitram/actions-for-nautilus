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

# Acknowledments
The main acknowledgement is of [Christoforos Aslanov](https://github.com/chr314) whose [Nautilus Copy Path](https://github.com/chr314/nautilus-copy-path) 
extension provided the inspiration and template for my own extension, and whose project structure, installation procedure and doc I mercilessly 
ripped off :)
