def convert_path_to_slash_string(path):
    if isinstance(path, list):
        path_string = ''
        for x in path:
            path_string = '%s/%s' % (path_string, x)
        return path_string
    else:
        return path_string.replace(' ', '/')


class Error(Exception):
    pass


class PyConfHoardAccessNonLeaf(Error):
    """
    Raised when we access a part of the model (container, list) etc
    but are trying to retreive or set data as if it was a leaf.
    """

    def __init__(self, path):
        self.message = 'Path %s is not a leaf.' % (convert_path_to_slash_string(path))


class PyConfHoardNonConfigLeaf(Error):
    """
    Raised when an attempt is made to write to a non-config node
    """

    def __init__(self, path):
        self.message = 'Path %s is not a configuration leaf.' % (convert_path_to_slash_string(path))

class PyConfHoardNonConfigList(Error):
    """
    Raised when an attempt is made to create to a non-config node
    """

    def __init__(self, path):
        self.message = 'Path %s is not a configuration list: ' % (convert_path_to_slash_string(path))

class PyConfHoardNotAList(Error):
    """
    Raised when an attempt is made to create on a non-list
    """

    def __init__(self, path):
        self.message = 'Path %s is not a list: ' % (convert_path_to_slash_string(path))

class PyConfHoardWrongKeys(Error):
    """
    Raised when an attempt is made to create a list item with wrong keyst
    """

    def __init__(self, path, keys):
        self.message = 'Path %s is a list with the following keys required %s' % (convert_path_to_slash_string(path), keys)

class PyConfHoardDataNoLongerRequired(Error):
    """
    Raised when we attempt to load in data which is no longer part of the schema
    """
    
    def __init__(self, path):
        self.message = 'Path %s is no longer part of the schema - data loss would occur' % (path)

class PyConfHoardInvalidUse(Error):

    def __init__(self, msg):
        self.message = msg

class PyConfHoardUnhandledUse(Error):

    def __init__(self, msg):
        self.message = msg
