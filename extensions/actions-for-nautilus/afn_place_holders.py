###
### Place holder replacement functions
###
import sys, re, afn_config

class PluralCache():
    def __init__(self):
        self.B = None
        self.D = None
        self.F = None
        self.M = None
        self.O = None
        self.U = None
        self.W = None
        self.X = None

###
### Exported functions and values
###
PLURAL = 0
SINGULAR = 1

def resolve(string, file_index, files, escape, cache) -> tuple[str, PluralCache]:
    if cache is None:
        cache = PluralCache()
    
    def match_replace(m):
        return _cmdline_place_holders[m.group()[1:]]["f"](file_index, None, files, _original_escape if escape else None, cache)
    
    output = _place_holder_keys_re.sub(match_replace, string)
    return (output, cache)

#
# Slightly more complex
#
def resolve2(array, file_index, files, escape, cache) -> tuple[str, PluralCache]:
    command_array = []
    if cache is None:
        cache = PluralCache()
    plural_index = None

    def match_replace(m):
        return _cmdline_place_holders[m.group()[1:]]["f"](file_index, plural_index, files, _improved_escape if escape else None, cache)

    for string in array:
        # If we are escaping, each token gets surrounded by quotes with inner quotes escaped
        if escape:
            string = string.replace('"','\\"')
            string = '"' + string + '"'
        if _plural_place_holder_keys_re.search(string):
            for plural_index,_ in enumerate(files):
                command_array.append(_place_holder_keys_re.sub(match_replace, string))
            plural_index = None
        else:
            command_array.append(_place_holder_keys_re.sub(match_replace, string))
    
    return (command_array, cache)

def get_behavior(string):
    behavior = -1
    next_index = 0
    while behavior == -1 and next_index < len(string):
        match = _place_holder_keys_re.search(string[next_index:])
        if match is None:
            break
        behavior = _cmdline_place_holders[match.group()[1:]]["behavior"]
        next_index += match.span()[1]
    return behavior if behavior > -1 else PLURAL

def get():
    return _place_holder_keys


# This breaks the command line into space-delimited groups that
# contain one or more A4N place holders. This allows the user to 
# specify quoting semantics and anything else funky they want to
# do with the placeholders, because for each group that contains
# a singlular placeholder, the group will be duplicated with the
# the placeholder expanded for each member of a selection.
#
# '\ ' and '\%' are ignored.
#
_split_to_parts_re = re.compile(r'[\\]?[ %]')
def split_to_parts(line):
    parts = []
    collect_spaces = True
    part = ""
    subpart_start = 0
    last_space = -1
    i = _split_to_parts_re.finditer(line)
    for m in i:
        first = m.start()
        end = m.end()
        last = end-1
        if line[first:end] == r'\ ':
            # Skip the backslash, the space isn't a part terminator
            part += line[subpart_start:first] # everything up to the backslash
            subpart_start = last              # next sub-part starts with the space
        elif line[last] == ' ':
            # we have "? "
            if collect_spaces:
                # we are collecting spaces; record the index of the space
                last_space = last
            else:
                # we are not collecting spaces; The space is the end of a part
                part += line[subpart_start:last]  # append the subpart to the part
                parts.append(part)             # push it
                part = ""                      # reinitialize
                subpart_start = end
                last_space = -1
                collect_spaces = True
        else:
            # We have "?%" - the start of a place holder - we look out for the
            # next non-escaped space
            collect_spaces = False

            if last_space > -1:
                # push everything before the previous space (if any) as a part
                part += line[subpart_start:last_space]
                subpart_start = last_space + 1
                last_space = -1

                if len(part) > 0:
                    parts.append(part)
                    part = ""

    if subpart_start < len(line):
        part += line[subpart_start:]

    if len(part) > 0:
        parts.append(part)

    return parts

###
### Private functions and values
###

#
# In double quoted strings - which the tokens end up being delimited
# by when a shell is being used to execute an action, the following
# characters must be quoted so that the shell doesn't 
#
TO_ESCAPE = re.compile(r'([$\`"])')

def _original_escape(str):
    return str.replace(" ","\\ ")

def _improved_escape(str):
    return TO_ESCAPE.sub(r'\\\1',str)

def _expand_percent_c(index, _, files, escape, cache):
    return str(len(files))

def _expand_percent_h(index, _, files, escape, cache):
    h = files[0]["uri"].hostname
    return "" if h is None else (escape)(h) if escape else h

def _expand_percent_n(index, _, files, escape, cache):
    n = files[0]["uri"].username
    return "" if n is None else (escape)(n) if escape else n

def _expand_percent_p(index, _, files, escape, cache):
    p = files[0]["uri"].port
    return "" if p is None else p

def _expand_percent_s(index, _, files, escape, cache):
    return files[0]["uri"].scheme

#
# SINGULAR (per index)
#
def _expand_percent_b(index, _, files, escape, cache):
    return (escape)(files[index]["basename"]) if escape else files[index]["basename"]

def _expand_percent_d(index, _, files, escape, cache):
    return (escape)(files[index]["folder"]) if escape else files[index]["folder"]

def _expand_percent_f(index, _, files, escape, cache):
    return (escape)(files[index]["filepath"]) if escape else files[index]["filepath"]

def _expand_percent_m(index, _, files, escape, cache):
    return (escape)(files[index]["mimetype"]) if escape else files[index]["mimetype"]

def _expand_percent_o(index, files, escape, cache):
    return ""

def _expand_percent_u(index, _, files, escape, cache):
    return (escape)(files[index]["uri"].geturl()) if escape else files[index]["uri"].geturl()

def _expand_percent_w(index, _, files, escape, cache):
    return (escape)(_file_name_extension(files[index]["basename"])["name"]) if escape else _file_name_extension(files[index]["basename"])["name"]

def _expand_percent_x(index, _, files, escape, cache):
    return (escape)(_file_name_extension(files[index]["basename"])["extension"]) if escape else _file_name_extension(files[index]["basename"])["extension"]

#
# PLURAL (all)
#
def _expand_percent_B(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_B_array(files,cache,index)))

def _expand_percent_D(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_D_array(files,cache,index)))

def _expand_percent_F(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_F_array(files,cache,index)))

def _expand_percent_M(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_M_array(files,cache,index)))

def _expand_percent_U(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_U_array(files,cache,index)))

def _expand_percent_W(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_W_array(files,cache,index)))

def _expand_percent_X(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_X_array(files,cache,index)))

def _expand_percent_O(_, index, files, escape, cache):
    return ""

def _expand_percent_percent(_, index, files, escape, cache):
    return "%"

#
# Using the plural caches
#
def _expand_percent_B_array(files, cache, index = None):
    if cache.B is None:
        cache.B = [file["basename"] for file in files]
    return cache.B if index is None else [cache.B[index]]

def _expand_percent_D_array(files, cache, index = None):
    if cache.D is None:
        cache.D = [file["folder"] for file in files]
    return cache.D if index is None else [cache.D[index]]

def _expand_percent_F_array(files, cache, index = None):
    if cache.F is None:
        cache.F = [file["filepath"] for file in files]
    return cache.F if index is None else [cache.F[index]]

def _expand_percent_M_array(files, cache, index = None):
    if cache.M is None:
        cache.M = [file["mimetype"] for file in files]
    return cache.M if index is None else [cache.M[index]]

def _expand_percent_U_array(files, cache, index = None):
    if cache.U is None:
        cache.U = [file["uri"] for file in files]
    return cache.U if index is None else [cache.U[index]]

def _expand_percent_W_array(files, cache, index = None):
    if cache.W is None:
        cache.W = [_file_name_extension(file["basename"])["name"] for file in files]
    return cache.W if index is None else [cache.W[index]]

def _expand_percent_X_array(files, cache, index = None):
    if cache.X is None:
        cache.X = [_file_name_extension(file["basename"])["extension"] for file in files]
    return cache.X if index is None else [cache.X[index]]

def _file_name_extension(basename):
    w = basename.rpartition(".")
    return {"name": w[0], "extension": w[2]} if w[1] == "." else {"name": w[2], "extension": ""}

_cmdline_place_holders = {
    "b": { "f": _expand_percent_b, "behavior": SINGULAR},
    "B": { "f": _expand_percent_B, "behavior": PLURAL},
    "c": { "f": _expand_percent_c, "behavior": -1},
    "d": { "f": _expand_percent_d, "behavior": SINGULAR},
    "D": { "f": _expand_percent_D, "behavior": PLURAL},
    "f": { "f": _expand_percent_f, "behavior": SINGULAR},
    "F": { "f": _expand_percent_F, "behavior": PLURAL},
    "h": { "f": _expand_percent_h, "behavior": -1},
    "m": { "f": _expand_percent_m, "behavior": SINGULAR},
    "M": { "f": _expand_percent_M, "behavior": PLURAL},
    "n": { "f": _expand_percent_n, "behavior": -1},
    "o": { "f": _expand_percent_o, "behavior": SINGULAR},
    "O": { "f": _expand_percent_O, "behavior": PLURAL},
    "p": { "f": _expand_percent_p, "behavior": -1},
    "s": { "f": _expand_percent_s, "behavior": -1},
    "u": { "f": _expand_percent_u, "behavior": SINGULAR},
    "U": { "f": _expand_percent_U, "behavior": PLURAL},
    "w": { "f": _expand_percent_w, "behavior": SINGULAR},
    "W": { "f": _expand_percent_W, "behavior": PLURAL},
    "x": { "f": _expand_percent_x, "behavior": SINGULAR},
    "X": { "f": _expand_percent_X, "behavior": PLURAL},
    "%": { "f": _expand_percent_percent,"behavior": -1}
}

_place_holder_keys = "".join(_cmdline_place_holders.keys())
_plural_place_holder_keys = "".join([i for i in _cmdline_place_holders.keys() if i.isupper()])
_place_holder_keys_re = re.compile(f"%[{_place_holder_keys}]")
_plural_place_holder_keys_re = re.compile(f"%[{_plural_place_holder_keys}]")


#
# Testing
#
if __name__ == "__main__":

    import shlex

    test_files = [
        {
            "basename": "file-1",
            "folder":   "/home/use/dir1",
            "filepath": "/home/use/dir1/file-1",
            "uri":      "file:///home/use/dir1/file-1",
            "mimetype": "test/file-1" 
        },
        {
            "basename": "file-2",
            "folder":   "/home/use/dir2",
            "filepath": "/home/use/dir2/file-2",
            "uri":      "file:///home/use/dir2/file-2",
            "mimetype": "test/file-2" 
        },
        {
            "basename": "file 3",
            "folder":   "/home/use/dir 3",
            "filepath": "/home/use/dir 3/file 3",
            "uri":      "file:///home/use/dir+3/file+3",
            "mimetype": "test/file-3" 
        },
        {
            "basename": "4`th file has a $ sign and a \\ too",
            "folder":   "/home/use/dir 4",
            "filepath": "/home/use/dir 4/4`th file has a $ sign and a \\ too",
            "uri":      "file:///home/use/dir+4/4%60th%20file%20has%20a%20%24%20sign%20and%20a%20%5C%20too",
            "mimetype": "test/file-4" 
        },
    ]

    if len(sys.argv) > 1:
        line = sys.argv[1]
        print(line)

        parts = shlex.split(line)

        b = get_behavior(line)

        if b == 0:
            (final, _) = resolve(line, 0, test_files, True, None)
            print(f'Original: {final}')
            (final, _) = resolve2(parts, 0, test_files, False, None)
            print(f'Improved (raw): {final}')
            (final, _) = resolve2(parts, 0, test_files, True, None)
            print(f'Improved (shell): { " ".join(final)}')
        else:
            cache = None
            cache2 = None
            for i,_ in enumerate(test_files):
                (final, _) = resolve(line, i, test_files, True, cache)
                print(f'Original: {final}')
                (final, _) = resolve2(parts, i, test_files, False, cache2)
                print(f'Improved (raw): {final}')
                (final, _) = resolve2(parts, i, test_files, True, cache2)
                print(f'Improved (shell): {" ".join(final)}')
