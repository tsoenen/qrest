from qrest import APIConfig, ResourceConfig, QueryParameter


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
