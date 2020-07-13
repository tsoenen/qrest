********************
Module documentation
********************

configuration
=============

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

resource
========

.. automodule:: qrest.resource

.. autoclass:: API
  :members:
  :private-members:
  :special-members: __init__

.. autoclass:: Resource
  :members:
  :private-members:
  :special-members: __init__

.. autoclass:: JSONResource
  :members:
  :private-members:
  :special-members: __init__

authentication
==============

.. automodule:: qrest.auth

Classes
-------

.. autoclass:: RESTAuthentication
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: UserPassAuth
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: NetRCAuth
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: UserPassOrNetRCAuth
	:members:
	:private-members:
	:special-members: __init__

Configuration
-------------

.. autoclass:: UserPassAuthConfig
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: NetrcOrUserPassAuthConfig
	:members:
	:private-members:
	:special-members: __init__

response
========

Response Processors are called upon when data comes back from the server and
needs to be modified into a native style. For example, if the response is
expected to be tabular, it could be framed into a pandas dataframe before
providing it to the user. The simplest approach is basically handling of JSON
responses that need to be translated into native python classes, such as lists
and dictionaries

.. automodule:: qrest.response

.. autoclass:: Response
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: JSONResponse
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: CSVResponse
	:members:
	:private-members:
	:special-members: __init__
