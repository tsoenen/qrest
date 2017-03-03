import six

#centralized import from external libraries
from django.core.validators import URLValidator
from contracts import contract, new_contract


# Define new Python 2 & 3 compatible string contracts
string_type_or_none = new_contract(
    'string_type_or_none',
    lambda s: s is None or isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract that allows None as well. """

string_type = new_contract(
    'string_type',
    lambda s: isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract. """


class InvalidResourceError(KeyError):
    """An error when specifying an invalid resource for a given REST API."""
    def __init__(self, name, resource):
        """ InvalidResourceError constructor

            :param name: The name of the REST API client
            :type name: ``string``

            :param resource: The REST API resource name
            :type resource: ``string``

        """
        super("'{resource}' is not a valid resource for '{name}'".format(
            resource=resource,
            name=name
        ))

