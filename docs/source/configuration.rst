#####################
Configuring resources
#####################

This section documents the use of the qrest package to query arbitrary REST
APIs. For a given REST API, you create an APIConfig that configures all the
resources of the API [#subclass]_. A resource itself is configured using a
ResourceConfig instance. The introduction showed how that looks for the
JSONPlaceholder website::

  class JSONPlaceholderConfig(APIConfig):

      url = "https://jsonplaceholder.typicode.com"

      all_posts = ResourceConfig(path=["posts"], method="GET", description="retrieve all posts")

      filter_posts = ResourceConfig(
          path=["posts"],
          method="GET",
          description="retrieve all posts by filter criteria",
          parameters={
              "title": QueryParameter(
                  name="title", required=False, description="the title of the post",
              ),
          },


********************
Server configuration
********************

The main configuration object, the APIConfig, is inspired by Django Model
objects. It contains the configuration of a REST API.

::

  class MyRESTConfig(APIConfig):

      url = "http://example.com/rest/v1/"

      authentication = NetrcOrUserPassAuthConfig()

      default_headers = {
          "Content-Type": "application/json",
          "Accept": "application/json;charset=UTF-8",
      }

      list_items = ResourceConfig(path=["api", "items"], method="GET")

      # ...

You use the APIConfig to initialize the object that will access the REST API,
e.g.

::

  api = qrest.API(MyRESTConfig())
  items = api.list_items()

The names of the attributes of the APIConfig that specify the resources, are
also used to name the attributes on the actual API object. You can specify
another name using the ``name`` argument of the ResourceConfig.

Each API instance has a property ``resources`` that lists the resources::

  api = qrest.API(MyRESTConfig())
  assert ["list_items"] == api.resources

Available configuration options
===============================

Apart from attributes to configure resources, an APIConfig has the following
attributes.

url
---

This is the base URL of the REST server. You have to specify this field
otherwise the API cannot be initialized.

default_headers
---------------

This is a dictionary that contains the default headers for all ResourceConfig
instances of the APIConfig class. Its aim is to prevent a lot of duplicate
information. The headers that a ResourceConfig uses consist of these defaults,
extended or overridden by the defaults that can be specified for that
ResourceConfig.

authentication
--------------

This optional property configures a qrest.auth.AuthConfig instance. If this
property is omitted, no authentication is attempted. Basic authentication and
CAS authentication are provided. BasicAuthentication is provided to be able to
use both .netrc as regular usernames and password combinations. Each AuthConfig
instance has a login() method that allows customization of the credentials. For
NetrcOrUserPassAuthConfig the module first checks the presence of a .netrc file,
and then tries the optional username and password parameters.


**********************
Resource Configuration
**********************

This section describes the different keyword arguments of a ResourceConfig. It
uses the following ResourceConfig as an example::

  class MyConfig(APIConfig):

      get_posts = ResourceConfig(
          method="GET",
          path=["rest", "v1", "{location}", "posts"],
          description="this describes the role of the endpoint",
          path_description={"location": "this describes the location part of the parameter"},
          headers={"command": "search"},
          processor=JSONResource(extract_section=["_embedded", "posts"], create_attribute="myposts"),
          parameters={"post_uid": BodyParameter(name="PostUID")},
      )

  api = API(config=MyConfig())

method
======

This (keyword) argument specifies which HTTP request method should be used.
Commonly used HTTP request methods are GET, POST, PUT and DELETE. If no resource
method has been specified, GET will be used. For request methods where content
is part of the request body, the "data" parameter of the resource function can
be used.

In other words the code

::

  api.get_posts(post_uid="12345")

will perform a HTTP GET request with ``{"PostUID": 12345}`` as the request body.

path
====

Another argument to the ResourceConfig, is the path. The path option is a list
of strings that, when joined by a forward slash "/", specifies where the
resource is located in the REST API. If a path parameter is used, you can put
curly braces "{}" around the name of that parameter. From the example above::

  path=["rest", "v1", "{location}", "posts"],

Here, the above configuration corresponds to a path of
``rest/v1/{location}/posts`` where ``{location}`` is specified by a required
keyword parameter in the function call. To give an example, the code

::

  api.get_posts(location='myhouse')

will request the resource at URL http://example.com/rest/v1/myhouse/posts.

description
===========

This argument describes the resource, e.g.

::

  assert "this describes the role of the endpoint" == api.get_posts.description

path_description
================

This argument describes the individual path parameters, e.g.

::

  assert "this describes the location part of the parameter" == api.get_posts.help('location')

processor
=========

When you create an API for an APIConfig, the API will have a Resource instance
for every ResourceConfig of the APIConfig. It is the Resource that sends out the
request to the REST API and that makes sure the response is handled. There are
different Resource classes to handle different the content types. Out of the box
qrest provides a JSONResource to handle JSON responses and CSVResource to handle
CSV responses. You can create your own Response subclass to add specific
functionality, e.g. to support paging.

Optional argument ``processor`` configures the actual Resource object that the
resulting API instance will use. If you don't use this argument, the API
instance will use a standard JSONResource.

JSONResource
------------

A JSONResource can be configured to extract specific data from a JSON response.
It accepts keyword argument ``extract_section`` that specifies a list of
strings that forms the path to the relevant key. Say the response looks like
this::

  {"_embedded": {"posts": ["a", "b", "c"], "count": 3}, "_links": {"self": "http://someurl"}}

and you are only interested in the value of key ``["_embedded"]["posts"]``. The
specified JSONResource will do exactly that::

  assert ['a','b','c'] == api.get_posts()

The JSONResource shows another keyword argument, viz. ``create_attribute``. This
argument tells the JSONResource to store the retrieved value in a separate
attribute that is named using keyword argument ``create_attribute``, e.g.

::

  assert ['a','b','c'] == api.get_posts().myposts

Even if you don't specify ``create_attribute``, the retrieved value is
always accessible via attribute ``data``::

  assert ['a','b','c'] == api.get_posts().data

Finally, you can access the complete JSON response via attribute ``raw``::

  assert {
      "_embedded": {"posts": ["a", "b", "c"], "count": 3},
      "_links": {"self": "http://someurl"},
  } == api.get_posts().raw

As shown, there are multiple ways to retrieve data. Specifically, the ``data``
attribute doubles that of the ``myposts`` attribute. This is done to allow both
user-friendly coding (using the myposts), but the possibility to be consistent
(``data`` is always available and thus predictable)

Headers
=======

The required headers to be added to the request. Needs to be a dictionary

Parameters
==========

this is a list of ParameterConfig instances that describe the query and body parameters of the request


***********************
Parameter Configuration
***********************

A ResourceConfig accepts the keyword argument ``parameters``, which is a
dictionary that specifies the possible parameters for this resource. Each
parameter is specified as a BodyParameter or QueryParameter, both subclasses of
ParameterConfig.

A BodyParameter ends up inside the body of a request similar to the parameters
in curl, e.g

::

  curl -X POST -d '{"key":"value","type":"json"}' http://localhost:8080/api/call

Although it is possible to use query parameterrs in a POST request, one cannot
use body parameters in a GET request. A query parameter is usually used in a
HTTP GET request, by supplementing the request URL by a question mark ``?`` and
adding key-value pairs separated by ampersands ``&``. To give an example,

::

  http://example.com/resource?isThere=true&radius=2&...

To explain the different keyword arguments of a BodyParameter and
QueryParameter, we use the following ResourceConfig::

  get_items = ResourceConfig(
      # ...
      parameters={
          "param1": BodyParameter(name="Parameter1", exclusion_group="group_a"),
          "param2": BodyParameter(name="Parameter2", exclusion_group="group_a"),
          "multi_param": BodyParameter("MultiParameter", multiple=True),
          "required_param": BodyParameter(name="RequiredParameter", required=True,),
          "describe_param": BodyParameter(
              name="DescribedParameter", description="This parameter is described"
          ),
          "choices_param": QueryParameter(
              name="ChoicesParam", default="key", choices=["key", "name", "date", "value"]
          ),
      },
      # ...
  )

name
====

This (keyword) argument specifies the 'remote' name of the parameter, i.e., what
the REST resource actually gets to interpret. For example, the configuration
specifies a QueryParameter for key ``choices_param``, whose 'remote' name is
``ChoicesParam``. This means that the call

::

  api.get_items(choices_param="value")

will request the resource at URL http://example.com?ChoicesParam=value


required
========

This argument is an optional Boolean value: if the value is True but the
parameter is ommitted in the call, the API instance will raise an exception. By
default, its value is False.


multiple
========

This argument is an optional Boolean value: if the value is if set to True, not
only single values can be used but also a list of values.

Some query parameters can be used multiple times in a URL. This can be helpful
if some query parameter key needs a list of values.

For example, the configuration specifies a QueryParameter for key
``multi_param``. One can indeed write

::

  api.resource_name(multi_param=["some_value", "some_value_2"])

to request the resource at
http://example.com?multi_param=some_value&multi_param=some_value_2

A single value is still allowed, so

::

  rc.resource_name(multi_param="some_value")

will request http://example.com?multi_param=some_value

exclusion_group
===============

Parameters in the same exclusion group cannot be used together. Groups can be
used to specify dynamic key-value pairs that cannot be combined in a single
request. For instance, if some query parameter key can have different names but
only one of those names can be used in a request, then grouping is needed.

For example, the configuration specifies that one should either pass ``param1``
or ``param2``, or neither, but not both.

default
=======

This argument specifies the value that will be used if the parameter is not
supplied.

choices
=======

This argument specifies the list of values that are allowed for the parameter.

description
===========

This argument describes the parameter.

********************
Configuration Module
********************

.. automodule:: qrest.conf

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

.. rubric:: Footnotes

.. [#subclass] You actually create an instance of an APIConfig *subclass*. The
               APIConfig class itself does not specify any resources.
.. [#requests.Response] qrest uses the requests library to execute the requests.
                        The "raw response" is a ``requests.Response`` object.
