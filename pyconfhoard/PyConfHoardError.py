from PyConfHoardCommon import convert_path_to_slash_string


class Error(Exception):
    pass


class PyConfHoardDataStoreLocked(Error):
    """
    Raised when attempting to access a dastore which is locked
    """

    def __init__(self, datastore, path):
        message = 'Failed to obtain a lock for %s/%s - it is already locked' % (datastore, path)
        super().__init__(message)


class PyConfHoardAccessNonLeaf(Error):
    """
    Raised when we access a part of the model (container, list) etc
    but are trying to retreive or set data as if it was a leaf.
    """

    def __init__(self, path):
        message = 'Path %s is not a leaf.' % (convert_path_to_slash_string(path))
        super().__init__(message)


class PyConfHoardNonConfigLeaf(Error):
    """
    Raised when an attempt is made to write to a non-config node
    """

    def __init__(self, path):
        message = 'Path %s is not a configuration leaf.' % (convert_path_to_slash_string(path))
        super().__init__(message)


class PyConfHoardNonConfigList(Error):
    """
    Raised when an attempt is made to create to a non-config node
    """

    def __init__(self, path):
        message = 'Path %s is not a configuration list: ' % (convert_path_to_slash_string(path))
        super().__init__(message)


class PyConfHoardNotAList(Error):
    """
    Raised when an attempt is made to create on a non-list
    """

    def __init__(self, path):
        message = 'Path %s is not a list: ' % (convert_path_to_slash_string(path))
        super().__init__(message)


class PyConfHoardWrongKeys(Error):
    """
    Raised when an attempt is made to create a list item with wrong keyst
    """

    def __init__(self, path, keys):
        message = 'Path %s is a list with the following keys required %s' % (convert_path_to_slash_string(path), keys)
        super().__init__(message)


class PyConfHoardDataNoLongerRequired(Error):
    """
    Raised when we attempt to load in data which is no longer part of the schema
    """

    def __init__(self, path):
        message = 'Path %s is no longer part of the schema - data loss would occur' % (path)
        super().__init__(message)


class PyConfHoardInvalidUse(Error):

    def __init__(self, msg):
        message = msg
        super().__init__(message)


class PyConfHoardUnhandledUse(Error):

    def __init__(self, msg):
        message = msg
        super().__init__(message)


class PyConfHoardPathAlreadyRegistered(Error):

    """ 
    Raised if we are trying to register the same path for a datastore multiple times
    """

    def __init__(self, path):
        message = 'The path %s has already been regsitered' % (path)
        super().__init__(message)


class PyConfHoardDataPathDoesNotExist(Error):

    """
    Raised if we are trying to access a key of data which does not exist
    """

    def __init__(self, path):
        message = 'The path %s does exist' % (path)
        super().__init__(message)
