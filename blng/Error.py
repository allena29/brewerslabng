"""Exceptions for using with BLNG"""


class BlngPathNotValid(Exception):

    """Raised when we decode a path that is not valid and cannot reasonably decode it."""

    def __init__(self, path):
        message = '%s is not valid.' % (path)
        super().__init__(message)


class BlngSchemaNotCached(Exception):

    """Raised when attempting to access a dastore which is not pre-cached."""

    def __init__(self, module):
        message = 'Cached schema is not available for the module: %s' % (module)
        super().__init__(message)


class BlngYangSchemaNotSupported(Exception):

    """Raised when we encounter part of a YANG schema that is not supported."""

    def __init__(self, path):
        message = 'No support for the given YANG construct at: %s' % (path)
        super().__init__(message)


class BlngYangTypeNotSupported(Exception):

    """Raised when we encounter a YANG type (not a typedef) which is not supported."""

    def __init__(self, yang_type, path):
        message = 'No support for the given YANG type: %s\nPath: %s' % (yang_type, path)
        super().__init__(message)
