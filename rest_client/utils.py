""" Contains a set of related and unrelated functions and classes used elsewhere in this module
"""

import logging
from urllib.parse import urlparse
from .exception import RestClientConfigurationError

logger = logging.getLogger(__name__)


# ###############################################################
class URLValidator:
    """
    lightweight URL validation checker. This is a minimal implementation compared to e.g. the
    Django validation checker, as the configs are mostly supposed to be fixed in advance of usage.
    """

    def __init__(self, schemes=None):
        """
        set the restrictions imposed on the URL to be checked
        """
        pass

    # ------------------------------------------------------------------
    def check(self, url, require_path=True):
        """
        check if the presented URL is valid
        """

        final_url = urlparse(url)
        if not all([final_url.scheme, final_url.netloc]):
            raise RestClientConfigurationError(f"the URL {url} is not valid")
        if len(final_url.netloc.split(".")) == 1 and final_url.netloc != "localhost":
            raise RestClientConfigurationError(f"the URL {url} is has no domain indication")
        if require_path and not final_url.path:
            raise RestClientConfigurationError(f"the URL {url} has no valid path")
