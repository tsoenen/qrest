'''
The main working module of the package: contains the API class (which creates the ORM for a
RES server), and the Resource class (which wraps around a single endpoint / resources ). The Resource
class is encouraged to be subclassed to add functionality such as complex pagination or response processing

'''

import importlib
import requests
import logging
from urllib.parse import quote, urljoin
from abc import ABC, abstractmethod
from typing import Optional, Type

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

# ================================================================================================
# local imports
from .utils import URLValidator
from .exception import RestClientQueryError, RestClientConfigurationError, RestLoginError, RestResourceHTTPError, InvalidResourceError
from .response import JSONResponse

logger = logging.getLogger(__name__)

# ================================================================================================
class API:
    '''
    This is the main point of contact for end users
    '''

    # placeholder for subclassed resources
    config = None
    auth = None

    def __init__(self, config):
        """
        REST Client constructor
        
        :param config: The configuration object of the REST API resources
        :type config: Subclass of APIConfig
        
        An API describes a REST server, and contains a list of resources. 
        We allow customization of the "resource class", which is basically
        a wrapper around the response object: default is JSON, so we pre-made a JSON resource class.
        Optionally this resource class handles non-standard responses such as pagination or a
        specific response format from which the payload needs to be derived
        """

        # check
        from .conf import APIConfig
        if not isinstance(config, APIConfig):
            raise RestClientConfigurationError('configuration is not a APIConfig instance')


        self.config = config
        self.verifySSL = config.verify_ssl
        self.auth = config.authentication

        #  process the endpoints
        for name, item_config in self.config.endpoints.items():
            if not isinstance(item_config.processor, Resource):
                raise RestClientConfigurationError(f'defined resource class for {ep} is not a Resource instance')
            new_resource = self._create_rest_resource(item_config.processor,
                                                      resource_name=name,
                                                      config=item_config)
            setattr(self, name, new_resource)
            xx = 1
        x = 1


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
            if isinstance(field, Resource):
                resources.append(field.name)
        return resources


    # ---------------------------------------------------------------------------------------------
    def _create_rest_resource(self, processor, resource_name, config):
        """ This function is used to dynamically create request functions for a specified REST API resource

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A function that builds and sends a request for the specified REST API resource and validates the function call
            :rtype: ``list(string_type)``
        """

        if not config:
            raise InvalidResourceError(name=type(self).__name__, resource=resource_name)

        if not isinstance(processor, Resource):
            raise RestClientConfigurationError('processor must be a class instance')

        processor.configure(name=resource_name, config=config, server_url=self.config.url)
        return processor


# ===================================================================================================
class Resource(ABC):
    '''
    A resource is defined as a single REST endpoint.
    This class wraps functionality of creating and querying this resources, starting with a
    configuration string
    '''

    is_configured = False
    config = None

    server_url = None
    request_parameters = None
    verify_ssl = False
    auth = None
    cleaned_data = None
    
    response_class = None

    @abstractmethod
    def __init__(self):
        ''' ABC to set response parameters during configuration
        '''

    # ---------------------------------------------------------------------------------------------
    def configure(self,
                  name: str,
                  server_url: str,
                  config,
                  auth=None,
                  verify_ssl: bool = False
                  ):
        ''' Configure the resource. This is a required procedure to set all parameters.
        Setting these parameters is not possible by using __init__, because this class is initialized
        within the config, to enable setting custom parameters instead
        
        :param name: the pythonic name of this resource (i.e. my own name). Used to generate error messages
        :param server_url: the base server URL (e.g. http://localhost:8080)
        :param verify_ssl: boolean to set verify_ssl in the request on or off
        :param auth: Which Authentication module to use
        :type auth: subclass of AuthConfig 
        :param config: which ResourceConfiguration to use
        :type config: subclass of ResourceConfig 
        '''

        self.name = name
        self.server_url = server_url
        self.config = config
        self.auth = auth
        self.verify_ssl = verify_ssl
        
        self.cleaned_data = {}
        self.request_parameters = None
        self.is_configured = True
        

    # ---------------------------------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        '''
        runs the REST query using supplied arguments, checks input quality and format the REST
        parameters.
        '''

        self.cleaned_data = {}
        self.check(**kwargs)
        return self._get()


    # ---------------------------------------------------------------------------------------------
    def fetch(self, *args, **kwargs):
        '''
        shortcut function to immedaitely deliver the content of the response insetead of the response object itself
        '''
        response = self.__call__(*args, **kwargs)
        return response.fetch()

    # ---------------------------------------------------------------------------------------------
    @property
    def parameters(self) -> dict:
        '''
        return the configuration parameters for this rest resource
        :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list)

        '''
        return self.config.as_dict

    #---------------------------------------------------------------------------------------------
    @property
    def description(self) -> str:
        '''
        shortcut to provide a description of the endpoint
        '''
        return self.help()


    def help(self, parameter_name: Optional[str]=None):
        '''
        Print description of the endpoint and the parameters
        :param parameter_name: Optional parameter name to request the help text of
        '''
        if not parameter_name:
            return (self.config.description or 'No description given for this endpoint')
        if parameter_name not in self.config.all_parameters:
            if self.config.all_parameters:
                return '%s is not a valid parameter: valid are: %s' % (parameter_name, ','.join(self.config.all_parameters))
            else:
                return 'this endpoint has no parameters'
        if parameter_name in self.config.parameters:
            param_help = self.config.parameters[parameter_name].description
            choices = self.config.parameters[parameter_name].choices
            if choices:
                param_help += '. Valid choices are: %s' % ', '.join(choices)
            return (param_help or 'no description given for this parameter')
        if parameter_name in self.config.path_parameters:
            param_help = self.config.path_description.get(parameter_name, 'no description given for this parameter')
            return param_help
        return 'ERROR: not yet implemented'


    #---------------------------------------------------------------------------------------------
    def check(self, **kwargs):
        '''
        check the input request parameters before sending it to the remote service
        '''

        conf = self.config

        #----------------------------------
        # deny superfluous input
        diff = list(set(kwargs.keys()).difference(conf.all_parameters))
        if diff:
            raise RestClientQueryError("parameters {difference} are supplied but not usable for resource '{resource}'".format(
                difference=diff,
                resource=self.name
            ))

        #----------------------------------
        # Check required parameters
        for parameter in conf.required_parameters:
            if parameter not in kwargs:
                raise RestClientQueryError("parameter '{parameter}' is missing or empty for resource '{resource}'".format(
                    parameter=parameter,
                    resource=self.name
                ))

        #----------------------------------
        # check choices
        for parameter in kwargs:
            if parameter not in self.config.parameters:
                continue
            config = self.config.parameters[parameter]
            if config.choices:
                if not kwargs[parameter] in config.choices:
                    raise RestClientQueryError("value '{val}' for parameter '{parameter}' is not a valid choice: pick from {choices}".format(
                        val = kwargs[parameter],
                        parameter=parameter,
                        choices=', '.join(config.choices))
                                               )

        #----------------------------------
        # check query parameters
        intersection = set(conf.all_query_parameters).intersection(kwargs.keys())
        groups_used = {}
        for kwarg in intersection:
            for group in conf.query_parameter_groups:
                if kwarg in conf.query_parameter_groups[group]:
                    if group in groups_used:
                        raise RestClientQueryError(
                            "parameter '{kwarg1}' and '{kwarg2}' from group '{group}' can't be used together".format(
                                kwarg1=kwarg,
                                kwarg2=groups_used[group],
                                group=group
                            ))
                    else:
                        groups_used[group] = kwarg
                    break
            if isinstance(kwargs[kwarg], list) and kwarg not in conf.multiple_parameters:
                raise RestClientQueryError("parameter '{kwarg}' is not multiple".format(
                    kwarg=kwarg
                ))


        # apply defaults for missing optional parameters that do have default values
        defaults = self.config.defaults
        for item, value in defaults.items():
            if item not in kwargs:
                kwargs[item] = value


        self.cleaned_data = kwargs

    #---------------------------------------------------------------------------------------------
    @property
    def query_url(self):
        '''
        returns the URL that is actually queried
        '''

        # url and parameters
        if 'cleaned_data' not in dir(self):
            raise KeyError('request data is not cleaned. Run validate_request first')


        resolved_path = "/".join(self.config.path)
        selected_params = [parameter for parameter in self.cleaned_data if parameter in self.config.path_parameters]
        path_para = {p: quote(str(self.cleaned_data[p]), safe='') for p in selected_params}
        resolved_path = resolved_path.format(**path_para)

        # Construct URL using base URL and path
        url = urljoin(base=self.server_url, url=resolved_path)

        # Check if valid URL
        # Only allow http or https schemes for the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        url_validator.check(url)

        return url

    # ---------------------------------------------------------------------------------------------
    @property
    def query_parameters(self):
        '''
        generate the request and body parameters based on the validated input and the config
        '''
        request_parameters = {}
        body_parameters = {}

        # process via the config
        config_parameters = self.config.parameters
        for para_name, para_val in self.cleaned_data.items():
            if para_name in self.config.path_parameters:
                continue
            rest_name = config_parameters[para_name].name
            if config_parameters[para_name].call_location == 'query':
                request_parameters[rest_name] = para_val
            elif config_parameters[para_name].call_location == 'body':
                body_parameters[rest_name] = para_val
            else:
                raise RestClientConfigurationError('call location for %s is not understood' % para_name)

        # collect and return
        return_structure = {'request': request_parameters,
                            'body': body_parameters,
                            }

        return return_structure

    # ---------------------------------------------------------------------------------------------
    def _get(self, extra_request=None, extra_body=None):
        """ This function builds and sends a request for a specified REST API resource.
            The parameters are validated in a previous call to validate_query().
            It returns a dictionary of the response or throws an appropriate
            error, depending on the HTTP return code.
            
            This should be the *only* place in the module where the Requests module is called!
            
        """

        # check if user is logged in
        if self.auth and not self.auth.is_logged_in:
            raise RestLoginError('user is not logged in')

        # url and parameters
        if 'cleaned_data' not in dir(self):
            raise KeyError('request data is not cleaned. Run validate_query first')

        query_parameters = self.query_parameters

        # add hooks to extend get function
        for location, data_dict in [('request', extra_request), ('body', extra_body)]:
            if not data_dict:
                continue
            if not isinstance(data_dict, dict):
                raise RestClientQueryError('extra_request and extra_body must be dict')
            for item in data_dict.keys():
                if item in query_parameters[location]:
                    raise RestClientQueryError('trying to overload parameter ' + item)
            query_parameters[location].update(data_dict)

        # Do HTTP request to REST API
        logger.debug('[RESTCLIENT]: running %s' % self.query_url)
        try:
            response = requests.request(method=self.config.method,
                                        auth=self.auth,
                                        verify=self.verify_ssl,
                                        url=self.query_url,
                                        params=query_parameters['request'],
                                        json=query_parameters['body'],
                                        headers=self.config.headers
                                        )
            assert isinstance(response, requests.Response)

            if response.status_code > 399:  #Nicely catch exceptions
                raise RestResourceHTTPError(response_object=response)
            # for completeness sake: let requests check for valid output
            # code should not get here...
            response.raise_for_status()
        except ValueError:
            # Weird response errors: just give back the raw data. This has the risk of dismissing
            # valid errors!
            return response.content
        except requests.HTTPError as http:
            # This is a back-catcher for HTTP errors that were not caught before. Code shoul
            # not get here
            raise http
        else:
            r = self.response_class(response)
            return r


# ###############################################################
class JSONResource(Resource):
    """ A REST Resource that expects a JSON return
    
    """

    def __init__(self, *, extract_section: Optional[list] = None, create_attribute: Optional[str] = 'results'):
        '''
        :param extract_section: This indicates which part of the obtained JSON response contains the main
            payload that should be extracted. The tree is provided as a list of items to traverse
        :param create_attribute: The "results_name" which is the property that will be generated to contain
            the previously obtained subsection of the json tree
        '''

        self.response_class = JSONResponse(extract_section, create_attribute)


