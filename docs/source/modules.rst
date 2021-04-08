********************
Module documentation
********************

configuration
=============

.. automodule:: qrest.conf

.. autoclass:: APIConfig
  :members:
  :special-members: __init__

.. autoclass:: ResourceConfig
  :members:
  :special-members: __init__

.. autoclass:: ParameterConfig
  :members:
  :special-members: __init__

.. autoclass:: QueryParameter
  :members:
  :special-members: __init__

.. autoclass:: BodyParameter
  :members:
  :special-members: __init__

.. autoclass:: FileParameter
  :members:
  :special-members: __init__

resource
========

.. automodule:: qrest.resource

.. autoclass:: API
  :members:
  :special-members: __init__

.. autoclass:: Resource
  :members:
  :special-members: __init__

.. autoclass:: JSONResource
  :members:
  :special-members: __init__

authentication
==============

.. automodule:: qrest.auth

Classes
-------

.. autoclass:: RESTAuthentication
	:members:
	:special-members: __init__

.. autoclass:: UserPassAuth
	:members:
	:special-members: __init__

.. autoclass:: NetRCAuth
	:members:
	:special-members: __init__

.. autoclass:: UserPassOrNetRCAuth
	:members:
	:special-members: __init__

Configuration
-------------

.. autoclass:: UserPassAuthConfig
	:members:
	:special-members: __init__

.. autoclass:: NetrcOrUserPassAuthConfig
	:members:
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
	:special-members: __init__

.. autoclass:: JSONResponse
	:members:
	:special-members: __init__

.. autoclass:: CSVResponse
	:members:
	:special-members: __init__
