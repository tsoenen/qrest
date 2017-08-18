import requests
import copy
import six
from contracts import contract

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


if six.PY2:
    from urllib import quote
elif six.PY3:
    from urllib.parse import quote
else:
    raise Exception('gvd')

# ================================================================================================
# local imports
from bcs_rest_client.validator import URLValidator
from bcs_rest_client.exception import BCSRestQueryError, BCSRestConfigurationError
from bcs_rest_client.exception import BCSRestResourceHTTPError, BCSRestResourceMissingContentError
from bcs_rest_client.conf import EndPointConfig

# =================================================================================================
class RestResponse(object):
    '''
    Wrapper around the REST response. This is meant to process the response coming from the requests
    call into a python object
    '''

    def __init__(self, response, options={}):
        """ RestResponse constructor

            :param response: The Requests Response object

            :param options: The options object specifying the JSON options for returning results
            :type options: ``dict``

        """
        assert isinstance(response, requests.models.Response)
        self._response = response
        #self._response.raise_for_status()
        self.headers = response.headers
        self.content = response.content
        self.options = options

        #prepare the content to a python object
        self.data = None
        self._to_python()

    @property
    def response_type(self):
        """ Checks whether the Requests Response object contains JSON or not

            :return: True when the Requests Response object contains JSON and False when it does not
            :rtype: ``bool``
        """

        content_type = self.headers.get('content-type', 'unknown')

        if "json" in content_type:
            return 'json'
        elif 'text/csv' in content_type:
            return 'csv'
        else:
            return 'unknown'

    def _parse_json_response(self):
        """ Returns the JSON contained in the Requests Response object, following the options specified in the JSON configuration

            :return: A dictionary containing the Requests Response object, adapted to the JSON configuration
            :rtype: ``dict``
        """
        json = copy.deepcopy(self._response.json())
        json_source = copy.deepcopy(self._response.json())

        result_name = self.options.get("result_name", "result")

        #subset the response dictionary
        if isinstance(json, dict):
            if ("root" in self.options) and (len(self.options["root"]) > 0):
                for element in self.options["root"]:
                    if element in json:
                        json = json[element]
                    else:
                        raise BCSRestResourceMissingContentError("Element '%s' could not be found" % element)

        # look into the subset JSON: stick it into the self object
        if not isinstance(json, dict):
            json_dict = {}
            json_dict[result_name] = json
        else:
            json_dict = json

        #
        if ("root" in self.options) and (len(self.options["root"]) > 0):
            if "source_name" in self.options:
                json_dict[self.options["source_name"]] = json_source
            elif "source" not in json_dict:
                json_dict["source"] = json_source
            else:
                json_dict["_source"] = json_source

        # replace content by decoded content
        self.content = json_source

        #create data objects
        self.data = json_dict
        setattr(self, result_name, json)

    def _parse_csv_response(self):
        '''
        processes a raw CSV into lines. For very large content this may be better served by a generator

        : return:  a list of lists
        '''
        data = self._response.content
        self.content = data.decode('UTF-8')
        data = self.content.strip().split('\n')
        self.data = [x.split(",") for x in data]

    def _to_python(self):
        """ Returns the response body content contained in the Requests Response object.
            If the content is JSON, then the JSON content is returned adapted to the JSON configuration.
            If the content is not JSON, then the raw response body content is returned (in bytes).

            :return: A dictionary containing the response body JSON content, adapted to the JSON configuration or the raw response body content in bytes if it is not JSON
        """
        if self.response_type == 'json':
            self._parse_json_response()
        elif self.response_type == 'csv':
            self._parse_csv_response()


# ===================================================================================================
class RestResource():
    '''
    A resource is defined as a single REST endpoint.
    This class wraps functionality of creating and querying this resources, starting with a
    configuration string
    '''

    def __init__(self, client, name, config):
        self.client = client
        self.name = name

        assert isinstance(config, EndPointConfig)

        self.config = config
        self.path = self.config.path
        self.method = self.config.method
        self.cleaned_data = {}

    # ---------------------------------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        '''
        runs the REST query using supplied arguments, checks input quality and format the REST
        parameters.
        '''

        self.cleaned_data = {}
        self.validate_query(**kwargs)
        return self._get()

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def parameters(self):
        '''
        return the configuration parameters for this rest resource
        :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list)
        :rtype: ``dict``

        '''
        return self.config.as_dict


    #---------------------------------------------------------------------------------------------
    def validate_query(self, *args, **kwargs):
        '''
        check the input request parameters before sending it to the remote service
        '''

        rp = self.config

        #----------------------------------
        # deny superfluous input
        if args:
            raise BCSRestQueryError("all parameters must be keyword arguments")

        diff = set(kwargs.keys()).difference(rp.all_parameters)
        if len(diff) > 0:
            raise BCSRestQueryError("parameters {difference} are supplied but not usable for resource '{resource}'".format(
                difference=list(diff),
                resource=self.name
            ))

        #----------------------------------
        # Check required parameters
        for parameter in rp.required_parameters:
            if parameter not in kwargs:
                raise BCSRestQueryError("parameter '{parameter}' is missing or empty for resource '{resource}'".format(
                    parameter=parameter,
                    resource=self.name
                ))

        #----------------------------------
        # check choices
        for parameter in kwargs.keys():
            if not parameter in self.config.parameters:
                continue
            config = self.config.parameters[parameter]
            if config.choices:
                if not kwargs[parameter] in config.choices:
                    raise BCSRestQueryError("value '{val}' for parameter '{parameter}' is not a valid choice: pick from {choices}".format(
                        val = kwargs[parameter],
                        parameter=parameter,
                        choices=', '.join(config.choices))
                    )

        #----------------------------------
        # check query parameters
        intersection = set(rp.all_query_parameters).intersection(kwargs.keys())
        groups_used = {}
        for kwarg in intersection:
            for group in rp.query_parameter_groups:
                if kwarg in rp.query_parameter_groups[group]:
                    if group in groups_used:
                        raise BCSRestQueryError(
                            "parameter '{kwarg1}' and '{kwarg2}' from group '{group}' can't be used together".format(
                                kwarg1=kwarg,
                                kwarg2=groups_used[group],
                                group=group
                            ))
                    else:
                        groups_used[group] = kwarg
                    break
            if isinstance(kwargs[kwarg], list) and kwarg not in rp.multiple_parameters:
                raise BCSRestQueryError("parameter '{kwarg}' is not multiple".format(
                    kwarg=kwarg
                ))


        # apply defaults for missing optional parameters that do have default values
        defaults = self.config.defaults
        for item, value in defaults.items():
            if not item in kwargs:
                kwargs[item] = value


        self.cleaned_data = kwargs

    #---------------------------------------------------------------------------------------------
    @property
    def query_url(self):
        # construct the URL path
        rp = self.config

        # url and parameters
        if not 'cleaned_data' in dir(self):
            raise KeyError('request data is not cleaned. Run validate_request first')


        resolved_path = "/".join(self.path)
        path_para = {parameter: quote(self.cleaned_data[parameter], safe='') for parameter in self.cleaned_data if parameter in rp.path_parameters}
        resolved_path = resolved_path.format(**path_para)

        # Construct URL using base URL and path
        url = "{url}/{path}".format(url=self.client.url, path=resolved_path)

        # Check if valid URL
        # Only allow http or https schemes for the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        url_validator(url)

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
                raise BCSRestConfigurationError('call location for %s is not understood' % para_name)

        # collect and return
        qp = {'request': request_parameters,
              'body': body_parameters,
              }



        return qp


    # ---------------------------------------------------------------------------------------------
    def _get(self, extra_request=None, extra_body=None):
        """ This function builds and sends a request for a specified REST API resource.
            The parameters are validated in a previous call to validate_query().
            It returns a dictionary of the response or throws an appropriate error, depending on the HTTP return code.
        """

        # url and parameters
        if not 'cleaned_data' in dir(self):
            raise KeyError('request data is not cleaned. Run validate_query first')

        query_parameters = self.query_parameters

        # add hooks to extend get function
        for location, data_dict in [('request', extra_request), ('body', extra_body)]:
            if not data_dict:
                continue
            if not isinstance(data_dict, dict):
                raise BCSRestQueryError('extra_request and extra_body must be dict')
            for item in data_dict.keys():
                if item in query_parameters[location]:
                    raise BCSRestQueryError('trying to overload parameter ' + item )
            query_parameters[location].update(data_dict)

        # Do HTTP request to REST API
        try:
            response = requests.request(method=self.method,
                                        auth=self.client.auth,
                                        verify=self.client.verifySSL,
                                        url=self.query_url,
                                        params=query_parameters['request'],
                                        json=query_parameters['body'],
                                        headers=self.config.headers
                                        )
            assert isinstance(response, requests.Response)

            if response.status_code > 399:  #Nicely catch exceptions
                raise BCSRestResourceHTTPError(response_object=response)
            # for completeness sake: let requests check for valid output
            # code should not get here...
            response.raise_for_status()
        except ValueError as e:
            # Weird response errors: just give back the raw data. This has the risk of dismissing
            # valid errors!
            return response.content
        except requests.HTTPError as http:
            # This is a back-catcher for HTTP errors that were not caught before. Code shoul
            # not get here
            raise http
        else:
            return RestResponse(response=response, options=self.config.json_options)


