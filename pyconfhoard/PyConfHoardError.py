def convert_path_to_slash_string(path):
    if isinstance(path, list):
        path_string = ''
        for x in path:
            path_string = path_string + '/' + x
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
