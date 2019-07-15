'''
Contains all the configuration classes to create a Rest Configuration
'''
from contracts import contract
from collections import defaultdict

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import six
from rest_client.auth import AuthConfig

disable_warnings(InsecureRequestWarning)


# ================================================================================================
## local imports
from rest_client.utils import string_type, string_type_or_none
from rest_client.exception import RestClientConfigurationError


# ================================================================================================
class ParameterConfig(object):
    '''
    contain and validate parameters for and endpoint
    '''

    def __init__(self, name, required=False, multiple=False,
                 exclusion_group=None, default=None, choices=None,
                 description=None, regex=None
                 ):
        '''
        parameter configuration class to segregate validation and allow separation of python and REST
        names

        Attributes:
            name: the 'remote' nam,e of the parameter. this name is what the REST resource actually gets to interpret
            required: if this parameter is ommitted in the qyery, throw an exception
            multiple: if set to True, the value of the query parameter is a list
            exclusion_group: parameters in the same exclusion group may not be used together
            default: the default entry if this parameter is not supplied
            choices: a list of possible values for this parameter
            description: any information about the parameter, such as data format
            regex: a validation regular expression to test input for this parameter
        '''

        self.name = name
        self.required = required
        self.multiple = multiple
        self.exclusion_group = exclusion_group
        self.default = default
        self.choices = choices
        self.regex = regex
        self.description = description
        self.validate_configuration()

    def as_dict(self):
        '''
        return the parameter set as a dictionary
        '''
        return self.__dict__


    def validate_configuration(self):
        '''
        check a set of rules to validate if the ParameterConfig is configured correctly
        '''
        if not isinstance(self.required, bool):
            raise RestClientConfigurationError('parameter "required" must be boolean')
        if not isinstance(self.multiple, bool):
            raise RestClientConfigurationError('parameter "multiple" must be boolean')
        if self.exclusion_group:
            if not isinstance(self.exclusion_group, six.string_types):
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
class EndPointConfig(object):
    '''
    contain and validate details for a REST endpoint
    '''

    def __init__(self, path, method, parameters=None, json=None, headers=None, return_class=None, description=None, path_description=None):
        '''
        Enforce the presence of some parameters, help with definition, and validate
        '''
        self.path = path
        self.description = description
        self.path_description = path_description
        self.method = method
        self.parameters = parameters
        self.json_options = json
        self.headers = headers
        self.return_class = return_class
        self.validate()

    # ----------------------------------------------------
    def validate(self):
        '''
        broker service for all validators
        '''
        self.validate_path()
        self.validate_headers()
        self.validate_method()
        self.validate_json()
        self.validate_parameters()
        self.validate_return_class()
        self.validate_description()

        # integration tests
        if self.method == 'GET':
            for key in self.parameters:
                if self.parameters[key].call_location != 'query':
                    raise RestClientConfigurationError('body parameter not allowed in GET request')

    # ----------------------------------------------------
    def validate_description(self):
        ''' parameter validation'''
        if self.description and not isinstance(self.description, str):
            raise RestClientConfigurationError("description is not a string")

        if self.path_description and not isinstance(self.path_description, dict):
            raise RestClientConfigurationError("path_description is not a dictionary")

    # ----------------------------------------------------
    def validate_path(self):
        ''' parameter validation'''
        if not isinstance(self.path, list):
            raise RestClientConfigurationError("path is not a list")

    # ----------------------------------------------------
    def validate_headers(self):
        ''' parameter validation'''
        if self.headers:
            if not isinstance(self.headers, dict):
                raise RestClientConfigurationError("header is not a dict")
        else:
            self.headers = {}

    # ----------------------------------------------------
    def validate_method(self):
        ''' parameter validation'''
        if self.method not in ['GET', 'POST']:
            raise RestClientConfigurationError("method must be GET or POST")

    # ----------------------------------------------------
    def validate_json(self):
        '''
        validate the configured json parameter
        '''
        if self.json_options:
            if not isinstance(self.json_options, dict):
                raise RestClientConfigurationError("json option is not a dictionary")

            for key in ['source_name', 'result_name']:
                if key in self.json_options:
                    if not isinstance(self.json_options[key], six.string_types):
                        raise RestClientConfigurationError("json.%s option is not a string" % key)
            if "root" in self.json_options:
                if not isinstance(self.json_options["root"], list):
                    raise RestClientConfigurationError("json.root option is not a list")
        else:
            self.json_options = {}

    # ----------------------------------------------------
    def validate_parameters(self):
        '''
        validation of the GET and POST parameters
        '''

        if self.parameters:
            if not isinstance(self.parameters, dict):
                raise RestClientConfigurationError("parameters must be dictionary")
            for key, val in self.parameters.items():
                if not isinstance(val, ParameterConfig):
                    raise RestClientConfigurationError("Parameter '%s' must be ParameterConfig instance" % str(key))
        else:
            self.parameters = {}

    # ----------------------------------------------------
    def validate_return_class(self):
        '''
        This validation generates circular import and all kinds of interesting behaviour
        This routine is here to indicate that this validation is deliberatley ignored, and
        passed on to the restresource config itself

        '''

        pass

    # --------------------------------------------------------------------------------------------
    def apply_default(self, default):
        '''
        create a combined object that includes default configurations. For internal use.
        Note that this default only provides functionality for
        * method
        * headers
        * json
        '''

        # check
        allowed_default = ['headers', 'json']
        if not isinstance(default, dict):
            raise RestClientConfigurationError('default must be a dictionary')

        if set(default.keys()) - set(allowed_default):
            raise RestClientConfigurationError('default config may only contain %s' % ', '.join(allowed_default))

        # apply defaults
        if 'headers' in default:
            def_head = default['headers'].copy()
            if self.headers:
                def_head.update(self.headers)
            self.headers = def_head
        if 'json' in default:
            def_json = default['json'].copy()
            if self.json_options:
                def_json.update(self.json_options)
            self.json_options = def_json

        # re-validate to be sure current data is OK
        self.validate()

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def path_parameters(self):
        """ Lists the (always required) path parameters for the specified REST API resource

            #:param resource: A string that represents the REST API resource
            #:type resource: ``string_type``

            :return: A list of the (always required) path parameters for the specified REST API resource
            :rtype: ``list(string_type)``
        """

        path_parameters = []
        for part in self.path:
            if part.startswith("{") and part.endswith("}"):
                path_parameters.append(part[1:-1])
        return path_parameters


    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def query_parameter_groups(self):
        """ Lists the different groups of query parameters for the specified
            REST API resource. When query parameters are in a group, only one of
            them can be used in a query at a time, unless the 'multiple' property
            has been used for every query parameter of that group.

            :return: A dictionary of the different groups (key) of query parameters (value, is list) for the specified REST API resource
            :rtype: ``dict``
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
    @contract
    def query_parameters(self):
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``dict``
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
    @contract
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
    @contract
    def required_parameters(self):
        """ Lists the required parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``list``
        """
        return self.path_parameters + self.query_parameters["required"]

    # --------------------------------------------------------------------------------------------
    @property
    @contract
    def multiple_parameters(self):
        """ Returns all parameters that can be used simultaneously

            :return: A list of parameters
            :rtype: ``list``
        """
        return self.query_parameters["multiple"]


    # --------------------------------------------------------------------------------------------
    @property
    @contract
    def all_parameters(self):
        """ Aggregates all parameters into a single structure

            :return: A list of parameters
            :rtype: ``list``
        """
        all_parameters = self.all_query_parameters + self.path_parameters
        return all_parameters

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def as_dict(self):
        """ show all parameters in path or query

            :return: A dictionary that contains required and optional parameters.
            :rtype: ``dict``
        """

        result = {"required": [], "optional": []}
        result["required"].extend(self.path_parameters)

        qp = self.query_parameters
        result["required"].extend(qp['required'])
        result["optional"].extend(qp["optional"])

        return result


    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def defaults(self):
        """
        Returns a dict with all default parameters and their value
        :return: A dictionary
        :rtype: ``dict``
        """
        defaults = {x:y.default for x, y in self.parameters.items() if y.default}
        return defaults


#==================================================================================================
class RESTConfiguration(object):
    '''
    Class to configure and validate endpoints
    '''

    def __init__(self):
        self.endpoints = self.get_list_of_endpoints()
        self.apply_defaults()
        self.validate()


    def apply_defaults(self):
        '''
        rotate throught the endpoints and apply the fedault settings
        '''
        if 'default' in dir(self):
            for endpoint in self.endpoints.values():
                endpoint.apply_default(self.default)


    def validate(self):
        """
        Validates a resources configuration and raises appropriate exceptions
        """
        for resource_name, resource_config in self.endpoints.items():
            if not isinstance(resource_name, six.string_types):
                raise RestClientConfigurationError("resource name '{resource}' is not a string".format(
                    resource=resource_name
                ))
            if resource_name == 'data':
                raise RestClientConfigurationError("resource name may not be named 'data'")
            if not isinstance(resource_config, EndPointConfig):
                raise RestClientConfigurationError("endpoint {resource} must be class EndPointConfig".format(
                    resource=resource_name
                ))

    def get_list_of_endpoints(self):
        '''
        returns a dictionary of all the defined endpoints
        '''
        endpoints_dict = {}
        dirlist = [x for x in dir(self) if not x.startswith('_')]
        for item in dirlist:
            endpoint = getattr(self, item)
            if endpoint.__class__ == EndPointConfig:
                endpoints_dict[item] = endpoint
        if not endpoints_dict:
            raise RestClientConfigurationError('no endpoints defined for this REST client at all!')
        return endpoints_dict
        #return []


    # ===========================================================================
    def get_authentication_module(self, rest_client):
        '''
        return activated auth module for authentication
        '''

        from rest_client import RestClient
        assert isinstance(rest_client, RestClient)

        try:
            auth_config = self.authentication
        except AttributeError:
            # default to no authentication
            return None
        else:
            if auth_config is None:
                return None
            if not isinstance(auth_config, AuthConfig):
                raise RestClientConfigurationError('authentication attribute is not an instance of AuthConfig')
            auth_module = auth_config.authentication_module
            return auth_module(rest_client, auth_config)
