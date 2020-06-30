qrest is a Python package that allows you to build a Python API to send requests
to a REST API.

Overview
********

Let's have a look at the REST API that is provided by the JSONPlaceholder
website for testing and prototyping. The following Python snippet uses the
Python requests library to send a GET request that retrieves all posts::

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


If you have multiple requests in your code, before you know it you will add code
to

- avoid passing the same URL again and again,
- easily access different endpoints using different parameters,
- parse responses etc.

This is where qrest comes in: it allows you to configure a Python API that hides
the complexity and repetition of manually writing REST API code. For example,
using qrest the code to retrieve the posts looks like this::

    import pprint
    import qrest

    api = qrest.API(JSONPlaceholderConfig())

    posts = api.all_posts.fetch()

If you want to retrieve the posts with a specific title::

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

The one thing you have to do is configure this API. The
``JSONPlaceholderConfig`` in the example above is configured like this::

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
