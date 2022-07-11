# Release 2022-07-11

* Large scale revision of terminology
  The development of the JSON Schema for the configuration file brought to light the very
  imprecise and confusing terminology that I had allowed to slip into the configuration,
  the code, and the documentation.
  
  In particular the word **item** was severely overloaded and used inconsistently.
  
  Consequently, this release breaks any previous configuration as follows:
  
  * the `items` array properties are renamed `actions`, 
  * the value of the `type` property for "actions" that define a command to be executed 
    (as opposed to a submenu) has been changed from `item` to `command`.
  
  I apologize if this causes any problems, but I think it's better to get it right at 
  this early stage rather than later when the extension has (hopefully) a larger install
  base.
  
  The code, documentation, JSON schema, and delivered configuration have been modified to 
  reflect these changes.

* The JSON schema for the config file has been heavily revised to work better with the
  [JSON Editor](https://json-editor.github.io/json-editor/) tooling with which I hope 
  to build a configuration editor. And it's more "canonical" too.