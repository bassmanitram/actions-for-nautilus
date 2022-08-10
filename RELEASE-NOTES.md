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
