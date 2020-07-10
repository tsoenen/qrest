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


class ModuleClassRegistry:
    """Allows you to retrieve the classes that are defined in an imported module."""

    def __init__(self, imported_module):
        """Store the module from which the classes can be retrieved."""
        self._module = imported_module

    def retrieve(self, base_class):
        """Return all subclasses of the given base class.

        The classes returned are defined in the imported module.

        """
        classes = []
        for name, value in inspect.getmembers(self._module):
            # the member should be defined in the given module
            if inspect.getmodule(value) == self._module:
                # issubclass requires its first argument to be a class
                if inspect.isclass(value) and issubclass(value, base_class):
                    classes.append(value)
        return classes


class ModuleClassRegistryTests(unittest.TestCase):
    def setUp(self):
        self.current_module = inspect.getmodule(ModuleClassRegistryTests)

    def test_find_APIConfig_classes(self):
        classes = ModuleClassRegistry(self.current_module)
        config_classes = classes.retrieve(APIConfig)
        self.assertEqual(
            1, len(config_classes), "the current module should contain a single APIConfig class"
        )
        self.assertTrue(
            issubclass(config_classes[0], FindEndpointsConfig),
            f"Class {config_classes[0]} should be a subclass of APIConfig",
        )

    def test_find_ResourceConfig_classes(self):
        classes = ModuleClassRegistry(self.current_module)
        config_classes = classes.retrieve(ResourceConfig)
        self.assertEqual(
            2, len(config_classes), "the current module should contain 2 ResourceConfig classes"
        )
        for config_class in config_classes:
            self.assertTrue(
                issubclass(config_class, ResourceConfig),
                f"Class {config_class} should be a subclass of ResourceConfig",
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
