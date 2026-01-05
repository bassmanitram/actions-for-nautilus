# Actions For Nautilus - Agent Bootstrap

**Purpose**: Extends Gnome Files (Nautilus) with user-defined context menu actions for file operations  
**Type**: Desktop Extension + Configuration Utility  
**Language**: Python 3.10+  
**Repository**: https://github.com/bassmanitram/actions-for-nautilus  
**Current Version**: 2.0.0 (v2 branch)

---

## What You Need to Know

**This is**: A Gnome Nautilus extension that replaces the defunct nautilus-actions project. Users add custom commands to the Nautilus right-click context menu, filtered by file type, mimetype, path patterns, permissions, and even external program validation. Configuration is managed through a browser-based JSON editor (forked and enhanced from json-editor project) running as a local HTTP server.

**Architecture in one sentence**: Nautilus Python extension loads JSON config → parses config into action objects → filters actions based on file selection → builds dynamic context menus → tokenizes command lines → expands placeholders → executes shell commands with proper escaping.

**The ONE constraint that must not be violated**: Placeholder expansion behavior (SINGULAR vs PLURAL) is determined by the first placeholder with defined behavior in the command line - this is inherited from nautilus-actions for backward compatibility and cannot change without breaking existing user configs.

---

## Mental Model

- The extension is split into **two independent processes**: the **Nautilus extension** (passive menu provider) and the **configurator** (browser-based config editor via HTTP server)
- Configuration is **pull-based** with **polling**: extension watches `~/.local/share/actions-for-nautilus/config.json` for mtime changes every 30 seconds and reloads automatically
- Actions form a **recursive tree**: menus contain actions (commands or more menus), evaluated top-down with early filtering
- Command execution is **context-driven**: each command declares filters (mimetype, filetype, path patterns, permissions, item counts, external program) that determine visibility
- **V2 enhancement**: Placeholder expansion has two modes:
  - **V1 interpolation** (legacy): Single-pass string substitution with basic escaping
  - **V2 interpolation** (default): Tokenize-then-expand with context-aware escaping based on quote delimiters
- Tokenization is **execution-aware**: separate tokenization for `use_shell: true` (preserves shell constructs) vs `use_shell: false` (strict argument parsing)
- The configurator is **fire-and-forget**: starts HTTP server on 127.0.0.1, opens browser, terminates when tab closes

---

## Codebase Organization

```
root/
├── extensions/                          # Nautilus extension implementation
│   ├── actions-for-nautilus.py          # Entry point symlink
│   └── actions-for-nautilus/            # Extension module (installed to ~/.local/share/nautilus-python/extensions/)
│       ├── actions_for_nautilus.py      # Main: logging setup, MenuProvider interface
│       ├── afn_config.py                # Config loading, validation, file watching, action objects
│       ├── afn_menu.py                  # Menu construction, filtering logic, permission caching
│       ├── afn_place_holders.py         # Placeholder expansion, behavior detection, plural caching
│       └── afn_shell_tools.py           # V2: Tokenization (shell/native), improved interpolation
├── configurator/                        # Browser-based configuration UI
│   ├── actions-for-nautilus-configurator.py  # HTTP server serving the UI
│   ├── start-configurator.sh            # Desktop launcher (finds free port, opens browser)
│   ├── find-a-port.py                   # Utility to find available port
│   ├── *.html                          # Web UI pages (container, main editor, help)
│   ├── actions-for-nautilus.schema.json # JSON schema for extension config (canonical)
│   ├── actions-for-nautilus.ui.schema.json # JSON schema for UI (adds presentation metadata)
│   ├── css/, javascript/, images/      # Web UI assets
│   ├── javascript/jsoneditor.js        # Forked json-editor with custom enhancements
│   └── sample-config.json              # Installed on first launch if no config exists
├── dist/                               # Debian packages (generated, gitignored)
├── packaging/                          # Debian package metadata
│   ├── DEBIAN/control                  # Package control file with $VERSION placeholder
│   └── doc/actions-for-nautilus/       # Debian documentation
│       ├── changelog                   # Debian changelog format (RFC 2822 dates)
│       └── copyright                   # License information
├── local/                              # Development backups (gitignored)
├── Makefile                            # Installation/uninstallation/package-building (VERSION variable)
├── RELEASE-NOTES.md                    # User-facing release notes (markdown format)
└── TO-DO.md                            # Planned enhancements
```

**Navigation Guide**:

| When you need to... | Start here | Why |
|---------------------|------------|-----|
| Understand menu construction | `afn_menu.py::create_menu_items()` | Entry point for menu building, calls filtering |
| Understand filter evaluation | `afn_menu.py::_passes_all_filters()` | Orchestrates mimetype/filetype/path/permission/show-if-true checks |
| Understand V2 tokenization | `afn_shell_tools.py::tokenize_for_shell()`, `tokenize_for_native()` | Quote-aware parsing for improved escaping |
| Understand placeholder expansion | `afn_place_holders.py::expand()` | Replaces `%f`, `%F`, etc. with file properties |
| Understand V2 interpolation | `afn_shell_tools.py::resolve2()` | Tokenize-then-expand with context-aware escaping |
| Understand command execution | `actions_for_nautilus.py::_run_command()` | Determines SINGULAR vs PLURAL, calls interpolation |
| Understand config loading | `afn_config.py::ActionsForNautilusConfig.__init__()` | Loads JSON, validates, creates action objects |
| Understand config validation | `afn_config.py::_check_command_action()` | Validates and normalizes command actions |
| Debug extension behavior | Enable `"debug": true` in config.json, run `nautilus --no-desktop` | Extension logs to stdout via Python logging |
| Update version for release | `Makefile` (VERSION variable), `RELEASE-NOTES.md`, `packaging/doc/actions-for-nautilus/changelog` | See "Version Bump Procedure" below |

**Entry points**:
- Nautilus extension: `extensions/actions-for-nautilus.py` (symlink) → `actions_for_nautilus.py`
- Configurator: `configurator/start-configurator.sh` → `actions-for-nautilus-configurator.py`
- Tests: None currently exist (opportunity for improvement)
- Configuration: `~/.local/share/actions-for-nautilus/config.json` - user-editable JSON

---

## Critical Invariants

These rules MUST be maintained:

1. **Placeholder behavior determined by first SINGULAR/PLURAL placeholder**: Command execution mode (once vs once-per-file) is determined by scanning command_line left-to-right for first placeholder with `behavior` of `SINGULAR` or `PLURAL`. Placeholders with `behavior: -1` (like `%c`, `%h`) are skipped.
   - **Why**: Compatibility with original nautilus-actions. Users expect this and existing configs depend on it.
   - **Breaks if violated**: Commands execute wrong number of times. `echo %B %f` runs once (correct), `echo %f %B` runs once per file (correct). Changing this breaks both.
   - **Enforced by**: `afn_place_holders.py::get_behavior()` scans; `actions_for_nautilus.py::_run_command()` uses result for loop count

2. **Config file changes detected within 30 seconds**: Extension uses `GLib.timeout_add_seconds(30, ...)` to poll for config file mtime changes. Ensures users see changes without restarting Nautilus.
   - **Why**: Nautilus extensions can't cleanly reload themselves. Inotify unreliable in Nautilus's thread model.
   - **Breaks if violated**: Config changes require manual `nautilus -q`, degrading UX.
   - **Enforced by**: `afn_config.py::ActionsForNautilusConfig.__init__()` sets up timer; `_check_config_change()` compares mtimes

3. **Filter rules split into positive and negative lists**: Each filter type (mimetypes, filetypes, path_patterns) normalized into `{"p_rules": [...], "n_rules": [...]}` where p_rules are non-negated, n_rules are negated (`!` prefix).
   - **Why**: Evaluation: "match at least one p_rule (if any) AND match zero n_rules". Splitting at load time avoids re-parsing `!` on every menu construction.
   - **Breaks if violated**: Filter evaluation becomes O(n²) instead of O(n), causing UI lag on large selections.
   - **Enforced by**: `afn_config.py::_check_command_action()` calls `_split_rules()` during validation

4. **Configurator binds to 127.0.0.1 only**: HTTP server MUST use `http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ...)`, never `""` or `"0.0.0.0"`.
   - **Why**: Security vulnerability (fixed in v1.6.1). Binding to all interfaces exposes config server to network attackers.
   - **Breaks if violated**: Network attackers can modify Nautilus config, execute arbitrary commands.
   - **Enforced by**: Code review (v1.6.1 fix maintained in v2)

5. **Plural cache must be reused within execution context**: `PluralCache` object passed through `resolve()` and `resolve2()` must be reused for all placeholders in same command execution to avoid redundant array builds.
   - **Why**: Plural placeholders (`%B`, `%F`, etc.) build arrays from all files. Without caching, each plural placeholder rebuilds same array.
   - **Breaks if violated**: Performance degradation on large selections (O(n) becomes O(n*m) where m = number of plural placeholders).
   - **Enforced by**: `actions_for_nautilus.py::_run_command()` creates cache once, passes to interpolation functions

6. **V2 tokenization must preserve shell constructs when use_shell=true**: `tokenize_for_shell()` must NOT consume shell operators (`|`, `;`, `&`, `<`, `>`, `()`) as they need to be passed to shell.
   - **Why**: V2's main feature is better shell command handling (pipelines, redirects, command substitution).
   - **Breaks if violated**: Commands like `ls %f | grep foo` would fail - pipe operator consumed during tokenization.
   - **Enforced by**: `afn_shell_tools.py::tokenize_for_shell()` treats shell operators as `Handle.NO_HANDLE` tokens

---

## Non-Obvious Behaviors & Gotchas

Things that surprise people:

1. **V2 interpolation is opt-out, not opt-in**:
   - **Default**: `use_v1_interpolation` defaults to `False` - V2 tokenization is used
   - **Why**: V2 fixes escaping issues, handles quotes better. V1 mode exists only for edge-case compatibility.
   - **Watch out for**: Commands that worked in V1 might break if they relied on V1's quirky escaping. Add `"use_v1_interpolation": true` to revert.
   - **Correct approach**: Test configs on v2, only use V1 mode for problematic commands, report issues so V2 can be improved

2. **Escaping behavior differs between shell and native execution**:
   - **use_shell: false**: Arguments are list `["cmd", "arg1", "arg2"]`, escaping is backslash removal from shlex tokens
   - **use_shell: true**: Command is string `"cmd arg1 arg2"`, escaping depends on quote context:
     - Single quotes: No escaping (`'$VAR'` stays literal)
     - Double quotes: Escape `\`, `` ` ``, `$`, `"` (`RAW_ESCAPE_RE`)
     - No quotes: Escape all shell special chars including space, tab, newline, etc.
   - **Common mistake**: Using same command for both modes and expecting identical behavior
   - **Correct approach**: Design commands for their execution mode. Use `use_shell: true` for pipelines/loops, `false` for simple commands with exact argument control.

3. **Permission caching has 5-second expiry (V2 optimization)**:
   - **Why**: `os.access()` filesystem call is expensive. Lazy caching reduces redundant checks during menu construction.
   - **Cache key**: `f"{filepath}:{permission_flags}"` - file path + permission type
   - **Expiry**: 5 seconds via timestamp check
   - **Watch out for**: If file permissions change during menu construction (rare), cache might be stale for up to 5 seconds.
   - **Correct approach**: This is acceptable - menu construction happens in <1 second typically. Cache prevents O(n*m) permission checks where n=files, m=actions.

4. **Menu visibility depends on ALL child commands passing filters**:
   - **Why**: Empty menus confuse users. If menu has 5 commands but all filtered out, menu itself is hidden.
   - **Watch out for**: Menu with broad filters (e.g., `mimetypes: ["*"]`) but all commands with narrow filters (e.g., `["image/*"]`) invisible for non-image selections.
   - **Correct approach**: Design menu filters as union of child filters, or accept menus may not always appear.

5. **show_if_true program must exit 0 for action to appear**:
   - **V2 feature**: External program determines action applicability
   - **Behavior**: Program receives selection via environment variables, exits 0 (success) = show action, non-zero = hide action
   - **Watch out for**: Program errors/crashes = non-zero exit = action hidden. No user notification of failure.
   - **Correct approach**: Test show_if_true programs thoroughly, ensure they handle all edge cases gracefully

6. **Plural placeholders in SINGULAR mode only expand for current file**:
   - **Example**: Command `echo %f %B` with 3 files selected
     - Behavior: SINGULAR (because `%f` comes first)
     - Iteration 1: `echo file1 file1` (not `echo file1 file1 file2 file3`)
     - Iteration 2: `echo file2 file2`
     - Iteration 3: `echo file3 file3`
   - **Why**: V2's plural cache optimization - when index is passed, cache returns only that index's value
   - **Watch out for**: Expecting plural placeholders to always expand to all files. They don't in SINGULAR mode.
   - **Correct approach**: Understand placeholder behavior, use `%O` to force PLURAL if needed

7. **Tokenization handles quotes but doesn't remove them**:
   - **V2 behavior**: `tokenize_for_shell("echo '%f'")` produces `[("echo", NO_HANDLE), ("'%f'", SINGULAR)]`
   - **Quotes preserved**: Shell needs them to determine grouping
   - **Escaping applied**: Based on outer quote type (none, single, double)
   - **Watch out for**: Thinking quotes are removed during tokenization. They're not - shell processes them.
   - **Correct approach**: Let tokenization preserve quotes, escaping function adapts based on quote context

---

## Architecture Decisions

**Why two interpolation modes (V1 and V2)?**
- **Trade-off**: V2 fixes escaping bugs but changes behavior slightly. V1 mode preserves exact legacy behavior for edge cases.
- **Alternative considered**: Break compatibility, force V2 for everyone. Rejected because some users have complex configs that might break.
- **Implications**: Dual code paths increase complexity. Default is V2 (opt-out), minimizing V1 maintenance burden. V1 will eventually be deprecated.

**Why tokenize before placeholder expansion?**
- **Trade-off**: Tokenization first allows context-aware escaping (different rules inside quotes vs outside). Expansion first (V1) requires uniform escaping, causing bugs with special chars.
- **Alternative considered**: Keep V1 approach, document escaping quirks. Rejected after user reports of quote/special char issues (#53, #63).
- **Implications**: Tokenization adds complexity but solves entire class of escaping bugs. Performance impact negligible (tokenization is O(n) string scan).

**Why lazy permission caching?**
- **Trade-off**: Caching reduces filesystem calls but adds 5-second staleness window. Acceptable because permissions rarely change during browsing, and 5s is short enough for UX.
- **Alternative considered**: No caching (check every time). Rejected due to performance - `os.access()` is expensive, menu construction with 100 files + 10 permission-filtered actions = 1000 calls.
- **Implications**: ~10x speedup on permission-heavy configs. Cache expires quickly to handle permission changes. Cache only created when permission filter actually used.

**Why fork json-editor instead of contributing upstream?**
- **Trade-off**: Forking gives control over features/fixes but creates maintenance burden. Contributing upstream is cleaner but slower.
- **Alternative considered**: Wait for upstream PRs to merge. Rejected because response time is months, blocking v2 release.
- **Implications**: Maintain fork with custom enhancements (copy/paste, drag/drop). Submit PRs to upstream when possible. Document fork URL in README.

**Why Python logging instead of print statements?**
- **Trade-off**: Logging module adds ~50 lines setup code but provides log levels, structured output, handler management.
- **Alternative considered**: Keep print statements. Rejected because no way to control verbosity, mixing stdout/stderr inconsistently.
- **Implications**: Professional logging, controllable via `debug` flag. Easier to troubleshoot issues. Requires `nautilus --no-desktop` to see output (unchanged).

**Why 30-second config poll interval?**
- **Trade-off**: Shorter = faster config reload but more CPU. Longer = less responsive.
- **Alternative considered**: Inotify file watching. Rejected - unreliable in Nautilus's thread model (tested, caused race conditions).
- **Implications**: 30s delay acceptable - users save config, wait ~30s, see changes. Alternative (restart Nautilus) is worse. Low CPU impact (one mtime check every 30s).

---

## Key Patterns & Abstractions

**Pattern 1: Config Validation and Normalization Pipeline**
- **Used for**: Transforming JSON into optimized runtime objects (`CommandAction`, `MenuAction`)
- **Structure**: 
  1. `_check_action()` dispatches by `type` field
  2. `_check_menu_action()` or `_check_command_action()` validates required fields
  3. Normalizers generate optimized filters (split positive/negative, compile regexes)
  4. Add runtime metadata (`idString`, `cmd_is_plural`, tokenized `command_line_parts`)
  5. Return action object or `None` (filtered out)
- **Examples**: `afn_config.py::_check_command_action()` generates `{"mimetypes": {"p_rules": [...], "n_rules": [...]}}` from `["text/*", "!text/plain"]`
- **Why this way**: Optimization moves to load time, not menu construction time. Invalid configs caught early with clear errors.

**Pattern 2: Recursive Menu Construction with Early Filtering**
- **Used for**: Building Nautilus menu hierarchies while pruning irrelevant branches
- **Structure**:
  1. `create_menu_items()` → `_create_menu_item()` (dispatcher)
  2. Dispatch to `_create_submenu_menu_item()` (recursive) or `_create_command_menu_item()` (leaf)
  3. Each level filters actions via `_passes_all_filters()`, returns `None` for filtered-out
  4. Submenus with no visible children are pruned (return `None`)
  5. Remaining items sorted if `sort: auto`, returned as list
- **Why not build everything then filter**: Constructing `Nautilus.MenuItem` objects is expensive. Early filtering avoids creating objects that will be discarded. ~5x speedup on configs with heavy filtering.

**Pattern 3: Tokenize-Then-Expand with Context-Aware Escaping (V2)**
- **Used for**: Correct placeholder expansion in quoted contexts
- **Structure**:
  1. Tokenization: `tokenize_for_shell()` or `tokenize_for_native()` → list of `(token, Handle)` tuples
  2. Classification: Each token classified as `NO_HANDLE` (literal), `SINGULAR` (per-file placeholder), `PLURAL` (all-files placeholder)
  3. Expansion: `resolve2()` iterates tokens, calls `expand()` on SINGULAR/PLURAL tokens
  4. Context escaping: Escaping function (`_improved_escape`) selected based on token's outer quote type
  5. Reconstruction: Tokens joined for shell or returned as array for native
- **Examples**: 
  - Input: `"echo '%f' | grep pattern"`
  - Tokens: `[("echo", NO_HANDLE), ("'%f'", SINGULAR), ("|", NO_HANDLE), ("grep", NO_HANDLE), ("pattern", NO_HANDLE)]`
  - Expansion: `'%f'` → `'file name.txt'` (single quote = no escaping)
  - Output: `"echo 'file name.txt' | grep pattern"`
- **Why this way**: Solves entire class of quote/special-char bugs. Tokenization understands shell syntax, expansion doesn't need to.

**Pattern 4: Plural Cache with Lazy Array Building**
- **Used for**: Avoiding redundant array building for plural placeholders
- **Structure**:
  1. `PluralCache` object created once per command execution
  2. First `%B` expansion: builds `cache.B = [file["basename"] for file in files]`, returns it
  3. Subsequent `%B` expansions: returns cached `cache.B`
  4. SINGULAR mode override: `_expand_percent_B_array(files, cache, index=i)` returns `[cache.B[i]]` instead of full array
- **Why cache per execution**: Same command line resolved multiple times in SINGULAR mode. Without cache, each iteration rebuilds all plural arrays. With cache, build once, reuse.
- **Performance impact**: O(n*m*p) → O(n*m + p) where n=files, m=iterations, p=plural placeholders. For 10 files, 10 iterations, 3 plurals: 300 builds → 13 builds.

**Pattern 5: Lazy Permission Caching with Timestamp Expiry (V2 optimization)**
- **Used for**: Reducing filesystem calls during menu construction
- **Structure**:
  1. Global cache `{cache_key: bool}` and `cache_timestamp`
  2. On permission check: compare current time to `cache_timestamp`, clear cache if >5s old
  3. Check cache for `f"{filepath}:{permission_flags}"`
  4. On miss: call `os.access()`, store result, return
  5. On hit: return cached result
- **Why lazy**: Only caches when permission filter actually used. Most configs don't use permissions, no cache overhead.
- **Why 5-second expiry**: Balances cache hit rate vs staleness. Permissions change rarely during browsing. 5s is short enough to catch changes within single browsing session.

**Anti-pattern to avoid: Storing mutable state in action objects**
- **Don't do this**: Add runtime state (like "last execution time") to `CommandAction` or `MenuAction` objects
- **Why it fails**: Action objects are loaded once, shared across all menu constructions. Multiple threads may access simultaneously. State would be unreliable.
- **Instead**: Commands are stateless, derive all context from file selection. Use filesystem (`/tmp`, `~/.cache/`) if commands need to communicate state between invocations.

---

## State & Data Flow

**State management**:
- **Persistent state**:
  - User config: `~/.local/share/actions-for-nautilus/config.json` (user-editable JSON)
  - Config backups: `~/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json_MMM-DD-YY-HH:MM:SS` (auto-created by configurator on save)
- **Runtime state**:
  - Parsed config: `ActionsForNautilusConfig.actions` (list of action objects, reloaded every 30s if mtime changes)
  - Config mtime: `ActionsForNautilusConfig.mtime` (used to detect changes)
  - Menu cache: `afn_menu.menu_cache` (maps config mtime → menu items, invalidated on config change)
  - Permission cache: `afn_menu._permission_cache` (maps `filepath:flags` → bool, 5s expiry)
  - Plural cache: `PluralCache` instance (created per command execution, not persisted)
- **No state here**: Command execution is fire-and-forget via `subprocess.Popen()`. No tracking of running commands. No IPC between configurator and extension.

**Data flow**:
```
User edits config in browser → HTTP POST to configurator → writes JSON to disk → backup old config
                                                                 ↓
Extension polls every 30s → detects mtime change → calls update_config()
                                                                 ↓
JSON loaded → validated → normalized → action objects created → stored in ActionsForNautilusConfig.actions
                                                                 ↓
User right-clicks file(s) in Nautilus → Nautilus calls get_file_items()
                                                                 ↓
Extract file properties (path, basename, mimetype, uri, etc.) → create list of file dicts
                                                                 ↓
create_menu_items() → iterate actions → _passes_all_filters() for each action
                                                                 ↓
Filter evaluation: mimetypes → filetypes → path_patterns → permissions → show_if_true → item count
                                                                 ↓
Filtered actions → recursive menu construction → return Nautilus.MenuItem list
                                                                 ↓
User clicks menu item → activate signal → _run_command()
                                                                 ↓
Determine behavior (SINGULAR/PLURAL) → loop file_index 0..count-1
                                                                 ↓
For each iteration: resolve cwd → tokenize command (or use V1) → expand placeholders → escape based on context
                                                                 ↓
Execute: subprocess.Popen(final_command_line, cwd=cwd, shell=use_shell)
```

**Critical paths**: Config validation → menu construction → placeholder expansion → command execution. Exceptions in these paths cause actions to disappear or commands to fail silently.

---

## Integration Points

**This project depends on** (upstream):
- **nautilus-python** (tight coupling): Provides `Nautilus.MenuProvider` interface, `Nautilus.MenuItem`/`Nautilus.Menu` objects. V2 maintains v1.6.0 compatibility with both nautilus-python v3 and v4 APIs.
- **python3-gi / GObject introspection** (tight coupling): Provides `Gio` (file types, URIs), `GLib` (timers, main loop). Core to Nautilus integration.
- **json-editor** (loose coupling): V2 uses forked version (https://github.com/bassmanitram/json-editor) with custom enhancements (copy/paste, drag/drop). Could be replaced but requires UI rewrite.
- **ACE editor** (loose coupling): Used for JSON source editing in configurator. Easily replaceable.
- **Bootstrap, jQuery** (loose coupling): UI framework for configurator. Updated to latest versions in v2.

**Projects that depend on this** (downstream):
- **End users** (user-facing): Breaking config schema requires migration path. V2 maintains backward compatibility with v1 configs.
- **Wiki examples** (community): Community configs at https://github.com/bassmanitram/actions-for-nautilus/wiki. Schema changes break shared examples.

**Related projects** (siblings):
- **nautilus-actions / filemanager-actions** (defunct): Spiritual predecessor. V2 maintains placeholder compatibility but doesn't share code. Original was C-based, this is Python.
- **nautilus-copy-path**: Simpler extension, inspired original POC.

---

## Configuration Philosophy

**What's configurable**: Everything about menu structure and command execution:
- Action labels, command lines, cwd, use_shell
- Filtering rules: mimetypes, filetypes, path_patterns, permissions, min/max items, show_if_true
- Menu sorting (manual/auto)
- Debug mode
- V2: Interpolation mode (`use_v1_interpolation`), strict-match modes for filters, disabled flag

**What's hardcoded**:
- Placeholder expansion semantics (SINGULAR/PLURAL behavior, character meanings) - changing breaks compatibility
- Config file location (`~/.local/share/actions-for-nautilus/config.json`) - hardcoded for discovery by both extension and configurator
- File watch interval (30 seconds) - hardcoded in `GLib.timeout_add_seconds(30, ...)`
- Configurator bind address (127.0.0.1) - security requirement
- Permission cache expiry (5 seconds) - performance tuning

**Configuration sources** (precedence order):
1. User config file (`~/.local/share/actions-for-nautilus/config.json`) - if exists, used exclusively
2. Sample config (installed by configurator on first launch) - only if user config doesn't exist

**The trap**: Debug flag enables verbose logging but requires `nautilus --no-desktop` from terminal to see output. Users enable debug, don't see output in normal Nautilus, assume it's broken. Always mention this in troubleshooting docs.

---

## Testing Strategy

**What we test**:
- Manual testing during development
- Pre-release testing via community (v2.0.0~pre1-1, v2.0.0~pre2-1 published)

**What we don't test**:
- Unit tests - Why not: Extension tightly coupled to Nautilus/GObject, mocking complex
- Integration tests - Why not: Requires running Nautilus in CI, selecting files programmatically
- Schema validation - Handled by configurator's json-editor library, not directly tested

**Test organization**: N/A currently

**Mocking strategy**: N/A currently

**Opportunity for improvement**: Add unit tests for pure functions:
- Tokenization: `afn_shell_tools.tokenize_for_shell()`, `tokenize_for_native()`
- Placeholder expansion: `afn_place_holders.expand()`, `get_behavior()`
- Filter evaluation: `afn_menu._test_rule()`, `_applicable_to_*()` functions
- Config validation: `afn_config._gen_mimetype()`, `_gen_pattern()`, `_split_rules()`

These are pure functions (input → output, no side effects), easy to test without Nautilus.

---

## Common Problems & Diagnostic Paths

**Symptom**: Actions don't appear in context menu after installation
- **Most likely cause**: Config file doesn't exist or contains invalid JSON
- **Check**:
  1. Does `~/.local/share/actions-for-nautilus/config.json` exist? If not, run configurator to create it.
  2. Is JSON valid? `python3 -m json.tool ~/.local/share/actions-for-nautilus/config.json`
  3. Check Nautilus output: `nautilus -q`, then `nautilus --no-desktop` from terminal
- **Fix**: Run configurator, save config (even without changes) to create valid file. Check Nautilus output for validation errors.

**Symptom**: Actions don't appear for specific file selections
- **Most likely cause**: Filters excluding selection (mimetype, filetype, path_pattern, permissions, min/max items, show_if_true)
- **Check**:
  1. Enable `"debug": true` in config, run `nautilus --no-desktop`, right-click files. Extension prints filter evaluation.
  2. Check action's filters - do they match selected files?
  3. If using show_if_true: test program manually with same file selection
- **Fix**: Adjust filters. Common mistake: `["text/*", "!text/plain"]` means "text files except text/plain", not "include text/plain".

**Symptom**: Command executes wrong number of times or with wrong arguments
- **Most likely cause**: Placeholder behavior (SINGULAR vs PLURAL) misunderstood
- **Diagnostic**:
  1. What's first placeholder in command_line? `%f`/`%b`/`%d`/`%m`/`%u`/`%w`/`%x` = SINGULAR. `%F`/`%B`/`%D`/`%M`/`%U`/`%W`/`%X` = PLURAL.
  2. Enable debug mode, check "Count: X" in output
- **Solution**: Use PLURAL placeholders (`%F`, `%B`) for commands that run once. Use SINGULAR for per-file execution. Use `%O` to force PLURAL or `%o` to force SINGULAR.

**Symptom**: Special characters in filenames cause command failures (V2 should fix this)
- **Most likely cause**: Using V1 interpolation (`use_v1_interpolation: true`) or command designed for V1
- **Check**: Is `"use_v1_interpolation": true` in command config? Remove it to enable V2.
- **Fix**: V2's tokenization handles quotes and special chars correctly. Test without V1 mode. If still broken, report bug - V2 should handle all cases.

**Symptom**: Configurator won't start or shows blank page
- **Most likely cause**: Port conflict (service on 8000-8099) or missing dependencies (jquery, HTTP server)
- **Check**:
  1. Does `start-configurator.sh` output port? If not, `find-a-port.py` failing.
  2. Can access `http://127.0.0.1:<PORT>/` manually? If not, server not starting.
  3. Dependencies installed? `dpkg -l | grep libjs-jquery` (Debian) or equivalent.
- **Fix**: Kill processes using ports (`lsof -i :8000-8099`). Install dependencies (`sudo apt install libjs-jquery`).

**Symptom**: Config changes don't appear after saving
- **Most likely cause**: Waiting <30 seconds, or file watcher not detecting change
- **Check**:
  1. Wait full 30 seconds after save
  2. `stat ~/.local/share/actions-for-nautilus/config.json` before/after - does mtime change?
  3. Nautilus output (`nautilus --no-desktop`) shows "WATCHER THREAD: updating config"?
- **Fix**: Wait 30 seconds. If still not working, restart manually: `nautilus -q`

**Symptom**: V2 command works in terminal but fails from Nautilus
- **Most likely cause**: Environment differences (PATH, working directory, shell variables)
- **Check**:
  1. Set `cwd` property to ensure correct working directory
  2. Use absolute paths for commands (`/usr/bin/foo` not `foo`)
  3. Check if command relies on interactive shell features (aliases, functions) - these don't work
- **Fix**: Make commands self-contained. Set `cwd`. Use absolute paths. Don't rely on shell initialization files.

---

## Modification Patterns

**To add a new placeholder** (e.g., `%z` for file size):
1. Add expansion function to `afn_place_holders.py`:
   ```python
   def _expand_percent_z(index, _, files, escape, cache):
       return str(files[index]["size"])
   ```
2. Add to `_cmdline_place_holders` dict:
   ```python
   "z": { "f": _expand_percent_z, "behavior": SINGULAR}
   ```
   Choose `SINGULAR`, `PLURAL`, or `-1` (neutral)
3. Update file property extraction in `afn_menu.py::create_menu_items()`:
   ```python
   "size": file.get_size()
   ```
4. Placeholder automatically available (regex rebuilt from dict keys)
5. Document in README placeholder table

**To add a new filter type** (e.g., file size range):
1. Add properties to `configurator/actions-for-nautilus.schema.json`:
   ```json
   "min_size": {"type": "integer", "minimum": 0},
   "max_size": {"type": "integer", "minimum": 0}
   ```
2. Update `configurator/actions-for-nautilus.ui.schema.json` with UI presentation (labels, help)
3. Add to `CommandAction` class in `afn_config.py`:
   ```python
   class CommandAction():
       def __init__(self):
           # ...existing...
           self.min_size = 0
           self.max_size = 0
   ```
4. Add normalization in `afn_config.py::_check_command_action()`:
   ```python
   if type(json_action.get("min_size")) == int:
       action.min_size = json_action["min_size"]
   if type(json_action.get("max_size")) == int:
       action.max_size = json_action["max_size"]
   ```
5. Add filter function in `afn_menu.py`:
   ```python
   def _applicable_to_size(action, files):
       if action.min_size == 0 and action.max_size == 0:
           return True
       return all(
           action.min_size <= file["size"] <= (action.max_size if action.max_size > 0 else float('inf'))
           for file in files
       )
   ```
6. Call in `_passes_all_filters()`:
   ```python
   if not _applicable_to_size(action, files):
       return False
   ```
7. Update file extraction to include size (if not already done)

**To change config file location**:
1. Update `afn_config.py::_config_path` variable
2. Update `configurator/actions-for-nautilus-configurator.py::config_file` variable
3. Update README references (search `.local/share/actions-for-nautilus`)
4. Consider migration: check old location, copy to new if found
5. Update sample config installation in configurator

**To bump version for release** ("bump version", "update version", "prepare release"):

**⚠️ CRITICAL**: Always verify and use the correct current date and time. Check system date before making changes.

1. **Update `Makefile`**: Change `VERSION=X.Y.Z` line to new version
   - Pre-release: `VERSION=2.0.0~pre3-1` (tilde for pre-release)
   - Final release: `VERSION=2.0.0`

2. **Add to `RELEASE-NOTES.md`**:
   ```markdown
   # Release X.Y.Z
   * [First change/feature]
   * [Second change/feature]
   * [Third change]
   
   # Release [previous]
   ...
   ```

3. **Update `packaging/doc/actions-for-nautilus/changelog`** (Debian format):
   ```
   actions-for-nautilus (X.Y.Z) stable; urgency=medium
     * [Brief description of changes]
   
    -- Martin Bartlett <martin.j.bartlett@gmail.com>  [RFC 2822 date: "Day, DD Mon YYYY HH:MM:SS +HHMM"]
   
   [previous entries...]
   ```
   
   **Date format examples** (USE ACTUAL CURRENT DATE/TIME):
   - `Wed, 15 Jan 2025 14:30:00 +0100`
   - `Thu, 21 Mar 2024 09:15:00 +0100`
   
   **Do NOT**: Use placeholder dates, copy old dates, guess timezone

4. **Commit changes**: `git commit -am "Prepare Release X.Y.Z"`

5. **Create and push tag**: 
   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin v2  # or main, depending on branch
   git push origin vX.Y.Z
   ```

6. **Build Debian package**: `make deb`

7. **Create GitHub release**:
   - Go to https://github.com/bassmanitram/actions-for-nautilus/releases/new
   - Tag: vX.Y.Z
   - Title: "Version X.Y.Z"
   - Description: Copy from RELEASE-NOTES.md
   - Attach: `dist/actions-for-nautilus_X.Y.Z_all.deb`
   - Publish

**Version numbering** (semantic versioning):
- **MAJOR** (1.x → 2.0): Breaking config format changes, placeholder semantic changes, major architecture rewrites
- **MINOR** (2.0 → 2.1): New features, backward-compatible changes
- **PATCH** (2.0.0 → 2.0.1): Bug fixes only
- **Pre-release** (2.0.0~pre1-1): Testing before final release, tilde notation for Debian package versioning

**V2.0.0 justifies MAJOR bump**:
- New tokenization system (breaking for edge cases)
- Forked json-editor with different behavior
- Enhanced interpolation (opt-out but default)
- Multiple new features (strict-match, negative permissions, show-if-true)

---

## When to Update This Document

Update this bootstrap when:
- ✅ Core architecture changes (e.g., V3 interpolation, service-based extension)
- ✅ New critical invariant added (e.g., tokenization must preserve shell operators)
- ✅ Major dependency change (e.g., switching from json-editor fork back to upstream)
- ✅ Execution model changes (e.g., async commands, job queue)
- ✅ Integration points change (e.g., supporting Nemo/Caja in addition to Nautilus)
- ✅ New placeholder behavior semantics (changes to SINGULAR/PLURAL rules)
- ✅ Config file format breaking changes (schema v3 with incompatible structure)

Don't update for:
- ❌ Adding new placeholders following existing pattern (document in README)
- ❌ Adding new filter types following existing pattern (document in README)
- ❌ Bug fixes to tokenization, expansion, config validation
- ❌ UI improvements in configurator (CSS, layout)
- ❌ Adding sample config examples
- ❌ Documentation improvements outside this file

---

**Last Updated**: 2025-01-15  
**Last Architectural Change**: v2.0.0 - Complete rewrite of placeholder interpolation system. New tokenization layer (`afn_shell_tools.py`) with separate handling for shell vs native execution. Context-aware escaping based on quote delimiters. Plural cache optimization. Migrated from print statements to Python logging. Forked and enhanced json-editor for configurator. Added strict-match, negative permissions, show-if-true features. Lazy permission caching with timestamp expiry.

**Branch Note**: This v2 branch is a major update from v1 (last stable: 1.7.1). Has been in pre-release testing since July 2025. Ready for final 2.0.0 release.
