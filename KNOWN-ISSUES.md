# Known Issues

This document describes known limitations and issues with the Actions For Nautilus extension.

## Background Menu Flickering in Large Directories

### Description

When opening a folder containing many items (100+) and **immediately** clicking the "..." background menu in the Nautilus title bar, you may experience brief menu flickering or unresponsiveness for 1-2 seconds.

### Root Cause

This is due to Nautilus's internal behavior when scanning directory contents. When a directory is opened, Nautilus:

1. Begins scanning and indexing the directory contents
2. For each item encountered, queries all installed extensions via `get_background_items()`
3. Calls the extension repeatedly (100+ times) for the _same directory path_ (very likely a bug)
4. Processes each response, even if the menu content is identical
5. Updates the UI for each response

If you click the "..." menu while this scan is in progress, the extension correctly returns the appropriate menu items for each call. However, Nautilus's repeated UI updates during the scan create a visible flicker effect and temporary unresponsiveness.

### Why Standard Workarounds Don't Work

Several approaches were investigated to mitigate this issue:

- **Caching**: The extension already caches menu items efficiently. The menu is not rebuilt 100+ times, but Nautilus still processes each response.

- **Returning None/empty for subsequent calls**: This causes the menu to appear and then disappear, as Nautilus processes each response independently and updates the UI accordingly.

- **Returning the same object reference**: Nautilus does not recognize object identity and processes every response as if it were new.

- **Throttling responses**: Any approach that varies the response causes the menu to flicker between states.

The extension must return consistent menu items for every call, and Nautilus will process each one, triggering UI updates.

### Workarounds

#### Option 1: Wait Before Clicking (Recommended)

Wait 1-2 seconds after opening a large folder to allow Nautilus to complete its directory scan before clicking the "..." button. Once the scan completes, the background menu will function normally without flickering.

#### Option 2: Use Alternative Context Menu Access

Instead of clicking the "..." button in the title bar, you can:
- Right-click on empty space within the folder window
- Right-click on the folder itself from its parent directory

These methods do not trigger the same burst calling behavior.

### Impact

- **File context menus**: Not affected. Right-clicking on files/folders works normally.
- **Background menu after scan**: Not affected. The "..." menu works normally once directory scanning completes.
- **Small directories**: Not affected. Folders with fewer items scan quickly and don't exhibit noticeable flickering.
- **Functionality**: Not affected. All menu items work correctly; the issue is purely cosmetic/responsiveness during the scan period.

### Optimizations

The extension includes several optimizations to minimize the impact:

- **Optimized menu cache**: Uses dict-based O(1) lookup to make repeated menu builds as fast as possible
- **Conditional debug logging**: Avoids logging overhead when debug mode is disabled
- **Efficient menu construction**: Caches menu items to avoid rebuilding for repeated calls

These optimizations reduce the duration and severity of the flicker but cannot eliminate it entirely due to the Nautilus API design.

### Technical Details

For developers interested in the technical details:

The `get_background_items()` method of the `Nautilus.MenuProvider` interface is called by Nautilus during various UI operations, including directory scanning. According to the nautilus-python example code:

```python
# Current versions of Nautilus will throw a warning if get_background_items
# isn't present
def get_background_items(self, window, file):
    return None
```

This comment suggests the method is required, but doesn't document the call frequency. Testing reveals that during directory scans, the method is called once for each item being processed, all with the same directory path as the argument.

The extension cannot distinguish between "initial" calls that should return a menu and "repeated" calls that should be ignored, as all calls are identical from the API perspective. Furthermore, varying the response causes menu items to appear and disappear, creating a worse user experience than consistent responses.

### Status

This is considered a **limitation of the Nautilus MenuProvider API** rather than a bug in the extension. The extension's behavior is correct and consistent with the API design; the flickering is an unavoidable consequence of how Nautilus processes extension responses during directory scans.

### Future

If Nautilus's API is enhanced in the future to provide:
- A way to indicate "menu unchanged, use cached version"
- A signal to indicate directory scan completion
- Reduced calling frequency for `get_background_items()`

...then this issue could be fully resolved. Until then, the workarounds listed above are recommended.
