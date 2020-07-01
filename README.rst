qrest is a Python package that allows you to easily build a Python client to use
a REST API.

Overview
********

The `JSONPlaceholder website`_ provides information through a REST API for
testing and prototyping purposes. The following Python snippet retrieves all
"posts", which is one of the resources that the website provides. The snippet
sends a HTTP GET request using the Python requests_ library::

    import pprint
    import requests

    response = requests.request("GET", "https://jsonplaceholder.typicode.com/posts")
    pprint.pprint(response.json()[0:2])

This snippet outputs::

    [{'body': 'quia et suscipit\n'
              'suscipit recusandae consequuntur expedita et cum\n'
              'reprehenderit molestiae ut ut quas totam\n'
              'nostrum rerum est autem sunt rem eveniet architecto',
     'id': 1,
     'title': 'sunt aut facere repellat provident occaecati excepturi optio '
              'reprehenderit',
     'userId': 1},
    {'body': 'est rerum tempore vitae\n'
             'sequi sint nihil reprehenderit dolor beatae ea dolores neque\n'
             'fugiat blanditiis voluptate porro vel nihil molestiae ut '
             'reiciendis\n'
             'qui aperiam non debitis possimus qui neque nisi nulla',
     'id': 2,
     'title': 'qui est esse',
     'userId': 1}]

Although the requests library makes it very easy to query a REST API, it
requires the user to know the structure of the REST API, how to build calls to
that API, how to parse responses. This is where qrest comes in: it allows you to
*configure* a Python API that provides access to the *information* and hides the
nitty-gritty details of writing REST API code. For example, using qrest the code
to retrieve the posts looks like this::

    import qrest

    api = qrest.API(JSONPlaceholderConfig())

    posts = api.all_posts.fetch()

If you want to retrieve the posts with a specific title::

    import pprint

    posts = api.filter_posts.fetch(title="qui est esse")
    pprint.pprint(post)

which outputs::

    [{'body': 'est rerum tempore vitae\n'
              'sequi sint nihil reprehenderit dolor beatae ea dolores neque\n'
              'fugiat blanditiis voluptate porro vel nihil molestiae ut '
              'reiciendis\n'
              'qui aperiam non debitis possimus qui neque nisi nulla',
      'id': 2,
      'title': 'qui est esse',
      'userId': 1}]

The one thing you have to do is configure this API. The JSONPlaceholderConfig in
the example above is configured like this::

    from qrest import APIConfig, ResourceConfig, QueryParameter

    class JSONPlaceholderConfig(APIConfig):

        url = 'https://jsonplaceholder.typicode.com'

        all_posts = ResourceConfig(path=["posts"], method="GET", description="retrieve all posts")

        filter_posts = ResourceConfig(
            path=["posts"],
            method="GET",
            description="retrieve all posts by filter criteria",
            parameters={
                "title": QueryParameter(
                    name="title",
                    required=False,
                    description="the title of the post",
                ),
            },
        )

For more information about qrest and its usage, we refer to the documentation.

If you want to contribute to qrest itself, we refer to the developer README that
is located in the root directory of the repo.

.. _JSONPlaceholder website: https://jsonplaceholder.typicode.com
.. _requests: https://requests.readthedocs.io/en/master/
