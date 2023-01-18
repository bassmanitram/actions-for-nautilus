IMPL = "xclip" # or "gtk"

if IMPL == "gtk":
	import gi

	gi.require_version("Gtk", "3.0")
	from gi.repository import Gtk, Gdk

	global _gtk_clipboard
	_gtk_clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
else:
	import os

def _get_from_gtk_clipboard():
	return _gtk_clipboard.wait_for_text()

def _get_from_xclip():
	try:
		paste_str = os.popen('xclip -out').read()
		return "AFN_CLIPBOARD_NOT_STRING" if not isinstance(paste_str, str) else paste_str
	except Exception as error:
		print("Clipboard load error", error)
		return "AFN_CLIPBOARD_UNREADABLE"

def get_from_clipboard():
	if IMPL == "gtk":
		return _get_from_gtk_clipboard()
	else:
		return _get_from_xclip()
