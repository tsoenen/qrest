import unittest
import unittest.mock as mock

import ddt
import requests

import qrest
from qrest import APIConfig
from qrest import QueryParameter, BodyParameter, ResourceConfig
from qrest.response import JSONResponse, Response

from . import jsonplaceholderconfig


class JsonPlaceHolderConfig(APIConfig):
    url = "https://jsonplaceholder.typicode.com"
    default_headers = {"Content-type": "application/json; charset=UTF-8"}

    all_posts = ResourceConfig(path=["posts"], method="GET", description="retrieve all posts")

    filter_posts = ResourceConfig(
        path=["posts"],
        method="GET",
        description="retrieve all posts by filter criteria",
        parameters={
            "user_id": QueryParameter(
                name="userId",
                required=False,
                # default='',
                # choices=[],
                description="the user Id that made the post",
            ),
        },
    )

    single_post = ResourceConfig(
        path=["posts", "{item}"],
        method="GET",
        description="Retrieve a single post",
        path_description={"item": "select the post ID to retrieve"},
        headers={"X-test-post": "qREST python ORM"},
    )

    comments = ResourceConfig(
        path=["posts", "{post_id}", "comments"],
        method="GET",
        description="Retrieve comments for a single post",
        path_description={"post_id": "select the post ID to retrieve"},
    )

    create_post = ResourceConfig(
        path=["posts"],
        method="POST",
        description="Create a new post",
        parameters={
            "title": BodyParameter(
                name="title",
                required=True,
                # default='',
                # choices=[],
                description="The title of the post",
            ),
            "content": BodyParameter(
                name="body",
                required=True,
                # default='',
                # choices=[],
                description="The title of the post",
            ),
            "user_id": BodyParameter(
                name="userId",
                required=False,
                default=101,
                # choices=[],
                description="The id of the user creating the post",
            ),
        },
    )


class ContentResponse(Response):
    """Provide access to the content of the requests.Response that is wrapped.

    The qrest.API uses a Response to process the requests.Response it
    receives from the endpoint. That processing requires specific responses and
    would make the setup of the API tests much more elaborate and the tests
    themselves much less focussed on the API. To work around that, we use a
    ContentResponse for the tests, which does no processing at all.

    Note that Response objects have their own tests and do not have to be
    tested by the API tests.

    """

    def __init__(self):
        pass

    def fetch(self):
        """Return the content of the requests.Response object received."""
        return self._response.content

    def _check_content(self):
        pass

    def _parse(self):
        pass


@ddt.ddt
class TestJsonPlaceHolder(unittest.TestCase):
    def setUp(self):
        self.config = JsonPlaceHolderConfig()

        self.mock_response = mock.Mock(spec=requests.Response)
        self.mock_response.status_code = 200
        self.mock_response.content = b"Hello World!"
        # for this test we're not interested in the headers attribute of
        # the requests.Response but our Response object requires it
        self.mock_response.headers = {}

    def tearDown(self):
        # In this testsuite we instantiate an API from the same APIConfig
        # multiple times. This means we are reusing the same ResourceConfig
        # objects and as such, the same processor (JSONResource). As we modify
        # the processor in our tests, we have to reset it after each test.
        for config_name in ["all_posts", "comments", "filter_posts", "single_post"]:
            config = getattr(JsonPlaceHolderConfig, config_name)
            config.processor.response = JSONResponse()

    def _create_api_from_class(self):
        return qrest.API(self.config)

    def _create_api_from_module(self):
        return qrest.API.from_module(jsonplaceholderconfig)

    @ddt.data("_create_api_from_class", "_create_api_from_module")
    def test_all_posts_queries_the_right_endpoint(self, function_name):
        api = getattr(self, function_name)()
        api.all_posts.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            posts = api.all_posts()

            mock_request.assert_called_with(
                method="GET",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts",
                params={},
                json={},
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_all_posts_queries_the_right_endpoint_2(self):
        api = qrest.API.from_module(jsonplaceholderconfig)
        api.all_posts.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            posts = api.all_posts()

            mock_request.assert_called_with(
                method="GET",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts",
                params={},
                json={},
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_single_post_queries_the_right_endpoint(self):
        api = qrest.API(self.config)
        api.single_post.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            post = api.single_post(item=1)

            mock_request.assert_called_with(
                method="GET",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts/1",
                params={},
                json={},
                headers={
                    "Content-type": "application/json; charset=UTF-8",
                    "X-test-post": "qREST python ORM",
                },
            )

            self.assertEqual(self.mock_response.content, post)

    def test_filter_posts_queries_the_right_endpoint(self):
        api = qrest.API(self.config)
        api.filter_posts.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            posts = api.filter_posts(user_id=1)

            mock_request.assert_called_with(
                method="GET",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts",
                params={"userId": 1},
                json={},
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_filter_posts_returns_the_response_when_called(self):
        api = qrest.API(self.config)
        api.filter_posts.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response):
            response = api.filter_posts.get_response(user_id=1)
            self.assertIs(api.filter_posts.response, response)

    def test_comments_queries_the_right_endpoint(self):
        api = qrest.API(self.config)
        api.comments.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            comments = api.comments(post_id=1)

            mock_request.assert_called_with(
                method="GET",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts/1/comments",
                params={},
                json={},
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, comments)

    def test_create_post_help_returns_the_correct_title(self):

        api = qrest.API(self.config)
        self.assertEqual("The title of the post", api.create_post.help("title"))

    def test_create_post_accesses_the_right_endpoint_when_called(self):
        api = qrest.API(self.config)
        api.create_post.response = ContentResponse()

        title = "new post using qREST ORM"
        content = "this is the new data posted using qREST"
        user_id = 200

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            response = api.create_post.get_response(title=title, content=content, user_id=user_id)

            mock_request.assert_called_with(
                method="POST",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/posts",
                params={},
                json={"title": title, "body": content, "userId": user_id},
                headers={"Content-type": "application/json; charset=UTF-8"},
            )
            self.assertIs(api.create_post.response, response)
