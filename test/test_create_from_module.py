import inspect
import unittest
import unittest.mock as mock

import ddt

import qrest
from qrest import APIConfig, BodyParameter, QueryParameter
from qrest import ResourceConfig
from qrest.exception import RestClientConfigurationError
from qrest.resource import JSONResource


class JsonPlaceHolderConfig(APIConfig):
    url = "https://jsonplaceholder.typicode.com"
    default_headers = {"Content-type": "application/json; charset=UTF-8"}


class AllPosts(ResourceConfig):
    name = "all_posts"
    path = ["posts"]
    method = "GET"
    description = "retrieve all posts"


class CreateAPIFromModuleTests(unittest.TestCase):
    def test_all_posts_becomes_an_attribute(self):

        api = qrest.API(inspect.getmodule(self))
        self.assertIsInstance(api.all_posts, JSONResource)

    def test_raise_proper_exception_when_multiple_APIConfig_classes_are_present(self):
        registry = mock.Mock()
        registry.retrieve.return_value = [mock.Mock(), mock.Mock()]
        with mock.patch("qrest.resource.ModuleClassRegistry", return_value=registry):
            message = "Imported module '.*' contains more than 1 subclass of APIConfig."
            with self.assertRaisesRegex(RestClientConfigurationError, message):
                _ = qrest.API(inspect.getmodule(self))

    def test_raise_proper_exception_when_no_APIConfig_class_is_present(self):
        registry = mock.Mock()
        registry.retrieve.return_value = []
        with mock.patch("qrest.resource.ModuleClassRegistry", return_value=registry):
            message = "Imported module '.*' does not contain a subclass of APIConfig."
            with self.assertRaisesRegex(RestClientConfigurationError, message):
                _ = qrest.API(inspect.getmodule(self))

    def test_raise_proper_exception_when_ResourceConfig_class_is_without_name(self):
        class WithoutName(ResourceConfig):
            path = ["without", "name"]
            method = "GET"

        registry = mock.Mock()
        registry.retrieve.return_value = [WithoutName]
        with mock.patch("qrest.resource.ModuleClassRegistry", return_value=registry):
            message = "Imported class '.*' does not have a 'name' attribute."
            with self.assertRaisesRegex(RestClientConfigurationError, message):
                _ = qrest.API(inspect.getmodule(self))


@ddt.ddt
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

    @ddt.data("path", "method")
    def test_raise_proper_exception_when_required_attribute_is_missing(self, attribute):
        class MyConfig(ResourceConfig):
            name = "my_config"
            path = ["my", "config"]
            method = "GET"

        delattr(MyConfig, attribute)

        with self.assertRaisesRegex(
            RestClientConfigurationError, f"Required attribute '{attribute}' is missing"
        ):
            _ = MyConfig.create()

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
