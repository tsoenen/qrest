##################### 
Configuring Resources
#####################
This document is part of the Python REST API client package and documents how to use the package to query arbitrary REST APIs.
For a given REST API, the resources are described by means of a RESTConfig instance which holds the configuration of every resource in the REST API.
The configuration class is then passed to a API object to create an interface to a REST server

Basic usage is to define all parameters of the REST service into a configuration structure, and then use this as a parameter
::

	class MyRESTConfig(APIConfig):
		...
	my_config = MyRESTConfig()

	rest_client = API(config=my_config)

or:
::

	class MyRESTConfig(APIConfig):
		...

	class DataRepository(Launcher):
		config = MyRESTConfig()

	data_rep = DataRepository()



********************
Server Configuration
********************

The main configuration object is a Python class inspired by the Django Model objects. It contains the configuration of a a REST API.

::

	class MyRESTConfig(APIConfig):

		authentication = NetrcOrUserPassAuthConfig(verify_ssl=False)

		default_headers = {"Content-Type": "application/json",
					       "Accept": "application/json;charset=UTF-8"}
		
		list_items = ResourceConfig(path=['api',"items"],
									method='POST',
									)
	...

The structure of the class is as follows:

* Each endpoint is configured as an ResourceConfig instance, 

* Besides endpoints, two fixed-named objects are allowed
	* 'default_headers' is a dictionary with default entries that ResourceConfig objects use to populate
	* 'authentication' is an AuthConfig instance that describes the type of configuration. 

All items of the ResourceConfig class will be transformed into methods for the API object
They are used to dynamically create functions in the REST API client object for every resource.
The name of the function corresponds to the name of the resource, but this may be altered via the 'name' parameter in the Parameter Configuration.

For example, when constructing a API instance with the above configuration, the resulting API instance will have a property "resources".
The code to invoke the function will be

::

	rc = API(configuration_class_instance)
	print(rc.resources)

Available configuration options
===============================

Apart from endpoint configurations (described below) there are other parameters that may be set

url
---
This is the Base URL of the REST server

default_headers
---------------
This is a dictionary that contains default values for all EndpointConfig instances within the Configuration class. Its aim is 
to prevent a lot of duplicate information. Currently only the 'headers' and 'json' parameters are supported.


authentication
--------------
This optional property configures an rest_client.auth.AuthConfig instance. If this property is omitted, no authentication is attempted. 
Basic authentication and CAS authentication are provided. BasicAuthentication is provided to be able to use both .netrc as regular usernames 
and password combinations. Each AuthConfig instance has a login() method that allows customization of the credentials. For NetrcOrUserPassAuthConfig
the module first checks the presence of a .netrc file, and then tries the optional username and password parameters.

::

	class MyConfig(APIConfig):
		authentication = NetrcOrUserPassAuthConfig(verify_ssl=False)
		
	rest_client = API(config=MyConfig())
	rest_client.login()
	


**********************
Endpoint Configuration
**********************

::

	get_posts = ResourceConfig(path=['rest', 'v1', '{location}',"posts"],
								description='this describes the role of the endpoint', 
								path_description={'location': 'this desribes the path parameter',}
								method='POST',
								headers={"command": "search"},
								processor=JSONResource(extract_section=["_embedded", "posts"],create_attribute="myposts",)
								parameters={
									'post_uid': BodyParameter(name="PostUID"),
								},
							)


Method
======

The resource method configuration option specifies which HTTP request method should be used.
Commonly used HTTP request methods are "GET", "POST", "PUT" and "DELETE".
If no resource method has been specified, the default method "GET" will be used.
For request methods where content is part of the request body, the "data" parameter of the resource function can be used.

In other words the code below

::

	rc = API(config=MyConfig())
	rc.get_posts(post_uid='12345')

will perform a HTTP POST request with {"PostUID": 12345} as the request body.

Path
====

One of the configuration options of a resource, is the path.
The path option is a list of strings that, when joined by a forward slash "/", specifies where the resource is located in the REST API.
If a path parameter is used, you can put curly braces "{}" around the name of that parameter. From the example above:

::

	path=['rest', 'v1', '{location}',"posts"]

Here, the above configuration corresponds to a path of "../{location}/.." where "{location}" is a required parameter specified in the function call.
The following code

::

	rc = API(config=MyConfig())
	rc.get_posts.fetch(location='myhouse')

will request the resource at the URL: "http://example.com/rest/v1/myhouse/posts".


Description
===========
allows you to add description for the endpoint

::

	rc = API(config=MyConfig())
	rc.get_posts.description

This will print "this describes the role of the endpoint" to screen


Path_description
================
allows you to add description for path parameters of the endpoint

::

	rc = API(config=MyConfig())
	rc.get_posts.help('location')

This will print "this desribes the path parameter" to screen. 


Processor
============

Normally a call to an endpoint returns a Response object. For most needs it may be required to subclass this 
object to add functionality (paging is a typical example). This functionality may be specific for your REST service.
Creating custom RestResponse objects is however not in scope of this document. This parameter allows to set and 
configure the Resource object that handles the interaction for one specific endpoint


JSONResource
------------

Often a REST call will return a complicated JSON object, where the 'interesting' data is embedded within a structure. This parameter 
creates a 'direct link' to this data. For example when the return data is

::

	{ "_embedded": { "posts":['a','b','c'],
					"count":3
				},
	"_links":{"self":"http://someurl"}
	}

The "extract_section" option will probably be the most used one.
With this option, you can specify where to look for the resulting Python object in the response body JSON content.
The "extract_section" JSON option is a list of strings and traverses the response body JSON content looking for nested keys, following the order of the specified list.
THe "create_attribute" option is the name of an attribute that is created to store the returned data.
The following configuration for example will look for the response_json["_embedded"] object for the first resource name and the response_json["_embedded"]["posts"] object for the second resource name.

Then it is possible to do either of:

::

	rc = API(config=MyConfig())
	print(rc.get_posts().fetch())  # will print ['a','b','c']
	
	returned_posts = rc.get_posts().myposts
	print(returned_posts)  # will print ['a','b','c']
	
	print(rc.get_posts().data)  # will print ['a','b','c']

	print(rc.get_posts().raw)  # will print the complete return JSON
	

As shown, there are multiple ways to retreive data. Specifically, the 'data' attribute doubles that of the 'myposts' attribute. This
is done to allow both user-friendly coding (using the myposts), but the possibility to be consistent ('data' is always available and 
thus predictable)





Headers
=======

The required headers to be added to the request. Needs to be a dictionary


Parameters
==========

this is a list of ParameterConfig instances that describe the query and body parameters of the request



***********************
Parameter Configuration
***********************

The parameters dictionary contains all possible parameters for this endpoint, described using ParameterConfig instances.
The ParameterConfig class is subclassed into BodyParameter and QueryParameter.

A QueryParameter is usually used in a HTTP GET request, by supplementing the request URL by a question mark "?" and adding key-value pairs separated by ampersands "&".
An example: "http://example.com/resource?isThere=true&radius=2&...

A BodyParameter ends up inside the body of a request (similar to the parameters in curl -X POST -d '{"key":"value","type":"json"}' http://localhost:8080/api/call)
Although it is possible to use QueryParameters in a POST request, one cannot use POST parameters in a GET request.

::

	get_items = ResourceConfig(
		...
		parameters={'param1': BodyParameter(name="Parameter1", exclusion_group="group_a"),
					'param2': BodyParameter(name="Parameter2", exclusion_group="group_a"),
					'multi_param': BodyParameter("MultiParameter", multiple=True),
					'required_param': BodyParameter(name="RequiredParameter", 
													required=True,
													),
					'describe_param': BodyParameter(name="DescribedParameter", 
													description='This parameter is described'
													),
					'choices_param': QueryParameter(name="ChoicesParam",
													default='key',
													choices=['key','name','date','value']),
			},
		...
		)

Name
====
the 'remote' name of the parameter. this name is what the REST resource actually gets to interpret

For example, the above configuration specifies one (optional) query parameter with a name of "required_param".
An example invocation is given below:

::

	rc = API(url="http://example.com", config=MyConf())
	rc.get_items(choices_param="value")

This will request the resource at the URL: "http://example.com?ChoicesParam=value".


Required
=============================
if this parameter is ommitted in the qyery, throw an exception
Query parameters are optional by default, but can be configured to be required (and will be validated as a result of that).
The "required" option is an optional boolean configuration value and is "False" by default.


multiple
=============================
if set to True, the value of the query parameter is a list
Some query parameters can be used multiple times in a URL.
This can be helpful if some query parameter key needs a list of values.
The "multiple" option is an optional boolean configuration value and is "False" by default.
When set to "True", not only single values ("some_value" or 1 or True or ...) but also lists can be used "[1, 2, 3]".

For example, the above configuration specifies one (optional) query parameter with a name of "multi_param" and allows lists as its value.
One can indeed write

::

	rc.resource_name(multi_param=["some_value", "some_value_2"])

for passing multiple values or

::

	rc.resource_name(multi_param="some_value")

for passing a single value. This will request the resource at the URL: 
"http://example.com?multi_param=some_value&multi_param=some_value_2" in the first 
case and "http://example.com?multi_param=some_value" in the latter case.


Exclusion_group
=============================
Parameters in the same exclusion group may not be used together
Groups can be used to specify dynamic key-value pairs that can't be combined in a single request.
If, for instance, some query parameter key can have different names but only one of those names can be used in a request, then grouping is needed.
In the above example, the user must either set param1 or param2 (or neither) , but cannot set both param1 and param2.


Default
=============================
the default entry if this parameter is not supplied

Choices
=============================
a list of possible values for this parameter

Description
=============================
any information about the parameter, such as data format 


******************** 
Configuration Module
******************** 

.. automodule:: rest_client.conf

.. autoclass:: APIConfig
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: ResourceConfig
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: ParameterConfig
	:members:
	:private-members:
	:special-members: __init__
	
.. autoclass:: QueryParameter
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: BodyParameter
	:members:
	:private-members:
	:special-members: __init__




