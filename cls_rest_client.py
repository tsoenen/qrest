import requests
from django.core.validators import URLValidator
from contracts import contract, new_contract
import copy
import six

# Define new Python 2 & 3 compatible string contracts
string_type_or_none = new_contract(
    'string_type_or_none',
    lambda s: s is None or isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract that allows None as well. """

string_type = new_contract(
    'string_type',
    lambda s: isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract. """


class InvalidResourceError(KeyError):
    """An error when specifying an invalid resource for a given REST API."""
    def __init__(self, name, resource):
        """ InvalidResourceError constructor

            :param name: The name of the REST API client
            :type name: ``string``

            :param resource: The REST API resource name
            :type resource: ``string``

        """
        super("'{resource}' is not a valid resource for '{name}'".format(
            resource=resource,
            name=name
        ))


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


class RestClient(object):

    @contract
    def __init__(self, url, user="", password="", resources={}, verifySSL=False):
        """ RestClient constructor

            :param url: The base URL of the REST API
            :type url: ``string_type``

            :param user: The user for authenticating with the REST API
            :type user: ``string_type_or_none``

            :param password: The password for authenticating with the REST API
            :type password: ``string_type_or_none``

            :param resources: The configuration object of the REST API resources
            :type resources: ``dict``

            :param verifySSL: Whether the REST client should verify SSL certificates upon making a request
            :type verifySSL: ``bool``
        """

        # Only allow http or https schemes for the REST API base URL
        self.url_validator = URLValidator(schemes=["http", "https"])

        # Validate the REST API base URL
        self.url_validator.__call__(url)

        self.url = url

        if (user is not None) and (user.strip() != ""):
            if password is None:
                password = ''
            self.auth = (user, password)
        else:
            self.auth = None

        validate_resources_configuration(resources)
        self.resources = resources

        for resource in self.resources:
            setattr(RestClient, resource, self.create_request_function(
                resource=resource))

        self.verifySSL = verifySSL

    @contract
    def list_resources(self):
        """ Lists the available resources for this REST API

            :return: A list of the available resources for this REST API
            :rtype: ``list(string_type)``
        """

        keys = list(self.resources.keys())
        return keys

    @contract
    def list_parameters(self, resource):
        """ Lists the required and optional parameters for the specified REST API resource

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A dictionary of the 'optional' and 'required' (keys) parameters (value, a list) for the specified REST API resource
            :rtype: ``dict``
        """

        if resource not in self.resources:
            raise InvalidResourceError(name=type(self).__name__, resource=resource)

        # TODO: show that a parameter is a list/multiple?
        result = {"required": [], "optional": []}
        result["required"].extend(self.list_path_parameters(resource))
        query_parameters = self.list_query_parameters(resource)
        result["required"].extend(query_parameters["required"])
        result["optional"].extend(query_parameters["optional"])
        return result

    @contract
    def list_query_parameters(self, resource):
        """ Lists the required and optional query parameters for the specified REST API resource.
            Also summarises the query parameters that can be multiple.

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A dictionary of the 'optional', 'required' and 'multiple' (keys) query parameters (value, a list) for the specified REST API resource
            :rtype: ``dict``
        """
        if resource not in self.resources:
            raise InvalidResourceError(name=type(self).__name__, resource=resource)

        result = {"required": [], "optional": [], "multiple": []}
        if "query_parameters" in self.resources[resource]:
            for parameter in self.resources[resource]["query_parameters"]:
                if ("required" in parameter) and (parameter["required"] is True):
                    result["required"].append(parameter["name"])
                else:
                    result["optional"].append(parameter["name"])
                if ("multiple" in parameter) and (parameter["multiple"] is True):
                    result["multiple"].append(parameter["name"])
        return result

    @contract
    def list_query_parameter_groups(self, resource):
        """ Lists the different groups of query parameters for the specified
            REST API resource. When query parameters are in a group, only one of
            them can be used in a query at a time, unless the 'multiple' property
            has been used for every query parameter of that group.

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A dictionary of the different groups (key) of query parameters (value, is list) for the specified REST API resource
            :rtype: ``dict``
        """
        if resource not in self.resources:
            raise InvalidResourceError(name=type(self).__name__, resource=resource)

        result = {}
        if "query_parameters" in self.resources[resource]:
            for parameter in self.resources[resource]["query_parameters"]:
                # TODO: check if string, maybe also support int?
                if ("group" in parameter) and (parameter["group"].strip() != ""):
                    if parameter["group"] not in result:
                        result[parameter["group"]] = []
                    result[parameter["group"]].append(parameter["name"])
        return result

    @contract
    def list_path_parameters(self, resource):
        """ Lists the (always required) path parameters for the specified REST API resource

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A list of the (always required) path parameters for the specified REST API resource
            :rtype: ``list(string_type)``
        """
        if resource not in self.resources:
            raise InvalidResourceError(name=type(self).__name__, resource=resource)

        path_parameters = []
        if "path" in self.resources[resource]:
            for part in self.resources[resource]["path"]:
                if part.startswith("{") and part.endswith("}"):
                    path_parameters.append(part[1:-1])
        return path_parameters

    def create_request_function(self, resource):
        """ This function is used to dynamically create request functions for a specified REST API resource

            :param resource: A string that represents the REST API resource
            :type resource: ``string_type``

            :return: A function that builds and sends a request for the specified REST API resource and validates the function call
            :rtype: ``list(string_type)``
        """
        if resource not in self.resources:
            raise InvalidResourceError(name=type(self).__name__, resource=resource)

        if "method" in self.resources[resource]:
            method = self.resources[resource]["method"]
        else:
            method = "GET"
        if "path" in self.resources[resource]:
            path = self.resources[resource]["path"]
        else:
            path = []

        required_parameters = []
        all_query_parameters = []
        path_parameters = self.list_path_parameters(resource)
        query_parameters = self.list_query_parameters(resource)
        required_parameters.extend(path_parameters)
        required_parameters.extend(query_parameters["required"])
        multiple_parameters = query_parameters["multiple"]
        all_query_parameters.extend(query_parameters["optional"])
        all_query_parameters.extend(query_parameters["required"])
        all_parameters = []
        all_parameters.extend(all_query_parameters)
        all_parameters.extend(path_parameters)
        all_parameters.append("data")  # data (request body) can be a parameter as well
        groups = self.list_query_parameter_groups(resource)

        def function_template(self, **kwargs):
            """ This function builds and sends a request for a specified REST API resource.
                The parameters are validated dynamically, depending on the configuration of said REST API resource.
                It returns a dictionary of the response or throws an appropriate error, depending on the HTTP return code.
            """
            diff = set(kwargs.keys()).difference(all_parameters)
            if len(diff) > 0:
                raise SyntaxError("parameters {difference} are supplied but not usable for resource '{resource}'".format(
                    difference=list(diff),
                    resource=resource
                ))
            parameters = {}
            # Resolve path parameters in path
            resolved_path = "/".join(path)
            for parameter in required_parameters:
                if parameter not in kwargs.keys():
                    raise SyntaxError("parameter '{parameter}' is missing for resource '{resource}'".format(
                        parameter=parameter,
                        resource=resource
                    ))
                if parameter in path_parameters:
                    resolved_path = resolved_path.format(**{parameter: kwargs[parameter]})

            # Construct URL using base URL and path
            url = "{url}/{path}".format(url=self.url, path=resolved_path)

            # Prepare & check query parameters
            intersection = set(all_query_parameters).intersection(kwargs.keys())
            groups_used = {}
            for kwarg in intersection:
                for group in groups:
                    if kwarg in groups[group]:
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
                if isinstance(kwargs[kwarg], list) and kwarg not in multiple_parameters:
                    raise SyntaxError("parameter '{kwarg}' is not multiple".format(
                        kwarg=kwarg
                    ))
                else:
                    parameters[kwarg] = kwargs[kwarg]

            # Add request body data
            data = None
            if "data" in kwargs:
                data = kwargs["data"]

            # Check if valid URL
            self.url_validator.__call__(url)

            # JSON options
            if "json" in self.resources[resource]:
                json_options = self.resources[resource]["json"]
            else:
                json_options = {}

            # Do HTTP request to REST API
            try:
                response = requests.request(method=method,
                                            url=url,
                                            params=parameters,
                                            data=data,
                                            auth=self.auth,
                                            verify=self.verifySSL)
                return RestResponse(response=response,
                                    options=json_options).to_python()
            except ValueError:
                return response.content
            except requests.HTTPError as http:
                raise http

        return function_template
