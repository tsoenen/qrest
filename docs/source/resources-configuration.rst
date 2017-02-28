Resources configuration
------------------------

This document is part of the Python REST API client package and documents how to use the package to query arbitrary REST APIs.
For a given REST API, the resources are described by means of a Python dictionary object which holds the configuration of every resource in the REST API.

Resource
========

A Python dictionary object which holds the configuration of a resource of a REST API.

::

    resources = {
    	"resource_name": {
    		...
    	}
    }

The keys in the resources configuration dictionary are the names of the REST API resources.
These keys have to be a string type.
They are used to dynamically create functions in the REST API client object for every resource.
The name of the function exactly corresponds to the name of the resource.

For example, when constructing a RestClient instance with the above configuration, the resulting RestClient instance will have a function "resource_name".
The code to invoke the function will be

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name()

Resource method
===============

The resource method configuration option specifies which HTTP request method should be used.
Commonly used HTTP request methods are "GET", "POST", "PUT" and "DELETE".
If no resource method has been specified, the default method "GET" will be used.
For request methods where content is part of the request body, the "data" parameter of the resource function can be used.

::

    resources = {
    	"resource_name": {
    		"method": "POST"
    	}
    }

For example, the above configuration will do a HTTP POST request when executing the "resource_name" function.
In other words the code below

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name(data={"some_key": "some_value"})

will perform a HTTP POST request with {"some_key": "some_value"} as the request body.

Resource path
=============

One of the configuration options of a resource, is the path.
The path option is a list of strings that, when joined by a forward slash "/", specifies where the resource is located in the REST API.
If a path parameter is used, you can put curly braces "{}" around the name of that parameter.

::

    resources = {
    	"resource_name": {
    		"path": ["resource", "{id}"]
    	}
    }

For example, the above configuration corresponds to a path of "/resource/{id}" where "{id}" is the required id parameter specified in the function call.
The following code

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name(id="some_id")

will request the resource at the URL: "http://example.com/resource/some_id".

Nota bene: a path can't have the word "data" as a path parameter, i.e. ["resource", "{data}"] is forbidden, while ["resources", "data"] is perfectly fine.
That's because the "data" parameter is used to specify content for the request body (mostly used in POST or PUT HTTP requests).

Resource query parameters
=========================

The query parameters option of a resource is a list of dictionary objects (query parameters).
A query parameter is usually used in a HTTP GET request, by supplementing the request URL by a question mark "?" and adding key-value pairs separated by ampersands "&".
An example: "http://example.com/resource?isThere=true&radius=2&...

::

    resources = {
    	"resource_name": {
    		"query_parameters": [
    			{...},
    			{...}
    		]
    	}
    }

A query parameter dictionary object has a few options itself, specified by adding key-value pairs to the query parameter dictionary object.
Those options can be combined to allow correct use of the query parameter and are documented in the sections below.

Resource query parameter name
+++++++++++++++++++++++++++++

The only mandatory option is the "name" option, because that value is used as the parameter name when executing the resource function.

::

    resources = {
    	"resource_name": {
    		"query_parameters": [
    			{"name": "some_parameter"}
    		]
    	}
    }

For example, the above configuration specifies one (optional) query parameter with a name of "some_parameter".
An example invocation is given below:

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name(some_parameter="some_value")

This will request the resource at the URL: "http://example.com?some_parameter=some_value".

Nota bene: a query parameter can't have the word "data" as its name.
That's because the "data" parameter is used to specify content for the request body (mostly used in POST or PUT HTTP requests).

Resource query parameter required
+++++++++++++++++++++++++++++++++

Query parameters are optional by default, but can be configured to be required (and will be validated as a result of that).
The "required" option is an optional boolean configuration value and is "False" by default.

::

    resources = {
    	"resource_name": {
    		"query_parameters": [
    			{"name": "some_parameter", "required": True}
    		]
    	}
    }

For example, the above configuration specifies one required query parameter with a name of "some_parameter".
If you then would use the function without that query parameter, an exception will be raised

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name()

    SyntaxError: "parameter 'some_parameter' is missing for resource 'resource_name'"

Resource query parameter multiple
+++++++++++++++++++++++++++++++++

Some query parameters can be used multiple times in a URL.
This can be helpful if some query parameter key needs a list of values.
The "multiple" option is an optional boolean configuration value and is "False" by default.
When set to "True", not only single values ("some_value" or 1 or True or ...) but also lists can be used "[1, 2, 3]".

::

    resources = {
    	"resource_name": {
    		"query_parameters": [
    			{"name": "some_parameter", "multiple": True}
    		]
    	}
    }

For example, the above configuration specifies one (optional) query parameter with a name of "some_parameter" and allows lists as its value.
One can indeed write

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name(some_parameter=["some_value", "some_value_2"])

for passing multiple values or

::

    rc.resource_name(some_parameter="some_value")

for passing a single value. This will request the resource at the URL: "http://example.com?some_parameter=some_value&some_parameter=some_value_2" in the first case and "http://example.com?some_parameter=some_value" in the latter case.

Resource query parameter group
++++++++++++++++++++++++++++++

The last option for a query parameter is the group option.
Groups can be used to specify dynamic key-value pairs that can't be combined in a single request.
If, for instance, some query parameter key can have different names but only one of those names can be used in a request, then grouping is needed.
Let's take a look at the following configuration.

::

    resources = {
    	"resource_name": {
    		"query_parameters": [
    			{"name": "key1", "group": "some_group"},
    			{"name": "key2", "group": "some_group"},
    			{"name": "key3", "group": "some_group"}
    		]
    	}
    }

Using the above configuration, we specify that the following requests are good:

::

    ?key1=some_value
    ?key2=some_value
    ?key3=some_value

but the following requests are bad:

::

    ?key1=some_value&key2=some_value
    ?key3=some_value&key1=some_value
    ?key1=some_value&key2=some_value&key3=some_value

All three keys can indeed be used in the request, but they cannot be combined.
Using the above configuration one can perform

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name(key1="some_value")

but the following will raise an exception

::

    rc.resource_name(key1="some_value", key2="some_other_value")

    SyntaxError: "parameter 'key1' and 'key2' from group 'some_group' can't be used together"

Resource JSON options
=====================

Finally, options for resulting JSON responses (which will only apply when the response body content is JSON) can be configured using the following parameters.
The JSON options object is a dictionary.

::

    resources = {
    	"resource_name": {
    		"json": {...}
    	}
    }

Resource JSON option root
+++++++++++++++++++++++++

The "root" JSON option will probably be the most used one.
With this option, you can specify where to look for the resulting Python object in the response body JSON content.
The "root" JSON option is a list of strings and traverses the response body JSON content looking for nested keys, following the order of the specified list.
The following configuration for example will look for the response_json["_embedded"] object for the first resource name and the response_json["_embedded"]["resource"] object for the second resource name.

::

    resources = {
    	"resource_name1": {
    		"json": {"root": ["_embedded"]}
    	}
    	"resource_name2": {
    		"json": {"root": ["_embedded", "resource"]}
    	}
    }

With the above configuration one can write

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name1()

which will return some dictionary object "{...}"
where the response body JSON content was a dictionary with "_embedded" as a key:

::

    {
    	"_embedded": {...}
    }

or

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name2()

which will return some dictionary object "{...}"
where the response body JSON content was a dictionary with "_embedded" and "resource" as a key:

::

    {
    	"_embedded": {
    		"resource": {...}
    	}
    }

Resource JSON option source name
++++++++++++++++++++++++++++++++

If the "root" JSON option above has been used, the original response body JSON content will still be available in the resulting dictionary object.
By default, the original or source response body JSON content will be available using result["source"].
If this would override an existing "source" entry, it will be placed at "_source".
However, if you would like to specify a custom location where the original response body JSON content should be placed, specifying a string for the key in this option allows for that.

::

    resources = {
    	"resource_name1": {
    		"json": {"root": ["_embedded"], "source_name": "raw"}
    	}
    }

Using the above configuration:

::

    rc = RestClient(url="http://example.com", resources=resources)
    rc.resource_name1()

which returns some dictionary object

::

    {
    	...
    	"raw": {
    		"_embedded": {...}
    	}
    }

instead of the default behaviour (without specifying a "source_name" option):

::

    {
    	...
    	"source": {
    		"_embedded": {...}
    	}
    }

or

::

    {
    	...
    	"source": "some_value",
    	"_source": {
    		"_embedded": {"source": "some_value"}
    	}
    }

if a "source" key already exists in the root JSON object.

Resource JSON option result name
++++++++++++++++++++++++++++++++

The JSON result name option can come in handy when the obtained result from the response body is not a Python dictionary.
To be able to save the source (or raw) JSON response body content, a dictionary is needed.
So in the case where the resulting response body is a Python list (due to the "root" option for example) and the original response body contains other helpful information, the Python list will be put inside a dictionary with key "result" by default.
This option allows you to change the name of the key.

::

    resources = {
    	"resource_name1": {
    		"json": {"root": ["_embedded"], "result_name": "resources"}
    	}
    }

In the above configuration, a JSON response body content of

::

    {
    	"_embedded": [
    		{...},
    		{...}
    	],
    	"_links": [...]
    }

would normally return a list [{...}, {...}]
however, to be able to save the original response (including the "_links" list), the return value is changed to:

::

    {
    	"resources": [{...}, {...}],
    	"source": {
    		"_embedded": [
    			{...},
    			{...}
    		],
    		"_links": [...]
    	}
    }

or, using the default option (not specifying the "result_name" option):

::

    {
    	"result": [{...}, {...}],
    	"source": {
    		"_embedded": [
    			{...},
    			{...}
    		],
    		"_links": [...]
    	}
    }
