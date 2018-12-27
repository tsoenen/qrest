'''
Contains a set of utilities used by other modules
'''

import six
from contracts import new_contract


# ================================================================================================
# Define new Python 2 & 3 compatible string contracts
string_type_or_none = new_contract(
    'string_type_or_none',
    lambda s: s is None or isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract that allows None as well. """

string_type = new_contract(
    'string_type',
    lambda s: isinstance(s, six.string_types))
"""A Python 2 & 3 compatible string type contract. """
