__version__ = '2.4.3'

'''
Contains the main classes that interact with the end user
'''

import logging
import importlib
import inspect
from contracts import contract, new_contract
import six

logger = logging.getLogger('rest_client')


# ================================================================================================
# local imports
from rest_client.resources import RestResource
from rest_client.exception import InvalidResourceError, RestClientConfigurationError
from rest_client.utils import string_type, string_type_or_none
from rest_client.conf import RESTConfiguration
from rest_client.auth import RESTAuthentication
from rest_client.validator import ValidationError, URLValidator

# ================================================================================================
class RestClient(object):
    '''
    This is the main point of contact for end users, that is why it is in __init__
    '''

    #placeholder for subclassed resources
    config = {}
    auth = None

    def __init__(self, url, config, verifySSL=False):
        """
        RestClient constructor

        :param url: The base URL of the REST API
        :type url: ``string_type``

        :param auth: The authentication object, i.e. username/password tuple, for authenticating with the REST API
        :type auth: *

        :param resources: The configuration object of the REST API resources
        :type resources: ``dict``

        :param verifySSL: Whether the REST client should verify SSL certificates upon making a request
        :type verifySSL: ``bool`` or `` string_type`` 

        """

        # Only allow http or https schemes for the REST API base URL
        # Validate the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        try:
            url_validator.__call__(url)
        except ValidationError as e:
            raise RestClientConfigurationError(e.message)

        self.url = url

        # set the config
        if not isinstance(config, RESTConfiguration):
            raise RestClientConfigurationError('configuration is not a RESTConfig instance')
        self.config = config

        for name, item_config in self.config.endpoints.items():

            cls = item_config.return_class
            if cls:
                try:
                    module_name, class_name = cls.rsplit(".", 1)
                except ValueError as e:
                    raise RestClientConfigurationError('unable to parse %s into module and class name' % cls)
                somemodule = importlib.import_module(module_name)
                return_class = getattr(somemodule, class_name)
            else:
                return_class = RestResource

            setattr(self, name, self._create_rest_resource(return_class, resource_name=name, config=item_config))

        self.verifySSL = verifySSL

        # get the authentication module
        self.auth = self.config.get_authentication_module(self)


    # ---------------------------------------------------------------------------------------------
    @property
    def resources(self):
        """ Lists the available resources for this REST API

            :return: A list of the available resources for this REST API
            :rtype: ``list(string_type)``
        """

        resources = []
        fieldnames = dir(self)
        for fieldname in fieldnames:
            # this exclusion is to prevent endless loops
            if fieldname == 'resources':
                continue
            field = getattr(self, fieldname)
            if isinstance(field, RestResource):
                resources.append(field.name)
        return resources


    # ---------------------------------------------------------------------------------------------
    def _create_rest_resource(self, return_class, resource_name, config):
        """ This function is used to dynamically create request functions for a specified REST API resource

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A function that builds and sends a request for the specified REST API resource and validates the function call
            :rtype: ``list(string_type)``
        """

        if not config:
            raise InvalidResourceError(name=type(self).__name__, resource=resource_name)

        rest_resource = return_class(client=self, name=resource_name, config=config)
        return rest_resource


class RestClientLauncher(object):
    '''
    This is a wrapper object to make life easier for end-users. It creates the actual resource
    object instead of importing from multiple libs to join these together
    '''
    config = None

    def __new__(cls, url, verifySSL=False):
        config = cls.config
        if not isinstance(config, RESTConfiguration):
            raise RestClientConfigurationError('config is not a RESTConfig instance')

        return RestClient(config=config, url=url, verifySSL=verifySSL)

    def __init__(self):
        pass
