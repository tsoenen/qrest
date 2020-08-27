qrest is a Python package that allows you to easily build a Python client to
access a REST API. To show how it works, we use it to access the REST API of the
`JSONPlaceholder website`_, which provides dummy data for testing and
prototyping purposes.

The following Python snippet sends a HTTP GET request to retrieve all "posts",
which is one of the resources of the website::

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

The snippet uses the Python requests_ library to send the request. This library
makes it very easy to query a REST API, but it requires the user to know the
structure of the REST API, how to build calls to that API, how to parse
responses etc. This is where qrest comes in: it allows you to *configure* a
Python API that provides access to the *information* and hides the nitty-gritty
details of writing REST API code. For example, using qrest the code to retrieve
the posts looks like this::

    import qrest
    import jsonplaceholderconfig

    api = qrest.API(jsonplaceholderconfig)

    posts = api.all_posts()

If you want to retrieve the posts from a specific author::

    import pprint

    # all authors are numbered from 1 to 10
    posts = api.filter_posts(user_id=7)

    # only output the title of each post for brevity
    titles = [post["title"] for post in posts]
    pprint.pprint(titles)

which outputs::

    ['voluptatem doloribus consectetur est ut ducimus',
     'beatae enim quia vel',
     'voluptas blanditiis repellendus animi ducimus error sapiente et suscipit',
     'et fugit quas eum in in aperiam quod',
     'consequatur id enim sunt et et',
     'repudiandae ea animi iusto',
     'aliquid eos sed fuga est maxime repellendus',
     'odio quis facere architecto reiciendis optio',
     'fugiat quod pariatur odit minima',
     'voluptatem laborum magni']

The one thing you have to do is configure this API. The module
``jsonplaceholderconfig`` in the example above is configured like this::

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

For more information about qrest and its usage, we refer to the documentation.

If you want to contribute to qrest itself, we refer to the developer README that
is located in the root directory of the repo.

.. _JSONPlaceholder website: https://jsonplaceholder.typicode.com
.. _requests: https://requests.readthedocs.io/en/master/
