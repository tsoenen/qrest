import requests
import copy
import six

#local imports
from .utils import URLValidator
from .utils import contract, new_contract, string_type, string_type_or_none

@contract
def validate_resources_configuration(resources={}):
    """ Validates a resources configuration and raises appropriate exceptions

        :param resources: The object that represents the REST API resources
        :type resources: ``dict``
    """
    for resource in resources:
        if not isinstance(resource, six.string_types):
            raise ValueError("resource name '{resource}' is not a string".format(
                resource=resource
            ))
        if "path" in resources[resource]:
            if not isinstance(resources[resource]["path"], list):
                raise ValueError("path for resource '{resource}' is not a list".format(
                    resource=resource
                ))
            for part in resources[resource]["path"]:
                if not isinstance(part, six.string_types):
                    raise ValueError("part '{part}' of path for resource '{resource}' is not a string".format(
                        resource=resource,
                        part=part
                    ))
                elif part == "{data}":
                    raise SyntaxError("'data' isn't a valid path parameter name for resource '{resource}'".format(
                        resource=resource
                    ))
        if "method" in resources[resource]:
            if not isinstance(resources[resource]["method"], six.string_types):
                raise ValueError("method for resource '{resource}' is not a string".format(
                    resource=resource
                ))
        if "query_parameters" in resources[resource]:
            if not isinstance(resources[resource]["query_parameters"], list):
                raise ValueError("query parameters for resource '{resource}' is not a list".format(
                    resource=resource
                ))
            for parameter in resources[resource]["query_parameters"]:
                if not isinstance(parameter, dict):
                    raise ValueError("not all query parameters for resource '{resource}' are a dictionary".format(
                        resource=resource
                    ))
                if "name" in parameter:
                    if not isinstance(parameter["name"], six.string_types):
                        raise ValueError("not all query parameter names for resource '{resource}' are a string".format(
                            resource=resource
                        ))
                    elif parameter["name"] == "data":
                        raise SyntaxError("'data' isn't a valid query parameter name for resource '{resource}'".format(
                            resource=resource
                        ))
                else:
                    raise SyntaxError("not all query parameters for resource '{resource}' have a name".format(
                        resource=resource
                    ))
                if "group" in parameter:
                    if not isinstance(parameter["group"], six.string_types):
                        raise ValueError("not all query parameter group names for resource '{resource}' are a string".format(
                            resource=resource
                        ))
                if "required" in parameter:
                    if not isinstance(parameter["required"], bool):
                        raise ValueError("not all query parameter 'required' options for resource '{resource}' are a boolean".format(
                            resource=resource
                        ))
                if "multiple" in parameter:
                    if not isinstance(parameter["multiple"], bool):
                        raise ValueError("not all query parameter 'multiple' options for resource '{resource}' are a boolean".format(
                            resource=resource
                        ))
        if "json" in resources[resource]:
            if not isinstance(resources[resource]["json"], dict):
                raise ValueError("json option for resource '{resource}' is not a dictionary".format(
                    resource=resource
                ))
            if "root" in resources[resource]["json"]:
                if not isinstance(resources[resource]["json"]["root"], list):
                    raise ValueError("json.root option for resource '{resource}' is not a list".format(
                        resource=resource
                    ))
                for key in resources[resource]["json"]["root"]:
                    if not isinstance(key, six.string_types):
                        raise ValueError("not all json.root list elements for resource '{resource}' are a string".format(
                            resource=resource,
                            key=key
                        ))
            if "source_name" in resources[resource]["json"]:
                if not isinstance(resources[resource]["json"]["source_name"], six.string_types):
                    raise ValueError("json.source_name option for resource '{resource}' is not a string".format(
                        resource=resource
                    ))
            if "result_name" in resources[resource]["json"]:
                if not isinstance(resources[resource]["json"]["result_name"], six.string_types):
                    raise ValueError("json.result_name option for resource '{resource}' is not a string".format(
                        resource=resource
                    ))


class RestResponse(object):

    def __init__(self, response, options={}):
        """ RestResponse constructor

            :param response: The Requests Response object

            :param options: The options object specifying the JSON options for returning results
            :type options: ``dict``

        """
        self.response = response
        self.response.raise_for_status()
        self.headers = response.headers
        self.content = response.content
        self.options = options

    def is_json(self):
        """ Checks whether the Requests Response object contains JSON or not

            :return: True when the Requests Response object contains JSON and False when it does not
            :rtype: ``bool``
        """
        if ('content-type' in self.headers) and ("json" in self.headers['content-type']):
            return True
        else:
            return False

    def to_json(self):
        """ Returns the JSON contained in the Requests Response object, following the options specified in the JSON configuration

            :return: A dictionary containing the Requests Response object, adapted to the JSON configuration
            :rtype: ``dict``
        """
        json = copy.deepcopy(self.response.json())
        json_source = copy.deepcopy(self.response.json())
        if isinstance(json, dict):
            if ("root" in self.options) and (len(self.options["root"]) > 0):
                for element in self.options["root"]:
                    if element in json:
                        json = json[element]
                    else:
                        raise ValueError("")
        if not isinstance(json, dict):
            json_dict = {}
            if "result_name" in self.options:
                json_dict[self.options["result_name"]] = json
            else:
                json_dict["result"] = json
        else:
            json_dict = json

        if ("root" in self.options) and (len(self.options["root"]) > 0):
            if "source_name" in self.options:
                json_dict[self.options["source_name"]] = json_source
            elif "source" not in json_dict:
                json_dict["source"] = json_source
            else:
                json_dict["_source"] = json_source
        return json_dict

    def to_python(self):
        """ Returns the response body content contained in the Requests Response object.
            If the content is JSON, then the JSON content is returned adapted to the JSON configuration.
            If the content is not JSON, then the raw response body content is returned (in bytes).

            :return: A dictionary containing the response body JSON content, adapted to the JSON configuration or the raw response body content in bytes if it is not JSON
        """
        if self.is_json():
            return self.to_json()
        else:
            return self.content


class ResourceParameters():
    '''
    Wrapper for the parameter handling, this allows the RestResource to focus on the execution
    Code here is collected from multiple location, it hasnt been refactored but shows the redundancy
    in the original code.
    '''
    
    def __init__(self, config):
        self.config = config
        
        # although all functions below are properties, it may be more CPU friendly to 
        # store the result locally instead.
        self.path_parameters = self._path_parameters
        self.query_parameters = self._query_parameters
        self.multiple_parameters = self.query_parameters["multiple"]
        self.query_parameter_groups = self._query_parameter_groups
        self.required_parameters = self._required_parameters
        self.all_query_parameters = self._all_query_parameters
        self.all_parameters = self._all_parameters
        

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def all_parameter(self):
        """ show all parameters in path or query

            :return: A dictionary that contains required and optional parameters.
            :rtype: ``dict``
        """

        # TODO: show that a parameter is a list/multiple?
        result = {"required": [], "optional": []}
        result["required"].extend(self.path_parameters)
        result["required"].extend(self.query_parameters["required"])
        result["optional"].extend(self.query_parameters["optional"])
        
        return result

    # --------------------------------------------------------------------------------------------
    @property
    @contract
    def _required_parameters(self):
        """ Lists the required parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``list``
        """
        required_parameters = []
        required_parameters.extend(self.path_parameters)
        required_parameters.extend(self.query_parameters["required"])
        return required_parameters


    # --------------------------------------------------------------------------------------------
    @property
    @contract
    def _all_query_parameters(self):
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A list of parameters
            :rtype: ``list``
        """
        all_query_parameters = []
        all_query_parameters.extend(self.query_parameters["optional"])
        all_query_parameters.extend(self.query_parameters["required"])
        return all_query_parameters

    # --------------------------------------------------------------------------------------------
    @property
    @contract
    def _all_parameters(self):
        """ Aggregates all parameters into a single structure

            :return: A list of parameters
            :rtype: ``list``
        """
        all_query_parameters = []
        all_parameters = []
        all_parameters.extend(self.all_query_parameters)
        all_parameters.extend(self.path_parameters)
        all_parameters.append("data")  # data (request body) can be a parameter as well
        
        return all_parameters


    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def _query_parameters(self):
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``dict``
        """
        result = {"required": [], "optional": [], "multiple": []}
        if "query_parameters" in self.config:
            for parameter in self.config["query_parameters"]:
                if ("required" in parameter) and (parameter["required"] is True):
                    result["required"].append(parameter["name"])
                else:
                    result["optional"].append(parameter["name"])
                if ("multiple" in parameter) and (parameter["multiple"] is True):
                    result["multiple"].append(parameter["name"])
        return result

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def _query_parameter_groups(self):
        """ Lists the different groups of query parameters for the specified
            REST API resource. When query parameters are in a group, only one of
            them can be used in a query at a time, unless the 'multiple' property
            has been used for every query parameter of that group.

            :return: A dictionary of the different groups (key) of query parameters (value, is list) for the specified REST API resource
            :rtype: ``dict``
        """

        result = {}
        if "query_parameters" in self.config:
            for parameter in self.config["query_parameters"]:
                # TODO: check if string, maybe also support int?
                if ("group" in parameter) and (parameter["group"].strip() != ""):
                    if parameter["group"] not in result:
                        result[parameter["group"]] = []
                    result[parameter["group"]].append(parameter["name"])
        return result

    # ---------------------------------------------------------------------------------------------
    @property
    @contract
    def _path_parameters(self):
        """ Lists the (always required) path parameters for the specified REST API resource

            #:param resource: A string that represents the REST API resource
            #:type resource: ``string_type``

            :return: A list of the (always required) path parameters for the specified REST API resource
            :rtype: ``list(string_type)``
        """

        path_parameters = []
        if "path" in self.config:
            for part in self.config["path"]:
                if part.startswith("{") and part.endswith("}"):
                    path_parameters.append(part[1:-1])
        return path_parameters
    

class RestResource():
    '''
    A resource is defined as a single REST endpoint.
    This class wraps functionality of creating and querying this resources, starting with a
    configuration string
    '''
    
    def __init__(self, client, name, config):
        self.client = client
        self.config = config
        self.name = name
        self.path = self.config.get('path', [])
        self.method = self.config.get('method', 'GET')
        self.resource_parameters = ResourceParameters(config)
    
    # ---------------------------------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        # catch accidential positional arguments
        if args:
            raise SyntaxError("all parameters must by keyword arguments")
        
        return self._get_rest_data(**kwargs)

    #---------------------------------------------------------------------------------------------
    def validate_request(self, **kwargs):
        '''
        check the input request parameters before sending it to the remote service
        '''
        
        rp = self.resource_parameters
        
        diff = set(kwargs.keys()).difference(rp.all_parameters)
        if len(diff) > 0:
            raise SyntaxError("parameters {difference} are supplied but not usable for resource '{resource}'".format(
                difference=list(diff),
                resource=self.name
            ))
        request_parameters = {}
        # Resolve path parameters in path
        resolved_path = "/".join(self.path)
        for parameter in rp.required_parameters:
            if parameter not in kwargs.keys():
                raise SyntaxError("parameter '{parameter}' is missing for resource '{resource}'".format(
                    parameter=parameter,
                    resource=self.name
                ))
            if parameter in rp.path_parameters:
                resolved_path = resolved_path.format(**{parameter: kwargs[parameter]})

        # Construct URL using base URL and path
        url = "{url}/{path}".format(url=self.client.url, path=resolved_path)

        # Add request body data
        data = kwargs.get('data', None)

        # Check if valid URL
        # Only allow http or https schemes for the REST API base URL
        url_validator = URLValidator(schemes=["http", "https"])
        url_validator(url)


        # Prepare & check query parameters
        intersection = set(rp.all_query_parameters).intersection(kwargs.keys())
        groups_used = {}
        for kwarg in intersection:
            for group in rp.query_parameter_groups:
                if kwarg in rp.query_parameter_groups[group]:
                    if group in groups_used:
                        raise SyntaxError(
                            "parameter '{kwarg1}' and '{kwarg2}' from group '{group}' can't be used together".format(
                                kwarg1=kwarg,
                                kwarg2=groups_used[group],
                                group=group
                            ))
                    else:
                        groups_used[group] = kwarg
                    break
            # TODO: is this necessary? wouldn't we get HTTP 400?
            if isinstance(kwargs[kwarg], list) and kwarg not in rp.multiple_parameters:
                raise SyntaxError("parameter '{kwarg}' is not multiple".format(
                    kwarg=kwarg
                ))
            else:
                request_parameters[kwarg] = kwargs[kwarg]
        
        return {'url': url,
                'parameters': request_parameters,
                'data': data,
                }
        

    # ---------------------------------------------------------------------------------------------
    def _get_rest_data(self, **kwargs):
        """ This function builds and sends a request for a specified REST API resource.
            The parameters are validated dynamically, depending on the configuration of said REST API resource.
            It returns a dictionary of the response or throws an appropriate error, depending on the HTTP return code.
        """

        # JSON options
        json_options = self.config.get('json', {})
        
        # url and parameters
        validated_input = self.validate_request(**kwargs)
        

        # Do HTTP request to REST API
        try:
            response = requests.request(method=self.method,
                                        auth=self.client.auth,
                                        verify=self.client.verifySSL,
                                        url=validated_input['url'], 
                                        params=validated_input['parameters'],
                                        data=validated_input['data']
                                        )
            return RestResponse(response=response,
                                options=json_options).to_python()
        except ValueError:
            return response.content
        except requests.HTTPError as http:
            raise http

