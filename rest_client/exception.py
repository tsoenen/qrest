'''
local exceptions
'''

from requests import HTTPError
from requests.models import Response


# ================================================================================================
class RestClientException(Exception):
    ''' wrapper exception '''
    pass


class RestClientResourceError(RestClientException):
    ''' wrapper exception '''
    pass


class RestClientConfigurationError(RestClientException):
    ''' wrapper exception '''
    pass


class RestClientQueryError(RestClientException):
    ''' wrapper exception '''
    pass


class InvalidTargetError(RestClientException):
    """An error when specifying an invalid target for a given REST API."""
    pass

    # def __init__(self, name, target):
        # """ InvalidTargetError constructor

            # :param name: The name of the REST API client
            # :type name: ``string``

            # :param target: The REST API target name
            # :type target: ``string``

        # """
        # super()"'{target}' is not a valid target for '{name}'".format(
            # target=target,
            # name=name
        # ))


class InvalidResourceError(RestClientException):
    """An error when specifying an invalid resource for a given REST API."""
    def __init__(self, name, resource):
        """ InvalidResourceError constructor

            :param name: The name of the REST API client
            :type name: ``string``

            :param resource: The REST API resource name
            :type resource: ``string``

        """
        response = "'{resource}' is not a valid resource for '{name}'".format(resource=resource, name=name)
        super(InvalidResourceError, self).__init__(response)


class RestResourceMissingContentError(RestClientResourceError):
    ''' wrapper exception '''
    pass


class RestResourceNotFoundError(RestClientResourceError):
    ''' wrapper exception '''
    pass


class RestAccessDeniedError(RestClientResourceError):
    ''' wrapper exception '''
    pass


class RestLoginError(RestClientResourceError):
    ''' wrapper exception '''
    pass

class CASLoginError(RestLoginError):
    pass

class CASGrantingTicketError(CASLoginError):
    pass

class CASServiceTicketError(CASLoginError):
    pass


class RestInternalServerError(RestClientResourceError):
    ''' wrapper exception '''
    pass

class RestBadRequestError(RestClientResourceError):
    ''' wrapper excpetion '''
    pass

class RestResourceHTTPError(HTTPError):
    """An error when specifying an invalid target for a given REST API."""
    def __init__(self, response_object, *args, **kwargs):
        """
        RestResourceError constructor
        """

        assert isinstance(response_object, Response)
        self.response = response_object
        self.code = self.response.status_code
        self.reason = self.response.reason
        
        if self.code == 400:
            raise RestBadRequestError('Bad request for resource %s' % (self.response.url,))
        elif self.code == 404:
            raise RestResourceNotFoundError('Object could not be found in database')
        elif self.code in (401, 402, 403):
            raise RestAccessDeniedError('error %d: Access is denied to resource %s' % (self.code, self.response.url))
        elif self.code in (500, ):
            raise RestInternalServerError('error %d: Internal Server error (%s)' % (self.code, self.reason))
        else:
            raise Exception('REST error %d: %s' % (self.code, self.reason))


        super().__init__(*args, **kwargs)
