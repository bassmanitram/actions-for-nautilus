# Planned enhancements

* Add `min_items` configuration property to specify the minimum number of selection items for an action 
  (DONE: in version 1.3.0)
* Add JSON source editor to configurator ([in progress](https://github.com/bassmanitram/actions-for-nautilus/pull/20))
* Allow filtering on file permissions, ownership etc
* Allow filtering based upon a script
* Lift "labels must be unique" restriction - then different versions of the same action can appear
  based upon different filtering
* Add "all files must match the same pattern" condition (e.g. a command applies to three different file types,
  but on a particular selection, all selected files must match the same one of those file types)
* Enhance mimetype filtering to allow more specific rules to override more general rules
* Add backup config management to the configurator
* Add ability to specify the default shell to use for commands that have `use_shell` specified
* ...
