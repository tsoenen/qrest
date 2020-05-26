'''
Contains all the configuration classes to create a API Configuration
'''
from collections import defaultdict
from typing import Optional, Type

import logging
logger = logging.getLogger(__name__)

# ================================================================================================
# local imports
from .auth import AuthConfig
from .resource import Resource, JSONResource
from .exception import RestClientConfigurationError
from .utils import URLValidator

# ================================================================================================
#  Interface tweak
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

# ================================================================================================
class ParameterConfig:
    '''
    Contain and validate parameters for a REST endpoint. As this is a configuration container only, the main
    purpose is to store the config and check if the input aligns with the intended use. There is no
    validation beyond this point
    '''

    # -----------------------------------------------------------------------------------------------------
    def __init__(self, name: str,
                 required: bool = False,
                 multiple: bool = False,
                 exclusion_group: Optional[str] = None,
                 default: Optional[str] = None,
                 choices: Optional[list] = None,
                 description: Optional[str] = None
                 ):
        '''
        Parameter configuration. Details the name and limitations on the REST parameter and how it
        interacts with other parameters within the same endpoint. 

        :param name: the 'remote' name of the parameter. this name is what the REST resource actually gets to interpret
        :param required: if this parameter is ommitted in the qyery, throw an exception
        :param multiple: if set to True, the value of the query parameter is a list
        :param exclusion_group: parameters in the same exclusion group may not be used together
        :param default: the default entry if this parameter is not supplied
        :param choices: a list of possible values for this parameter
        :param description: any information about the parameter, such as data format
        '''

        self.name = name
        self.required = required
        self.multiple = multiple
        self.exclusion_group = exclusion_group
        self.default = default
        self.choices = choices
        self.description = description or ""
        self._validate()

    # -----------------------------------------------------------------------------------------------------
    def _validate(self):
        '''
        internal routine to check a set of rules to validate if the ParameterConfig is configured correctly
        '''
        if not isinstance(self.required, bool):
            raise RestClientConfigurationError('parameter "required" must be boolean')
        if not isinstance(self.multiple, bool):
            raise RestClientConfigurationError('parameter "multiple" must be boolean')
        if not isinstance(self.description, str):
            raise RestClientConfigurationError('parameter "description" must be string')
        if self.exclusion_group:
            if not isinstance(self.exclusion_group, str):
                raise RestClientConfigurationError("group name must be a string")
            if not self.exclusion_group.strip():
                raise RestClientConfigurationError("group name must be a string")
        if self.default and self.required:
            raise RestClientConfigurationError("you cannot combine required=True and a default setting")
        if self.choices and not isinstance(self.choices, list):
            raise RestClientConfigurationError("choices must be a list")
        if self.default and self.choices:
            if self.default not in self.choices:
                raise RestClientConfigurationError("if there is a choices list, default must be in this list")


# ================================================================================================
class QueryParameter(ParameterConfig):
    '''
    Subclass to specify parameters to be placed in the query part of the REST request
    '''

    call_location = 'query'


# ================================================================================================
class BodyParameter(ParameterConfig):
    '''
    Subclass to specify parameters to be placed in the query part of the REST request
    '''

    call_location = 'body'


# ================================================================================================
class ResourceConfig:
    '''
    contain and validate details for a REST endpoint. Effectively this creates an ORM wrapper around a
    REST endpoint, pretending it is a python object
    
    '''

    # -----------------------------------------------------------------------------------------------------
    def __init__(self,
                 path: list,
                 method: str,
                 parameters: Optional[dict] = None,
                 headers: Optional[dict] = None,
                 processor: Optional[Type[Resource]] = None,
                 description: Optional[str] = None,
                 path_description: Optional[dict] = None
                 ):
        '''
        Constructor, stores externally supplied parameters and validate the quality of it
        
        :param path: a list separation of the path components, e.g. ['api','v2','user','{name},'stats'] where
                     names in brackets are converted to path parameters. 
        :param method: one of GET,PUT,etc
        :param parameters: a dictionary of ParameterConfig instances that each describe one parameter. This is
                    relevant for body and query parameters only, path parameters are specified in the path itself
                    and subsequent annotation of those parameters is done in path_description.
        :param headers: a dictionary of headers that will be provided to the endpoint. Typical use is the response_type
        :param processor: a subclass of rest_client.RestResource that handles specific use cases.
                    This now defaults to JSONResource as this is the most common use type
        :param description: A general description of the endpoint that can be obtained by the user through the description
                    property of the endpointconfig instance
        :param path_description: a dictionary that provides a description for each path parameter.
       
        '''
        self.path = path
        self.description = description
        self.path_description = path_description
        self.method = method
        self.parameters = parameters or {}
        self.headers = headers

        #  we cannot set default processor above in the parameters as this means all endpoints
        #  share the same processor instance, and they cross-contaminate . By setting this below
        #  we enforce recreation of a new unique Resource instance each time
        self.processor = processor or JSONResource()
        self.validate()

    # ----------------------------------------------------
    def validate(self):
        ''' Check quality of each parameter and its type.
        Each parameter is checked for type, and if a specific substructure is required
        then this is also introspected. Currently Method is limited to GET or POST for no reason other then
        no tests were conducted with PUT, HEAD etc etc
        
        :raises RestClientConfigurationError: No response is provided if there is no problem
        
        '''

        # description --------------------
        if self.description and not isinstance(self.description, str):
            raise RestClientConfigurationError("description is not a string")

        if self.path_description and not isinstance(self.path_description, dict):
            raise RestClientConfigurationError("path_description is not a dictionary")

        # path --------------------
        if not isinstance(self.path, list):
            raise RestClientConfigurationError("path is not a list")

        # headers  --------------------
        if self.headers:
            if not isinstance(self.headers, dict):
                raise RestClientConfigurationError("header is not a dict")
        else:
            self.headers = {}

        # method  --------------------
        if self.method not in ['GET', 'POST']:
            raise RestClientConfigurationError("method must be GET or POST")

        #  parameters -------------------------------
        if not isinstance(self.parameters, dict):
            raise RestClientConfigurationError("parameters must be dictionary")
        for key, val in self.parameters.items():
            if not isinstance(val, ParameterConfig):
                raise RestClientConfigurationError("Parameter '%s' must be ParameterConfig instance" % str(key))

        #  resource class ----------------------------------
        if self.processor:
            if not isinstance(self.processor, Resource):
                raise RestClientConfigurationError("processor must be subclass of RestResource")

        # integration tests ---------------------------------------------------
        if self.method == 'GET':
            for key in self.parameters:
                if self.parameters[key].call_location == 'body':
                    raise RestClientConfigurationError('body parameter not allowed in GET request')

    # --------------------------------------------------------------------------------------------
    def apply_default_headers(self, default):
        '''
        For internal use. Update endpoint parameters from a shared default. This allows the user to set
        e.g. headers that are applicable to multiple endpoints in a single activity.
        
        Note that this default only provides functionality for headers
        '''

        # check types
        if not isinstance(default, dict):
            raise RestClientConfigurationError('default must be a dictionary')

        # apply defaults
        def_head = default.copy()
        if self.headers:
            def_head.update(self.headers)
        self.headers = def_head

        # re-validate to be sure current data is OK
        self.validate()

    # ---------------------------------------------------------------------------------------------
    @property
    def path_parameters(self) -> list:
        """ Lists the (always required) path parameters for the specified REST API resource. THis list is obtained
        by checking the path list (['api','v2','{para}','details']) for items that are within curly brackets {}.
        These parameters are stripped and the remainder is added to the path parameter list

        :return: A list of the path parameters for the specified REST API resource
        """

        path_parameters = []
        for part in self.path:
            if part.startswith("{") and part.endswith("}"):
                path_parameters.append(part[1:-1])
        return path_parameters


    # ---------------------------------------------------------------------------------------------
    @property
    def query_parameter_groups(self) -> dict:
        """ Lists the different groups of query parameters for the specified
            REST API resource. When query parameters are in a group, only one of
            them can be used in a query at a time, unless the 'multiple' property
            has been used for every query parameter of that group.

        :return: A dictionary of the different groups (key) of query parameters (value, is list) for the specified REST API resource
        """

        result = defaultdict(list)
        if self.parameters:
            for key, item in self.parameters.items():
                assert isinstance(item, ParameterConfig)
                if item.exclusion_group:
                    result[item.exclusion_group].append(key)
        return dict(result)

    # ---------------------------------------------------------------------------------------------
    @property
    def query_parameters(self) -> dict:
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters
                    (value, a list) for the specified REST API resource. 
        """
        result = {"required": [], "optional": [], "multiple": []}
        for para_name, para_set in self.parameters.items():
            if para_set.required:
                result['required'].append(para_name)
            else:
                result['optional'].append(para_name)

            if para_set.multiple:
                result['multiple'].append(para_name)

        return result

    # --------------------------------------------------------------------------------------------
    @property
    def all_query_parameters(self):
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A list of parameters
            :rtype: ``list``
        """
        params = self.query_parameters
        return params["optional"] + params["required"]

    # --------------------------------------------------------------------------------------------
    @property
    def required_parameters(self):
        """ Lists the required parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``list``
        """
        return self.path_parameters + self.query_parameters["required"]

    # --------------------------------------------------------------------------------------------
    @property
    def multiple_parameters(self):
        """ Returns all parameters that can be used simultaneously

            :return: A list of parameters
            :rtype: ``list``
        """
        return self.query_parameters["multiple"]


    # --------------------------------------------------------------------------------------------
    @property
    def all_parameters(self):
        """ Aggregates all parameters into a single structure

            :return: A list of parameters
            :rtype: ``list``
        """
        all_parameters = self.all_query_parameters + self.path_parameters
        return all_parameters

    # ---------------------------------------------------------------------------------------------
    @property
    def as_dict(self) -> dict:
        """ show all parameters in path or query

            :return: A dictionary that contains required and optional parameters.
        """

        result = {"required": [], "optional": []}
        result["required"].extend(self.path_parameters)

        qp = self.query_parameters
        result["required"].extend(qp['required'])
        result["optional"].extend(qp["optional"])

        return result


    # ---------------------------------------------------------------------------------------------
    @property
    def defaults(self):
        """
        Returns a dict with all default parameters and their value
        :return: A dictionary
        :rtype: ``dict``
        """
        defaults = {x:y.default for x, y in self.parameters.items() if y.default}
        return defaults


#==================================================================================================
class APIConfig:
    '''
    Class to configure and validate endpoints
    '''

    authentication = None
    url = None
    verify_ssl = False

    def __init__(self):
        self.endpoints = self.get_list_of_endpoints()
        self.apply_defaults()
        self.validate()


    def apply_defaults(self):
        '''
        rotate throught the endpoints and apply the fedault settings
        '''
        if 'default_headers' in dir(self):
            for endpoint in self.endpoints.values():
                endpoint.apply_default_headers(self.default_headers)


    def validate(self):
        """
        Validates a resources configuration and raises appropriate exceptions
        """
        for resource_name, resource_config in self.endpoints.items():
            if resource_name == 'data':
                raise RestClientConfigurationError("resource name may not be named 'data'")

        # check url definition
        if not self.url:
            raise RestClientConfigurationError('url is not set')
        URLValidator().check(self.url, require_path=False)

        if not isinstance(self.verify_ssl, bool):
            raise RestClientConfigurationError('verify_ssl is not True or False')
        
        # optional auth module
        if self.authentication and not isinstance(self.authentication, AuthConfig):
            raise RestClientConfigurationError('authentication attribute is not an initiated instance of AuthConfig')


    def get_list_of_endpoints(self):
        '''
        returns a dictionary of all the defined endpoints
        '''
        endpoints_dict = {}
        dirlist = [x for x in dir(self) if not x.startswith('_')]
        for item in dirlist:
            endpoint = getattr(self, item)
            if endpoint.__class__ == ResourceConfig:
                endpoints_dict[item] = endpoint
        if not endpoints_dict:
            raise RestClientConfigurationError('no endpoints defined for this REST client at all!')
        return endpoints_dict
        #return []


