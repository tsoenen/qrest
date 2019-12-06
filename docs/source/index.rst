.. Python REST API client documentation master file, created by
   sphinx-quickstart on Wed Jan 18 16:22:53 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python REST API client documentation
====================================

.. toctree::
   :titlesonly:
   :caption: Extra documentation:
   :maxdepth: 2

   resources-configuration
   rest-client

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


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
   :members:
   :private-members:
   :special-members: __init__

.. autoclass:: EndPointConfig
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



Authentication
==============

.. automodule:: rest_client.auth

Authentication classes 
----------------------
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


