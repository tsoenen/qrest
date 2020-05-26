##########################################
The Python Generic REST client project
##########################################

A Python project for sending requests to REST APIs.

Overview
***************************************************

This project aims to build ORM wrappers around REST interfaces, by separating the configuration 
from the business logic. For 

For example, taking the JSONplaceholder test site, there is a 
URL `<http://https://jsonplaceholder.typicode.com/posts?userId=1>`_ 

To query this rsource, some text formatting magic needs to be combined with the requests module, after which the results need to be parsed.

An easier solution
***************************************************

Would it not be a lot easier to use this format
::

    import jsonplaceholder as jp

    list_of_pots = jp.filter_posts.fetch(user_id=1)
    print list_of_posts

To achieve this, we need only this code:
::

    from rest_client import API, APIConfig

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

