#####################################
Configuration of server and endpoints
#####################################

The way access to a REST API is configured, is inspired by Django Model objects.
For any given REST API, you create

#. subclasses of ResourceConfig, where each subclass configures an endpoint of
   the REST API, and
#. a single subclass of APIConfig to configure values that hold for each of
   these endpoints, e.g. the url of the REST server.

The introduction already showed how that looks for the JSONPlaceholder website::

  from qrest import APIConfig, ResourceConfig, QueryParameter


  class JSONPlaceholderConfig(APIConfig):
      url = "https://jsonplaceholder.typicode.com"


  class AllPosts(ResourceConfig):

      name = "all_posts"
      path = ["posts"]
      method = "GET"
      description = "retrieve all posts"


  class FilterPosts(ResourceConfig):

      name = "filter_posts"
      path = ["posts"]
      method = "GET"
      description = "retrieve all posts with a given title"

      user_id = QueryParameter(name="userId", description="the user ID of the author of the post")

Suppose the above snippet is saved in a file ``jsonplaceholderconfig.py``. The
following lines import that file and instantiate the API instance that you use
to access the REST API::

  import qrest
  import jsonplaceholderconfig

  api = qrest.API(jsonplaceholderconfig)

  posts = api.all_posts()

  # posts is the list of dictionaries, where each dictionary stores the
  # information of a post

The init dunder of ``qrest.API`` inspects the module that is passed and
automatically retrieves the APIConfig and ResourceConfig subclasses. If the
module does not an APIConfig, or has more than one, the dunder will raise an
exception.

You see that the name attribute of each ResourceConfig is used as the attribute
name of the actual API object, e.g. the value of ``AllPosts.name``, which is
``all_posts``, is the name of the attribute on ``api``.

Each API instance has a property ``resources`` that lists the resources::

  assert set(["all_posts", "filter_posts"]) == set(api.resources)

One other thing, you don't have to configure the API in a separate Python
module. You can also define them in the current module and pass that module to
``qrest.API``::

  # subclasses of APIConfig and ResourceConfig

  import sys

  current_module = sys.modules[__name__]
  api = qrest.API(current_module)


********************
APIConfig attributes
********************

This section describes the attributes of an APIConfig.

url
===

This is the base URL of the REST server. You have to specify this field
otherwise the API cannot be initialized.

default_headers
===============

This is a dictionary that contains the default headers for all ResourceConfig
instances of the APIConfig class. Its aim is to prevent a lot of duplicate
information. The headers that a ResourceConfig uses consist of these defaults,
extended or overridden by the defaults that can be specified for that
ResourceConfig.

authentication
==============

This optional property configures a qrest.auth.AuthConfig instance. If this
property is omitted, no authentication is attempted. Basic authentication and
CAS authentication are provided. BasicAuthentication is provided to be able to
use both .netrc as regular usernames and password combinations. Each AuthConfig
instance has a set_credentials() method that allows customization of the
credentials. For NetrcOrUserPassAuthConfig the module first checks the presence
of a .netrc file, and then tries the optional username and password parameters.



*************************
ResourceConfig attributes
*************************

This section describes the attributes of a ResourceConfig. It
uses the following ResourceConfig as an example::

  class MyConfig(APIConfig):

      # ... configuration of attributes such as 'url'

  class Posts(ResourceConfig):

      name = "get_posts"
      method = "GET"
      path = ["rest", "v1", "{location}", "posts"]
      description = "this describes the role of the endpoint"
      path_description = {"location": "this describes the location part of the parameter"}
      headers = {"command": "search"}
      processor = JSONResource(extract_section=["_embedded", "posts"], create_attribute="myposts")

      post_uid = BodyParameter(name="PostUID")

name
====

The value of this attribute will be used as the name of the attribute of the
API, in this case ``api.get_posts``.

method
======

This attribute specifies which HTTP request method should be used. Commonly used
HTTP request methods are GET, POST, PUT and DELETE but at the moment only GET, POST and PUT are supported.

path
====

Another attribute of the ResourceConfig, is the path. It specifies a list of
strings that, when joined by a forward slash "/", specifies where the resource
is located in the REST API.

If a string in the path has curly braces around it, viz. "{}", it means that
that element of the path is parameterized. From the example above::

  path = ["rest", "v1", "{location}", "posts"]

Here, the above configuration corresponds to a path of
``rest/v1/{location}/posts`` where ``{location}`` is specified by a required
keyword parameter in the function call. To give an example, the code

::

  api.get_posts(location='myhouse')

will request the resource at URL http://example.com/rest/v1/myhouse/posts.

description
===========

This attribute describes the resource, e.g.

::

  assert "this describes the role of the endpoint" == api.get_posts.description

path_description
================

This attribute describes the individual path parameters, e.g.

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

A JSONResource can be configured to extract specific data from a JSON response.
It accepts keyword argument ``extract_section`` that specifies a list of strings
that forms the path to the relevant key. Say the response looks like this::

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

headers
=======

The required headers to be added to the request. Needs to be a dictionary


query parameters
================

A ResourceConfig has special attributes for a BodyParameter, QueryParameter or
FileParameter, all subclasses of ParameterConfig. A BodyParameter ends up inside
the body of a request similar to the parameters in curl, e.g

::

  curl -X POST -d '{"key":"value","type":"json"}' http://localhost:8080/api/call

Although it is possible to use query parameters in a POST request, one cannot
use body parameters in a GET request. A query parameter is usually used in a
HTTP GET request, by supplementing the request URL by a question mark ``?`` and
adding key-value pairs separated by ampersands ``&``. To give an example,

::

  http://example.com/resource?isThere=true&radius=2&...

To explain the different keyword arguments of a BodyParameter and
QueryParameter, we use the following example ResourceConfig::

  class MyResourceConfig(ResourceConfig):

      name = "get_items"

      param1 = BodyParameter(name="Parameter1", exclusion_group="group_a")
      param2 = BodyParameter(name="Parameter2", exclusion_group="group_a")
      multi_param = BodyParameter("MultiParameter", multiple=True)
      required_param = BodyParameter(name="RequiredParameter", required=True)
      describe_param = BodyParameter(
              name="DescribedParameter", description="This parameter is described"
          )
      choices_param = QueryParameter(
              name="ChoicesParam", default="key", choices=["key", "name", "date", "value"]
          )

FileParameter should be used to attach a file to a request. It has a similar effect
as the following example curl command to send a password file to a server

::

  curl -F password=@/etc/passwd www.mypasswords.com

In this example, password is the name of the form-field to which the file /etc/passwd is
the input. The name attribute of FileParameter should match the name of the form-field.
Files should be added as tuples: (filename(str), file(_io.BufferedReader)).

name
----

This attribute specifies the 'remote' name of the parameter, i.e., what the REST
resource actually gets to interpret. For example, the configuration specifies a
QueryParameter for key ``choices_param``, whose 'remote' name is
``ChoicesParam``. This means that the call

::

  api.get_items(choices_param="value")

will request the resource at URL http://example.com?ChoicesParam=value

For a BodyParameter, it is allowed that the name attribute has value None. In that
case, the value that is passed to the BodyParameter will be added as such to the body
of the request, not as a key/value pair. This is useful for bodies with a
non-dictionary structure. In that case, a resource can have only one BodyParameter.
For QueryParameters, a name attribute with value None is not allowed.

required
--------

This argument is an optional Boolean value: if the value is True but the
parameter is ommitted in the call, the API instance will raise an exception. By
default, its value is False.


multiple
--------

This argument is an optional Boolean value: if the value is set to True, not
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
---------------

Parameters in the same exclusion group cannot be used together. Groups can be
used to specify dynamic key-value pairs that cannot be combined in a single
request. For instance, if some query parameter key can have different names but
only one of those names can be used in a request, then grouping is needed.

For example, the configuration specifies that one should either pass ``param1``
or ``param2``, or neither, but not both.

default
-------

This argument specifies the value that will be used if the parameter is not
supplied.

choices
-------

This argument specifies the list of values that are allowed for the parameter.

description
-----------

This argument describes the parameter.

example
-------

This attribute specifies an optional example value for the parameter. If combined
with 'choices' or 'schema', the example must be in the list of choices, or obey the schema.

schema
------

This optional argument specifies a json schema. A json schema describes how data should
be structured and formatted, and therefore provides a powerful tool to impose requirements
on the value of a parameter.

For example, to ensure that the value of a parameter is formatted as a uuid, one can use

::

  {"type":"string", "pattern":"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}

as schema. To ensure that the value is a list of unique integers selected from a predefined set,

::

  {"type":"array", "items": {"type": "integer", "enum": [2, 4, 8, 16]}, "uniqueItems": true}

would be appropriate. For more info, visit the `json schema website <https://json-schema.org/>`.

When combined with schema, values for the 'default' and 'example' argument must obey the schema.
Schema can't be combined with the 'choices' argument.
