qrest is a Python package that allows you to build a Python API to send requests
to a REST API.

Overview
********

Let's have a look at the REST API that is provided by the JSONPlaceholder
website for testing and prototyping. If you sent a GET request to retrieve all
posts, you get a response with a text string in JSON format::

    $ curl jsonplaceholder.typicode.com/posts
    [
      {
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
      },
      {
        "userId": 1,
        "id": 2,
        "title": "qui est esse",
        "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
      },
      ...

qrest allows you to build an API that can query the JSONPlaceholder API like
this::

    import qrest
    from jsonplaceholder import JSONPlaceholderConfig

    api = qrest.API(JSONPlaceholderConfig())
    posts = api.all_posts.fetch()

    print(posts[0:2])

If you want to retrieve a post with a specific title::

    post = api.filter_posts(title="qui est esse")

    print(post)

To make this possible, you have to provide the API config such as the
JSONPlaceholderConfig in the example above::

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
