__version__ = '0.9.20170407.1'

import six
import importlib
import inspect

#local imports
from bcs_rest_client.resources import RestResource
from bcs_rest_client.utils import InvalidResourceError, URLValidator
from bcs_rest_client.utils import contract, new_contract, string_type, string_type_or_none
from bcs_rest_client.conf import RESTConfig
from bcs_rest_client.exception import BCSRestConfigurationError
from bcs_rest_client.validator import ValidationError

class RestClient(object):
    '''
    This is the main point of contact for end users, that is why it is in __init__
    '''
    
    #placeholder for subclassed resources
    config = {}

    def __init__(self, url, config=None, user="", password="",  verifySSL=False):
        """
        RestClient constructor

        """
        
        # Only allow http or https schemes for the REST API base URL
        # Validate the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        try:
            url_validator.__call__(url)
        except ValidationError as e:
            raise BCSRestConfigurationError(e.message)

        self.url = url

        if (user is not None) and (user.strip() != ""):
            if password is None:
                password = ''
            self.auth = (user, password)
        else:
            self.auth = None
        
        # -------------------------------------------------------    
        # allow empty config for testing
        if not config:
            return
        
        # set the config
        if not inspect.isclass(config):
            raise BCSRestConfigurationError('configuration is not a class')
        
        # execute and init the config class
        self.config = config()
        if not isinstance(self.config, RESTConfig):
            raise BCSRestConfigurationError('configuration is not a RESTConfig')

        for name, item_config in self.config.endpoints.items():
            
            cls = item_config.return_class
            if cls:
                try:
                    module_name, class_name = cls.rsplit(".", 1)
                except ValueError as e:
                    raise BCSRestConfigurationError('unable to parse %s into module and class name' % cls)
                somemodule = importlib.import_module(module_name)
                return_class = getattr(somemodule, class_name)
            else:
                return_class = RestResource
                
            setattr(self,name,self._create_rest_resource(return_class, resource_name=name, config=item_config))

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
