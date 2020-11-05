__version__ = "3.1.2-dev"

from .resource import JSONResource  # noqa: F401
from .conf import APIConfig, ResourceConfig, BodyParameter, QueryParameter  # noqa: F401
from .exception import RestClientConfigurationError  # noqa: F401
from .resource import API  # noqa: F401
