Python REST API client documentation
====================================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

##########################################
The Python Generic REST client project
##########################################

A Python project for sending requests to REST APIs.

Overview
***************************************************

This module aims to do for REST services what applications like SQLalchemy do for SQL services:
to provide a python-like interface that hides the technical background and provides a native python
ORM. 
THis is achieved by creating configuration files for each REST service that can be extended or modified 
at will, and allows restrictions on input that are required by the backend. Also custom authentication
and output handling is provided 

For example, taking the JSONplaceholder test site, there is a 
URL `<http://https://jsonplaceholder.typicode.com/posts?userId=1>`_ 

To query this resource, some text formatting magic needs to be combined with the requests module, after which the results need to be parsed.

An easier solution
***************************************************

Would it not be a lot easier to use this format
::

    import jsonplaceholder as jp

    list_of_pots = jp.filter_posts.fetch(user_id=1)
    print list_of_posts

To achieve this, we need only this code:
::

    from qrest import API, APIConfig

    class JsonPlaceHolderConfig(APIConfig):
        url = 'https://jsonplaceholder.typicode.com'
        filter_posts = ResourceConfig(path=['posts'],
                                      method='GET',
                                      description='retrieve all posts by filter criteria',
                                      parameters={ 'user_id': QueryParameter(name='userId',
                                                                             required=False,
                                                                             description='the user Id that made the post'),
                                                                             }
                                    )

    config =  JsonPlaceHolderConfig()
    jp  = API(config)  
    list_of_pots = jp.filter_posts.fetch(user_id=1)



.. toctree::
   :titlesonly:
   :caption: Table of Contents:
   :maxdepth: 2

   configuration

   rest-client
   authentication
   responses



