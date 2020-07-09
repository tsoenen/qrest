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
