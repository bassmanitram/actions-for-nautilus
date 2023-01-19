#
# I have two implementations because the original used xclip and I wanted
# to preserve that in the sources as the "reference" for semantics while
# we shake out the feature in general.
#
# However, there really isn't a need for a user switch between the GTK 
# implementation and the xclip implementation - if GTK is proved to be
# entirely consistent it will be the actual implementation, avoiding a 
# dependency on xclip (even though that remains a recommended additional
# tool.
#
IMPL = "gtk" # "gtk" or "xclip"

if IMPL == "gtk":
	import gi

	gi.require_version("Gtk", "3.0")
	from gi.repository import Gtk, Gdk

	global _gtk_clipboard
	_gtk_clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
	global _gtk_selection
	_gtk_selection = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
else:
	import os

def _get_from_gtk_clipboard(clipboard):
	return clipboard.wait_for_text()

def _get_from_xclip(clipboard):
	try:
		paste_str = os.popen(f"xclip -out -selection {clipboard}").read()
		return "" if not isinstance(paste_str, str) else paste_str
	except Exception as error:
		print("Clipboard load error", error)
		return ""

def get_from_clipboard():
	if IMPL == "gtk":
		return _get_from_gtk_clipboard(_gtk_clipboard)
	else:
		return _get_from_xclip("XA_CLIPBOARD")

def get_from_selection():
	if IMPL == "gtk":
		return _get_from_gtk_clipboard(_gtk_selection)
	else:
		return _get_from_xclip("XA_PRIMARY")
