import unittest

import qrest
from qrest import APIConfig
from qrest import ResourceConfig
from qrest.resource import JSONResource


class JsonPlaceHolderConfig(APIConfig):
    url = "https://jsonplaceholder.typicode.com"
    default_headers = {"Content-type": "application/json; charset=UTF-8"}


class AllPosts(ResourceConfig):
    name = "all_posts"
    path = ["posts"]
    method = "GET"
    description = "retrieve all posts"


def find_endpoints(o):
    return {AllPosts.name: AllPosts.create()}


class AlternativeConfigurationTests(unittest.TestCase):
    def test_all_posts_becomes_an_attribute(self):

        api = qrest.API(JsonPlaceHolderConfig(find_endpoints=find_endpoints))
        self.assertIsInstance(api.all_posts, JSONResource)
