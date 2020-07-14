from qrest import APIConfig, ResourceConfig, BodyParameter, QueryParameter


class JsonPlaceHolderConfig(APIConfig):
    url = "https://jsonplaceholder.typicode.com"
    default_headers = {"Content-type": "application/json; charset=UTF-8"}


class AllPosts(ResourceConfig):
    name = "all_posts"
    path = ["posts"]
    method = "GET"
    description = "retrieve all posts"


class FilterPosts(ResourceConfig):

    name = "filter_posts"
    path = ["posts"]
    method = "GET"
    description = "retrieve all posts from the given author"

    user_id = QueryParameter(name="userId", description="the user ID of the author of the post")


class SinglePost(ResourceConfig):

    name = "single_post"
    path = ["posts", "{item}"]
    method = "GET"
    description = "Retrieve a single post"
    path_description = {"item": "select the post ID to retrieve"}
    headers = {"X-test-post": "qREST python ORM"}


class Comments(ResourceConfig):

    name = "comments"
    path = ["posts", "{post_id}", "comments"]
    method = "GET"
    description = "Retrieve comments for a single post"
    path_description = {"post_id": "select the post ID to retrieve"}


class CreatePost(ResourceConfig):

    name = "create_post"
    path = ["posts"]
    method = "POST"
    description = "Create a new post"

    title = BodyParameter(name="title", required=True, description="The title of the post")
    content = BodyParameter(name="body", required=True, description="The content of the post")
    user_id = BodyParameter(
        name="userId",
        required=False,
        default=101,
        description="The id of the user creating the post",
    )
