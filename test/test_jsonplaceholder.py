import unittest
import unittest.mock as mock

import requests

import qrest
from qrest.response import Response

from . import jsonplaceholderconfig


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


class TestJsonPlaceHolder(unittest.TestCase):
    def setUp(self):
        self.mock_response = mock.Mock(spec=requests.Response)
        self.mock_response.status_code = 200
        self.mock_response.content = b"Hello World!"
        # for this test we're not interested in the headers attribute of
        # the requests.Response but our Response object requires it
        self.mock_response.headers = {}

    def test_all_posts_queries_the_right_endpoint(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_all_posts_queries_the_right_endpoint_2(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_single_post_queries_the_right_endpoint(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={
                    "Content-type": "application/json; charset=UTF-8",
                    "X-test-post": "qREST python ORM",
                },
            )

            self.assertEqual(self.mock_response.content, post)

    def test_filter_posts_queries_the_right_endpoint(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, posts)

    def test_filter_posts_returns_the_response_when_called(self):
        api = qrest.API(jsonplaceholderconfig)
        api.filter_posts.response = ContentResponse()

        with mock.patch("requests.request", return_value=self.mock_response):
            response = api.filter_posts.get_response(user_id=1)
            self.assertIs(api.filter_posts.response, response)

    def test_comments_queries_the_right_endpoint(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            self.assertEqual(self.mock_response.content, comments)

    def test_create_post_help_returns_the_correct_title(self):
        api = qrest.API(jsonplaceholderconfig)
        self.assertEqual("The title of the post", api.create_post.help("title"))

    def test_create_post_accesses_the_right_endpoint_when_called(self):
        api = qrest.API(jsonplaceholderconfig)
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
                files=[],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )
            self.assertIs(api.create_post.response, response)

    def test_upload_file_accesses_the_right_endpoint_when_called(self):
        api = qrest.API(jsonplaceholderconfig)
        api.upload_file.response = ContentResponse()

        file = open(qrest.__file__, 'rb')

        with mock.patch("requests.request", return_value=self.mock_response) as mock_request:
            response = api.upload_file.get_response(file=('__init__.py', file))

            mock_request.assert_called_with(
                method="POST",
                auth=None,
                verify=False,
                url="https://jsonplaceholder.typicode.com/files",
                params={},
                json={},
                files=[('file', ('__init__.py', file))],
                headers={"Content-type": "application/json; charset=UTF-8"},
            )
            self.assertIs(api.upload_file.response, response)
