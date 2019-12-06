__version__ = '2.5.0'

from .resource import RestResource
from .response import RestResponse
from .conf import RESTConfiguration, EndPoint, BodyParameter, QueryParameter
from .exception import  RestClientConfigurationError
