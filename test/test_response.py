import unittest
import unittest.mock as mock

import requests

from qrest.response import CSVResponse, JSONResponse

# the following content has been copied from the response to
# https://jsonplaceholder.typicode.com/posts and extended
_POSTS = [
    {
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": {
            "intro": "alea iacta est",
            "main": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto",  # noqa: E501
        },
    },
    {
        "userId": 1,
        "id": 2,
        "title": "qui est esse",
        "body": {
            "intro": "et tu, Brute?",
            "main": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla",  # noqa: E501
        },
    },
]


class JSONResponseTests(unittest.TestCase):
    def test_fetch_all_posts(self):
        all_posts = _POSTS
        mock_response = self._create_mock_response(all_posts)

        response = JSONResponse()(mock_response)

        expected_content = all_posts
        self.assertEqual(expected_content, response.fetch())

    def _create_mock_response(self, json):
        mock_response = mock.Mock(spec=requests.Response)
        mock_response.headers = {"Content-type": "application/json; charset=UTF-8"}
        mock_response.json = mock.Mock(return_value=json)
        return mock_response

    def test_raise_exception_on_incorrect_content_type(self):
        all_posts = _POSTS
        mock_response = self._create_mock_response(all_posts)
        mock_response.headers = {"Content-type": "text; charset=UTF-8"}

        regex = ".* response did not give a JSON but a text;.*"
        with self.assertRaisesRegex(TypeError, regex):
            _ = JSONResponse()(mock_response)  # noqa

    def test_fetch_single_post(self):
        single_post = _POSTS[0]
        mock_response = self._create_mock_response(single_post)

        response = JSONResponse()(mock_response)

        expected_content = single_post
        self.assertEqual(expected_content, response.fetch())

    def test_fetch_body_of_single_post(self):
        single_post = _POSTS[0]
        mock_response = self._create_mock_response(single_post)

        response = JSONResponse(extract_section=["body"])(mock_response)

        expected_content = single_post["body"]
        self.assertEqual(expected_content, response.fetch())
        self.assertEqual(expected_content, response.results)

    def test_fetch_intro_of_single_post(self):
        single_post = _POSTS[0]
        mock_response = self._create_mock_response(single_post)

        response = JSONResponse(extract_section=["body", "intro"])(mock_response)

        expected_content = single_post["body"]["intro"]
        self.assertEqual(expected_content, response.fetch())
        self.assertEqual(expected_content, response.results)


class CSVResponseTests(unittest.TestCase):
    def test_fetch_multiline_text_with_commas(self):
        mock_response = self._create_mock_response()

        response = CSVResponse()(mock_response)

        expected_content = [
            ["Lorem ipsum dolor sit amet", " consectetur adipiscing elit", " sed do eiusmod"],
            ["tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam", ""],
            ["quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo"],
            ["consequat."],
        ]
        self.assertEqual(expected_content, response.fetch())

    def _create_mock_response(self):
        text = b"""Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat."""

        mock_response = mock.Mock(spec=requests.Response)
        mock_response.headers = {"Content-type": "text/csv; charset=UTF-8"}
        mock_response.content = text

        return mock_response

    def test_raise_exception_on_incorrect_content_type(self):
        mock_response = self._create_mock_response()
        mock_response.headers = {"Content-type": "application/json; charset=UTF-8"}

        regex = ".* response did not give a CSV but a application/json;.*"
        with self.assertRaisesRegex(TypeError, regex):
            _ = CSVResponse()(mock_response)  # noqa
