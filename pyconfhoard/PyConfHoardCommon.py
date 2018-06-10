import dpath.util
import re


def decode_path_string(path, separator=' ', ignore_last_n=0, get_index=None, ignore_root=False):
    """
    This method should always be used to provide safe paths for dpath to work with.
    In particular this will add a fake 'root' element at the begining of the list
    as dpath functions don't like an empty glob.

    TODO: in future we should look to intelligently seprate on spaces
    i.e. level1 level2 level3 cfgonly "this is a value" should result in a path
    path = ['level1', 'level2', 'level3', 'cfgonly']
    value = 'this is a value'
    """
    if not isinstance(path, list):
        regex = re.compile("{([A-Za-z0-9]*)}")
        path = regex.sub('/{\g<1>}', path)

        if not path[0:5] == separator + 'root' and ignore_root is False:
            path = separator + 'root' + separator + path
        separated = path.split(separator)
    else:
        if len(path) == 0:
            if ignore_root is False:
                path.insert(0, 'root')
        elif not path[0] == 'root' and ignore_root is False:
            path.insert(0, 'root')
        separated = path

    seplen = len(separated)
    # Remove anything which is a null string
    for i in range(seplen):
        if separated[seplen-i-1] == '':
            separated.pop(seplen-i-1)

    for i in range(ignore_last_n):
        try:
            separated.pop()
        except:
            pass

    if isinstance(get_index, int):
        return separated[get_index]

    return separated


def fetch_keys_from_path(obj, path):
    result = []
    for key in dpath.util.get(obj, path).keys():
        if key == '__listelement':
            path.append('__listelement')
            return fetch_keys_from_path(obj, path)
        elif key == '__schema':
            pass
        else:
            result.append(key)
    return sorted(result)


def convert_path_to_slash_string(path):
    if isinstance(path, list):
        path_string = ''
        for x in path:
            path_string = path_string + '/' + x
        if len(path_string) == 0:
            path_string = '/'
        elif not path_string[0] == '/':
            path_string = '/' + path_string
        return path_string
    if not path[0] == '/':
        path = '/' + path
    return path.replace(' ', '/')
