"""Implements ModuleClassRegistry."""
import inspect


class ModuleClassRegistry:
    """Allows you to retrieve the classes that are defined in an imported module."""

    def __init__(self, imported_module):
        """Store the module from which the classes should be retrieved."""
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
