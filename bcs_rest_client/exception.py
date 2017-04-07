'''
local exceptions
'''

from requests import HTTPError
from requests.models import Response

class InvalidTargetError(KeyError):
    """An error when specifying an invalid target for a given REST API."""
    def __init__(self, name, target):
        """ InvalidTargetError constructor

            :param name: The name of the REST API client
            :type name: ``string``

            :param target: The REST API target name
            :type target: ``string``

        """
        super("'{target}' is not a valid target for '{name}'".format(
            target=target,
            name=name
        ))

class BCSRestResourceError(Exception):
    pass

class BCSRestResourceMissingContentError(BCSRestResourceError):
    pass

class BCSRestResourceNotFoundError(BCSRestResourceError):
    pass
    
class BCSRestAccessDeniedError(BCSRestResourceError):
    pass

class BCSRestInternalServerError(BCSRestResourceError):
    pass
    
class BCSRestResourceHTTPError(HTTPError):
    """An error when specifying an invalid target for a given REST API."""
    def __init__(self, response_object, *args, **kwargs):
        """
        BCSRestResourceError constructor
        """
        
        assert isinstance(response_object, Response)
        self.response = response_object
        self.code = self.response.status_code
        self.reason = self.response.reason
        
        if self.code == 404:
            raise BCSRestResourceNotFoundError('Object could not be found in database')
        elif self.code in (401, 402, 403):
            raise BCSRestAccessDeniedError('error %d: Access is denied to resource %s' % (self.code, self.response.url))
        elif self.code in (500, ):
            raise BCSRestInternalServerError('error %d: Internal Server error (%s)' % (self.code, self.reason))
        else:
            raise Exception('REST error %d: %s' % (self.code, self.reason))
        
        
        super().__init__(*args, **kwargs)


