
class CrestleBaseException(Exception):
    """
    All Crestle exceptions inherit from this exception.
    """


class CrestleHttpBaseException(CrestleBaseException):
    """
    All Crestle HTTP Exceptions inherit from this exception.
    """

    def __init__(self, *args, **kwargs):
        for key, value in iterator(kwargs):
            setattr(self, key, value)
        super(CrestleHttpBaseException, self).__init__(*args)


class HttpClientError(CrestleHttpBaseException):
    """
    Called when the server tells us there was a client error (4xx).
    """


class HttpNotFoundError(HttpClientError):
    """
    Called when the server sends a 404 error.
    """


class HttpServerError(CrestleHttpBaseException):
    """
    Called when the server tells us there was a server error (5xx).
    """


