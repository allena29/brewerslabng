"""Exceptions for using with BLNG"""


class BlngSchemaNotCached(Exception):

    """Raised when attempting to access a dastore which is not pre-cached."""

    def __init__(self, module):
        message = 'Cached schema is not available for the module: %s' % (module)
        super().__init__(message)
