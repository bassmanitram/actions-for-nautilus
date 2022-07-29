# The Config Editor
Firstly, if you simply want to edit the config file using the installed 
"application", then you don't need to read this - just navigate to
your system's "Applications" menu/panel/whatever, find 
**Actions For Nautilus Configurator**, click on it, and you'll be
presented with a web-based configuration tool - which I ASSURE you makes
no external server calls whatsoever.

If, on the other hand, you want to know why on earth this _is_ a 
web-based UI, then read on.

## The rationale
The config file is a JSON file the structure of which that very closely 
follows the model that it describes - a recursive set of "objects" that 
represent submenus and their component "actionable" items.

A tree, if you like.

And that configuration has a detailed canonical JSON Schema describing it.

Now, I COULD have built a GTK-based UI from scratch and become highly
frustrated with all little details necessary to make configuring
this tiny extension pleasant for you.

Basically a glorified JSON file editor!

I am most CERTAINLY not a UI designer - it would have taken MONTHS to
to get to a usable state, would have been a real time-suck
to maintain and fix, and you would have still hated it.

But back to the JSON Schema - that describes the config in perfect detail!

And JSON Schema is *ubiquitous* - SURELY *someone* has thought of building
a UI generator that gives you a JSON editor based upon a schema.

Well **YES** they have! But not as a desktop app! As a *web-based* app.

It is [JSON Editor](https://github.com/json-editor/json-editor) - and it's 
AWESOME!

But if you know about web development (and aside from the design of the UI
itself, I do) you know that you can't properly serve a web-based UI without
a web server...

So here we are!

## The configurator!
The configurator, then, consists of the following components:

* [The single-page HTML document](./actions-for-nautilus-configurator.html) that uses 
  [JSON Editor](https://github.com/json-editor/json-editor)
  to generate a (what I think is) beautiful UI based upon the config schema, with
  various customizations to make it easy to use in this context.

  All resources used by the UI are fetched from the _local_ http server, _NOT_
  from a public server (your privacy is protected).

  When you *close* the configurator page, it automatically stops the local server.

* [A TINY backend HTTP server](./actions-for-nautilus-configurator.py), that serves 
  the page, any existing config, and the schema, and can save the updated config 
  on demand from the UI.
  
  It is terminated when you close the configurator web page.

* [A shell script](./start-configurator.sh) that kills any existing copy of the server, 
  starts the server, then uses `xdg-open` to open the page in your system default 
  browser.
  
* [A Desktop file](./actions-for-nautilus-configurator.desktop) that gets installed into 
  your local Applications repository, and launches the afore-mentioned startup script 
  when you "open" that application.

This all works like a dream - for me. So I'm sticking with it.

If someone wants to take a shot at designing a "real" desktop configurator, go ahead -
If you do, though, *please* make it a generic JSON Schema-based JSON editor :) 
