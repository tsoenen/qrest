.. Python REST API client documentation master file, created by
   sphinx-quickstart on Wed Jan 18 16:22:53 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python REST API client documentation
====================================

.. toctree::
   :titlesonly:
   :caption: Extra documentation:

   resources-configuration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

rest_client
===============

.. automodule:: rest_client

.. autoclass:: RestClient
   :members:
   :private-members: 
   :special-members: __init__


Resources
=========

.. automodule:: rest_client.resources

.. autoclass:: RestResource
   :members:
   :private-members:
   :special-members: __init__

.. autoclass:: RestResponse
   :members:
   :private-members:
   :special-members: __init__


Configuration
=============

.. automodule:: rest_client.conf
.. autoclass:: RESTConfiguration
.. autoclass:: EndPointConfig

.. autoclass:: ParameterConfig
.. autoclass:: QueryParameter
.. autoclass:: BodyParameter


Authentication
==============

.. automodule:: rest_client.auth

Authentication classes 
----------------------
.. autoclass:: RESTAuthentication
   :members:
   :private-members:
   :special-members: __init__

.. autoclass:: NoAuth
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

.. autoclass:: NoAuthConfig
   :members:
   :private-members:
   :special-members: __init__

.. autoclass:: UserPassAuthConfig
   :members:
   :private-members:
   :special-members: __init__

.. autoclass:: NetrcOrUserPassAuthConfig
   :members:
   :private-members:
   :special-members: __init__

CAS Authentication
------------------

.. autoclass:: CASAuth
   :members:
   :private-members:
   :special-members: __init__


.. autoclass:: CasAuthConfig
   :members:
   :private-members:
   :special-members: __init__


