import unittest
import unittest.mock as mock

import qrest
from qrest import APIConfig, BodyParameter, QueryParameter
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


class ResourceConfigCreateTests(unittest.TestCase):
    def test_pass_required_attributes(self):
        class MyConfig(ResourceConfig):
            name = "my_config"
            path = ["my", "config"]
            method = "GET"

        with mock.patch.object(MyConfig, "__init__", return_value=None) as init_dunder:
            _ = MyConfig.create()

            args, kwargs = init_dunder.call_args

            self.assertEqual((["my", "config"], "GET"), args)
            self.assertDictEqual({}, kwargs)

    def test_pass_named_optional_attributes(self):
        class MyConfig(ResourceConfig):
            name = "my_config"
            path = ["my", "config"]
            method = "GET"
            description = "a ResourceConfig used for testing"
            headers = {"Content-type": "text/csv; charset=UTF-8"}

        with mock.patch.object(MyConfig, "__init__", return_value=None) as init_dunder:
            _ = MyConfig.create()

            _, kwargs = init_dunder.call_args

            expected_kwargs = {"description": MyConfig.description, "headers": MyConfig.headers}
            self.assertDictEqual(expected_kwargs, kwargs)

    def test_dont_pass_unknown_attribute(self):
        class MyConfig(ResourceConfig):
            name = "my_config"
            path = ["my", "config"]
            method = "GET"
            hello = "world"

        with mock.patch.object(MyConfig, "__init__", return_value=None) as init_dunder:
            _ = MyConfig.create()

            args, kwargs = init_dunder.call_args

            self.assertEqual((["my", "config"], "GET"), args)
            self.assertDictEqual({}, kwargs)

    def test_pass_parameter_configs(self):
        class MyConfig(ResourceConfig):
            name = "my_config"
            path = ["my", "config"]
            method = "GET"

            title = BodyParameter(name="title")
            user_id = QueryParameter(name="userId")

        with mock.patch.object(MyConfig, "__init__", return_value=None) as init_dunder:
            _ = MyConfig.create()

            expected_parameters = {"title": MyConfig.title, "user_id": MyConfig.user_id}

            _, kwargs = init_dunder.call_args
            self.assertDictEqual({"parameters": expected_parameters}, kwargs)
