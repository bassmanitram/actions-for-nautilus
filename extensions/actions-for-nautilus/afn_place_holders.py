###
### Place holder replacement functions
###
import re

###
### Exported functions and values
###
PLURAL = 0
SINGULAR = 1

def resolve(string, file_index, files, escape):
    next_index = 0
    _place_holder_list = "".join(_cmdline_place_holders.keys())
    while True:
        match = re.search( "%["+_place_holder_keys+"]", string[next_index:])
        if match is None:
            break
        span = match.span()
        start_index = next_index+span[0]
        end_index = next_index+span[1]
        replacement = _cmdline_place_holders[match.group()[1:]]["f"](file_index, files, escape)
        string = string[:start_index] + replacement + string[end_index:]
        next_index = (start_index + len(replacement))
    return string

def get_behavior(string):
    behavior = -1
    next_index = 0
    while behavior == -1 and next_index < len(string):
        match = re.search( "%["+_place_holder_keys+"]", string[next_index:])
        if match is None:
            break
        behavior = _cmdline_place_holders[match.group()[1:]]["behavior"]
        next_index += match.span()[1]
    return behavior if behavior > -1 else PLURAL

def get():
    return _place_holder_keys

###
### Private functions and values
###

def _expand_percent_percent(index, files, escape):
    return "%"

def _expand_percent_b(index, files, escape):
    return files[index]["basename"].replace(" ","\\ ")  if escape else files[index]["basename"]

def _expand_percent_B(index, files, escape):
    return " ".join(map(lambda file: file["basename"].replace(" ","\\ ") if escape else file["basename"], files))

def _expand_percent_c(index, files, escape):
    return str(len(files))

def _expand_percent_d(index, files, escape):
    return files[index]["folder"].replace(" ","\\ ") if escape else files[index]["folder"]

def _expand_percent_D(index, files, escape):
    return " ".join(map(lambda file: file["folder"].replace(" ","\\ ") if escape else file["folder"], files))

def _expand_percent_f(index, files, escape):
    return files[0]["filename"].replace(" ","\\ ") if escape else files[0]["filename"]

def _expand_percent_F(index, files, escape):
    return " ".join(map(lambda file: file["filename"].replace(" ","\\ ") if escape else file["filename"], files))

def _expand_percent_h(index, files, escape):
    h = files[index]["uri"].hostname
    return "" if h is None else h.replace(" ","\\ ") if escape else h

def _expand_percent_m(index, files, escape):
    return files[index]["mimetype"].replace(" ","\\ ") if escape else files[index]["mimetype"]

def _expand_percent_M(index, files, escape):
    return " ".join(map(lambda file: file["mimetype"].replace(" ","\\ ") if escape else file["mimetype"], files))

def _expand_percent_n(index, files, escape):
    n = files[index]["uri"].username
    return "" if n is None else n.replace(" ","\\ ") if escape else n

def _expand_percent_o(index, files, escape):
    return ""

def _expand_percent_O(index, files, escape):
    return ""

def _expand_percent_p(index, files, escape):
    p = files[index]["uri"].port
    return "" if p is None else p

def _expand_percent_s(index, files, escape):
    return files[index]["uri"].scheme

def _expand_percent_u(index, files, escape):
    return files[index]["uri"].geturl().replace(" ","\\ ") if escape else files[index]["uri"].geturl()

def _expand_percent_U(index, files, escape):
    return " ".join(map(lambda file: file["uri"].geturl().replace(" ","\\ ") if escape else file["uri"].geturl(), files))

def _expand_percent_w(index, files, escape):
    return _file_name_extension(files[index]["basename"])["name"].replace(" ","\\ ") if escape else _file_name_extension(files[index]["basename"])["name"]

def _expand_percent_W(index, files, escape):
    return " ".join(map(lambda file: _file_name_extension(file["basename"])["name"].replace(" ","\\ ") if escape else _file_name_extension(file["basename"])["name"], files))

def _expand_percent_x(index, files, escape):
    return _file_name_extension(files[index]["basename"])["extension"].replace(" ","\\ ") if escape else _file_name_extension(files[index]["basename"])["extension"]

def _expand_percent_X(index, files, escape):
    return " ".join(map(lambda file: _file_name_extension(file["basename"])["extension"].replace(" ","\\ ") if escape else _file_name_extension(file["basename"])["extension"], files))

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
