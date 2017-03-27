__version__ = '0.9.20170327.1'

import six
import importlib

#local imports
from .resources import RestResource, ResourceParameters, validate_resources_configuration
from .utils import InvalidResourceError, URLValidator
from .utils import contract, new_contract, string_type, string_type_or_none


class RestClient(object):
    '''
    This is the main point of contact for end users, that is why it is in __init__
    '''
    
    #placeholder for subclassed resources
    config = {}

    @contract
    def __init__(self, url,user="", password="",  config={}, verifySSL=False):
        """ RestClient constructor

            :param url: The base URL of the REST API
            :type url: ``string_type``

            :param user: The user for authenticating with the REST API
            :type user: ``string_type_or_none``

            :param password: The password for authenticating with the REST API
            :type password: ``string_type_or_none``

            :param config: The configuration object of the REST API resources
            :type config: ``dict``

            :param verifySSL: Whether the REST client should verify SSL certificates upon making a request
            :type verifySSL: ``bool``
        """
        
        # Only allow http or https schemes for the REST API base URL
        # Validate the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        url_validator.__call__(url)

        self.url = url

        if (user is not None) and (user.strip() != ""):
            if password is None:
                password = ''
            self.auth = (user, password)
        else:
            self.auth = None


        # load targets from subclass
        if not config:
            config = self.config

        # extract the default from the config
        default = self.config.pop("default", {})
        validate_resources_configuration(config)
        self.config = config
        
        for name, item_config_dict in self.config.items():
            
            cls = item_config_dict.get('return_class', None)
            if cls:
                module_name, class_name = cls.rsplit(".", 1)
                somemodule = importlib.import_module(module_name)
                return_class = getattr(somemodule, class_name)
            else:
                return_class = RestResource
                
            item_config = ResourceParameters(item_config_dict, default)
            setattr(self,
                    name,
                    self._create_rest_resource(return_class, resource_name=name, config=item_config))

        self.verifySSL = verifySSL

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
            if fieldname == 'resources': continue
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
