#
# Shlex - but telling us how each token is delimited
#
import shlex, re
from enum import Enum
from afn_place_holders import has_place_holders, has_plural_place_holders, expand, PluralCache, get_behavior, PLURAL

class Handle(Enum):
    NO_HANDLE = 0
    SINGULAR = 1
    PLURAL = 2

def is_command_plural(string):
    return get_behavior(string) is PLURAL

def resolve(string, file_index, files, escape, cache) -> tuple[str, PluralCache]:

    if cache is None:
        cache = PluralCache()

    def _original_escape(str):
        return str.replace(" ","\\ ")

    output = " ".join(expand(string, file_index, None, files, _original_escape if escape else None, cache))

    return (output, cache)

#
# Regexs for escaping stuff
#
ESCAPE_RES = {
    "'": None,
    '"': re.compile(r'([\\"`$])')
}
RAW_ESCAPE_RE = re.compile(r'([ \t\n;;&()<>|*?\[\]$\'`"\\{!}])')

#
# Slightly more complex for enhanced interpolation
#
def resolve2(array, file_index, files, escape, cache) -> tuple[str, PluralCache]:
    if cache is None:
        cache = PluralCache()
        
    command_array = []
    plural_index = None
    escape_re = RAW_ESCAPE_RE

    def _improved_escape(str):
        return escape_re.sub(r'\\\1',str) if escape_re else str

    for token, handle in array:
        escape_re = ESCAPE_RES.get(token[0], RAW_ESCAPE_RE)
        if handle is Handle.PLURAL:
            for plural_index,_ in enumerate(files):
                command_array += expand(token, file_index, plural_index, files, _improved_escape if escape else None, cache)
            plural_index = None
        elif handle is Handle.SINGULAR:
            command_array += expand(file_index, None, files, _improved_escape if escape else None, cache)
        else:
            command_array.append(token)
    
    return (command_array, cache)

def _get_token_type(str):
    return Handle.PLURAL if has_plural_place_holders(str) else Handle.SINGULAR if has_place_holders(str) else Handle.NO_HANDLE

#
# We tokenize for native (non shell) execution by using shlex because
# we end up with strict argument tokenization suitable for passing as
# an array of arguments, and we don't have to perform escaping
#
def tokenize_for_native(input_string):
    return list(map(lambda token: ((token, _get_token_type(token))), shlex.split(input_string)))

#
# Tokenize in a suitable fashion for reconstituting as a command line
#
# The resultant list contains tuples of stuff that will end up in the command line
# along with how to handle that stuff when the time comes
#
def tokenize_for_shell(input_string):

    tokens = []
    i = 0
    string_length = len(input_string)

    def append_token(token,type):
        if len(token) > 0:
            if len(tokens) > 0 and type is Handle.NO_HANDLE and tokens[-1][1] is Handle.NO_HANDLE:
                tokens[-1] = (tokens[-1][0] + token, Handle.NO_HANDLE)
            else:
                tokens.append((token,type))

    while i < string_length:
        char = input_string[i]
        token = ""
        if char.isspace() or char in ";&|()<>":
            # Handle shell special characters and whitespace as tokens and separators, collapsing consecutive ones
            token += char  # Start with the current char
            i += 1
            while i < string_length and input_string[i] in ";&|()<>":
                token += input_string[i]  # Append consecutive special chars
                i += 1
            append_token(token, Handle.NO_HANDLE)
            continue

        elif char == "'" or char == '"':
            # Single quoted is always treated as is
            # Double quoted can have escaped double quotes
            i += 1
            token += char
            handle_esc = char == '"'
            while i < string_length and input_string[i] != char:
                if input_string[i] == '\\' and handle_esc:
                    token += '\\'
                    i += 1
                    # Add the next character too, regardless
                    if i < string_length:
                        token += input_string[i]
                else:
                    token += input_string[i]
                i += 1
            if i < string_length:
                token += char
                i += 1  # Consume the closing quote
            append_token(token, _get_token_type(token))
            continue

        else:
            # Handle unquoted words along with any escapes in them
            while i < string_length:
                if input_string[i] == '\\':
                    token += '\\'
                    i += 1
                    # Add the next character too, regardless
                    if i < string_length:
                        token += input_string[i]
                        i += 1
                elif not input_string[i].isspace() and input_string[i] not in ";&|()<>\"'":
                    token += input_string[i]
                    i += 1
                else:
                    break
            append_token(token, _get_token_type(token))
            continue

    return tokens

def main(argv):
    """
    Demonstrates the usage of the posix_shell_tokenize function.
    """
    test_strings = [
        "ls -l \"My File with Spaces.txt\" | grep \"pattern$\"  ; echo 'Hello'",
        "echo $VAR > output.txt",
        "command1 && command2 || command3",
        "find . -name \"*.txt\" -print0 | xargs -0 ls -l",
        "if [ \"$VAR\" = \"value\" ]; then echo \"Match\"; fi",
        "a\\ b c'd'e\"f\"g",
        "export PATH=$PATH:/new/path",
        "  leading and trailing spaces  ",
        "'  quoted leading and trailing spaces  '",
        "a\tb\tc",
        "a\\\nb",
        "|",
        ";;",
        "&",
        "(",
        ")",
        "<",
        ">",
        "a|b",
        "a;b",
        "a&b",
        "a(b)",
        "a<b",
        "a>b",
        "a||b",  # Test consecutive special characters
        "a&&&b", # Test more consecutive special characters
        "a;;;b",
        "a<<<<<b",
        #Now onto what we are REALLY interested in
        "ls -l \"%f\" | grep \"pattern$\"  ; echo 'Hello'",
        "ls -l '%F' | grep \"pattern$\"  ; echo 'Hello'",
        "ls -l %F\ %B | grep \"pattern$\"  ; echo 'Hello'",
        "ls -l '%F %B' | grep \"pattern$\"  ; echo 'Hello'",
        "ls -l \"%F\ %B\" | grep \"pattern$\"  ; echo 'Hello'",
    ]

    for s in test_strings:
        print(f"\nInput String: '{s}'")
        tokens = tokenize_for_native(s)
        print(f"NATIVE:")
        for spec in tokens:
            print(f"  {spec}")

        tokens = tokenize_for_shell(s)
        print(f"SHELL:")
        for spec in tokens:
            print(f"  {spec}")

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

    if len(argv) > 1:
        line = argv[1]
        print(line)

        b = get_behavior(line)

        shell_parts = tokenize_for_shell(line)
        native_parts = tokenize_for_native(line)

        if b == 0:
            (final, _) = resolve(line, 0, test_files, True, None)
            print(f'Original: {final}')
            (final, _) = resolve2(native_parts, 0, test_files, False, None)
            print(f'Improved (raw): {final}')
            (final, _) = resolve2(shell_parts, 0, test_files, True, None)
            print(f'Improved (shell): { " ".join(final)}')
        else:
            cache = None
            cache2 = None
            for i,_ in enumerate(test_files):
                (final, _) = resolve(line, i, test_files, True, cache)
                print(f'Original: {final}')
                (final, _) = resolve2(native_parts, i, test_files, False, cache2)
                print(f'Improved (raw): {final}')
                (final, _) = resolve2(shell_parts, i, test_files, True, cache2)
                print(f'Improved (shell): {" ".join(final)}')

if __name__ == "__main__":
    import sys
    main(sys.argv)
