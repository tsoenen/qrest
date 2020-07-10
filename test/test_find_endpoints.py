import inspect
import unittest

from qrest import APIConfig, ResourceConfig


class FindEndpointsConfig(APIConfig):
    pass


class FirstResourceConfig(ResourceConfig):
    name = "first"
    path = ["my", "first", "resource", "config"]
    method = "GET"


class SecondResourceConfig(ResourceConfig):
    name = "second"
    path = ["my", "first", "resource", "config"]
    method = "GET"


def find_api_config_class(module):
    for name, value in inspect.getmembers(module):
        # the member should be defined in the given module
        if inspect.getmodule(value) == module:
            # issubclass requires its first argument to be a class
            if inspect.isclass(value) and issubclass(value, APIConfig):
                return value


class FindAPIConfigTests(unittest.TestCase):
    def test_return_APIConfig_from_given_module(self):
        current_module = inspect.getmodule(FindEndpointsConfig)
        config_class = find_api_config_class(current_module)
        self.assertTrue(
            issubclass(config_class, FindEndpointsConfig),
            f"Class {config_class} should be a subclass of FindEndpointsConfig",
        )


def find_endpoints(config_class):
    endpoints = {}
    module = inspect.getmodule(config_class)
    for name, value in inspect.getmembers(module):
        if inspect.isclass(value) and inspect.getmodule(value) == module:
            if issubclass(value, ResourceConfig):
                endpoints[value.name] = value.create()
    return endpoints


class FindEndpointTests(unittest.TestCase):
    def test_initial(self):
        configs = find_endpoints(FindEndpointsConfig)

        self.assertEqual(2, len(configs), "Two endpoints should have been found")
        self.assertSetEqual(set(["first", "second"]), set(configs.keys()))
        self.assertIsInstance(configs["first"], FirstResourceConfig)
        self.assertIsInstance(configs["second"], SecondResourceConfig)
