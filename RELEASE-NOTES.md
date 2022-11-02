# Release 1.5.1
* Fix sorting of submenu items
  The **Submenu sorting** option was not being correctly interpreted or defaulted.
  
# Release 1.5.0
* Implemented the `permissions` property to optionally require the
  user to have specific access permissions for the selected files.
  
# Release 1.4.1
* Fix config corruption by the configurator, caused by consistency checks for `min_items` and `max_items`
  
  The internal checks necessary to ensure consistency between the `min_items` and `max_items`
  properties were causing various corruptions to the extension configuration when items were
  moved and/or deleted in the configurator.

  For more details see https://github.com/bassmanitram/actions-for-nautilus/issues/23

# Release 1.4.0
* Added a syntax-checking JSON source editor
  
  The editor can be toggled using the new `JSON` button. Changes within this editor
  are copied back to the main UI upon `Save`.

# Release 1.3.0
* Fixed [issue with `%f` interpolation when multiple files are selected](https://github.com/bassmanitram/actions-for-nautilus/issues/17).

* Implemented the `min_items` property. The semantics are pretty straightforward:
  
  * `max_items` is now formally defaulted to zero internally, that being interpreted as unlimited.
  * `min_items` defaults to 1 and has a minimum value of 1.
  * If `max_items` is greater than zero, then `min_items` must be less than or equal to `max_items`.

* Improved configurator layout and styling (well, I think so :)). This results in having _two_ JSON schemas:

  * [one that describes the configuration file used by the extension itself](configurator/actions-for-nautilus.schema.json),
  * [a slightly different one that describes the configuration information within the configurator](configurator/actions-for-nautilus.ui.schema.json).

  Consequently, the configurator now performs model transformations when reading and writing the extension configuration.

* Fixed a small issue with the "copy" actions in the sample configuration whereby a "newline" was included
  at the end of the information written to the clipboard.

# Release 1.2.0
* In-window, hideable, contextual help
  The configurator is now an iframe in a container window that also
  contains a "help" iframe. 

  All "i" tooltip buttons can now be clicked and will open the help
  iframe at the appropriate part of the (now complete) help HTML page.
  
  The two iframes are resizable using a drag bar.

  There is also a show-help/hide-help button.

# Release 1.1.1
* Fix mimetype, file type, and path pattern rule evaluation.
* Fix syslog errors when virtual locations (Trash, Recent, ...) are
  in the selection

# Release 1.1.0
* Add `path_patterns` to command action configurations. This allows
  selected files to be matched against path patterns to establish if 
  the command should appear in the menu.

  Glob and Regular Expressions syntaxes are supported, as is pattern
  negation.

# Release 1.0.2

* Debian package fixes 
  Various changes that pertain to getting the Debian package past the
  Lintian tool and Gdebi installation problems.

  The one remaining issue is a warning that the copyright file doesn't
  contain a copyright notice. It does - it's modeled on many other similar
  files so I'm pretty confident it's correct.

  It IS just a warning, so Gdebi should now be fine (I did a Gdebi install
  to test that).

* Removal of external dependencies
  The one functional thing that the Debian package "purification" entailed was
  removing the external library dependencies from the configurator web app - these
  are now delivered with this package, or (better still) provided by Debian
  packages that are now listed as dependencies.

  This, of course, improves the privacy posture of the extension.

  PR: https://github.com/bassmanitram/actions-for-nautilus/pull/7

# Release 1.0.1

* Fixed `python` references in the config startup script to be `python3`.
  These were missed in the original "use python3" mod.
  
  PR: https://github.com/bassmanitram/actions-for-nautilus/pull/3
  Thanks to @Nova1545 for spotting this.
