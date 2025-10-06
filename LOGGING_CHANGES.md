# Logging Implementation Changes

## Summary
Replaced all `print()` statements with proper Python logging throughout the Actions for Nautilus extension. Logging level is now controlled by the `debug` flag in the JSON configuration file.

## Changes Made

### 1. **actions_for_nautilus.py**
- Added logging import and setup function
- Replaced debug `print()` statements with `logger.debug()`
- Added `update_logging_level()` function to dynamically adjust logging based on config
- Logging level defaults to WARNING in production, DEBUG when config `debug: true`

### 2. **afn_config.py**
- Added logging import
- Replaced all `print()` statements with appropriate log levels:
  - `logger.info()` for config reload messages
  - `logger.warning()` for ignored/invalid config entries
  - `logger.error()` for config load failures and compilation errors
  - `logger.debug()` for debug information
- Used `exc_info=True` for better exception logging
- Added structured logging with `extra` parameter for config validation errors
- **Added dynamic logging level updates**: When config is reloaded and `debug` flag changes, logging level is automatically updated

### 3. **afn_menu.py**
- Added logging import
- Replaced error `print()` statements with `logger.error()`
- Replaced debug `print()` statements with `logger.debug()`
- Converted commented debug prints to proper logger calls

### 4. **afn_shell_tools.py**
- Added logging import  
- Replaced all `print()` statements in main() function with `logger.debug()`
- This affects the test/demo functionality

### 5. **debug_print() function preserved**
- The existing `debug_print()` function in afn_config.py now uses `logger.debug()` internally
- This maintains backward compatibility with existing code that calls `debug_print()`

## Key Feature: Config-Controlled Logging

The logging level is now controlled by the `debug` flag in the JSON configuration:

```json
{
  "debug": true,
  "actions": [...]
}
```

- When `debug: true` → Logging level set to DEBUG (verbose output)
- When `debug: false` or omitted → Logging level set to WARNING (minimal output)
- **Dynamic updates**: Changing the debug flag and saving the config automatically updates the logging level within 30 seconds (config reload interval)

## Benefits

1. **User-Controlled**: Debug logging controlled via familiar JSON config file
2. **Dynamic**: No need to restart Nautilus - logging level updates on config reload
3. **Production Ready**: No unwanted output when debug is disabled
4. **Structured**: Consistent logging format across all modules
5. **Maintainable**: Centralized logging configuration
6. **Performance**: Logging calls are efficient and don't impact performance when disabled

## Usage

### Enable Debug Logging
Edit your config file at `~/.local/share/actions-for-nautilus/config.json`:

```json
{
  "debug": true,
  "actions": [
    ...
  ]
}
```

Save the file and debug logging will be enabled within 30 seconds.

### Disable Debug Logging
Change the config to:

```json
{
  "debug": false,
  "actions": [
    ...
  ]
}
```

### View Logs
Debug and error messages will appear in the terminal where Nautilus was started, or in system logs.

## Backward Compatibility

- All existing functionality preserved
- `debug_print()` function still works (now uses proper logging internally)
- Config file `debug` flag behavior unchanged - still controls debug output
- No changes to external APIs or config format required
- Existing config files without `debug` flag default to non-debug mode

## Implementation Details

- Logging setup occurs once during module initialization
- `update_logging_level()` function called whenever config `debug` flag changes
- All modules use the same logger name (`actions_for_nautilus`) for consistent control
- Circular import avoided by importing `update_logging_level` function when needed