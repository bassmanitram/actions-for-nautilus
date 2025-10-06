#
#  Place holder replacement functions
#
import re

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

#
#  Exported functions and values
#
PLURAL = 0
SINGULAR = 1

def get_behavior(string):
    behavior = -1
    next_index = 0
    while behavior == -1 and next_index < len(string):
        match = _place_holder_keys_re.search(string[next_index: ])
        if match is None:
            break
        behavior = _cmdline_place_holders[match.group()[1: ]]["behavior"]
        next_index += match.span()[1]
    return behavior if behavior > -1 else PLURAL

def get():
    return _place_holder_keys

def has_plural_place_holders(string):
    return _plural_place_holder_keys_re.search(string)

def has_place_holders(string):
    return _place_holder_keys_re.search(string)

def expand(string, file_index, plural_index, files, escape_function, cache):
    def match_replace(m):
        return _cmdline_place_holders[m.group()[1: ]]["f"](file_index, plural_index, files, escape_function if escape_function else None, cache)

    expanded = _place_holder_keys_re.sub(match_replace, string)
    return expanded.split("\r")

#
#  Private functions and values
#

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

def _expand_percent_percent(_, index, files, escape, cache):
    return "%"

def _expand_percent_US(_1, _2, _3, _4, _5):
    return "\r"

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
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_B_array(files, cache, index)))

def _expand_percent_D(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_D_array(files, cache, index)))

def _expand_percent_F(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_F_array(files, cache, index)))

def _expand_percent_M(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_M_array(files, cache, index)))

def _expand_percent_U(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_U_array(files, cache, index)))

def _expand_percent_W(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_W_array(files, cache, index)))

def _expand_percent_X(_, index, files, escape, cache):
    return " ".join(map(lambda file: (escape)(file) if escape else file, _expand_percent_X_array(files, cache, index)))

def _expand_percent_O(_, index, files, escape, cache):
    return ""

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
        cache.U = [file["uri"].geturl() for file in files]
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
    "_": { "f": _expand_percent_US, "behavior": -1},
    "%": { "f": _expand_percent_percent, "behavior": -1}
}

_place_holder_keys = "".join(_cmdline_place_holders.keys())
_plural_place_holder_keys = "".join([i for i in _cmdline_place_holders.keys() if i.isupper()])
_place_holder_keys_re = re.compile(f"%[{_place_holder_keys}]")
_plural_place_holder_keys_re = re.compile(f"%[{_plural_place_holder_keys}]")
