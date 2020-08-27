"""This module contains the Response objects. A response object is a wrapper
around the data the comes from the REST server after the client asks for it.

"""

import copy
import requests
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ================================================================================================
# local imports
from .exception import RestResourceMissingContentError, RestClientConfigurationError

disable_warnings(InsecureRequestWarning)
logger = logging.getLogger(__name__)

# =================================================================================================


class Response(ABC):

    """Abstract Base class wrapper around the REST response. This is meant to process the returned
    data obtained from the REST request into a python object

    :param data: stores the data of interest of the REST response

    Attribute data is initialized to None and should be set in method _parse.

    """

    _response = None
    headers = None
    raw = None
    options = None

    data = None

    def __call__(self, response: Type[requests.models.Response]):
        """ RestResponse wrapper call
            :param response: The Requests Response object
        """
        if not self.options:
            # raise RestClientConfigurationError('configuration is not set for API Response')
            logger.warning("No options are provided")

        if not isinstance(response, requests.models.Response):
            raise TypeError("RestResponse expects a requests.models.Response as input")

        self._response = response
        self.headers = response.headers
        self.raw = response.content

        # We also store the headers with lowercase field names so we become
        # independent of the case of each field name. For example, a response
        # header can have field "Content-Type", but field "content-type" is
        # also allowed.
        self._headers_lowercase = {name.lower(): value for name, value in self.headers.items()}

        self._check_content()
        self._parse()
        return self

    def fetch(self):
        """Return the data of interest of the REST response."""
        return self.data

    @abstractmethod
    def _check_content(self):
        pass

    @abstractmethod
    def _parse(self):
        """Parse the REST response and let self.data contain the data of interest."""
        pass


#  =========================================================================================================
class JSONResponse(Response):
    def __init__(
        self, extract_section: Optional[list] = None, create_attribute: Optional[str] = "results"
    ):
        """
        Special Wrapper to handle JSON responses. It takes the response object and creates a
        dictionary.
        Optionally it allows extraction of a payload subsection to a user-defined attribute. In all
        cases the raw data goes to the 'data' property'.

        :param extract_section: This indicates which part of the obtained JSON response contains
            the main payload that should be extracted. The tree is provided as a list of items to
            traverse
        :param create_attribute: The name of the attribute that will contain the aforementioned
            payload subsection.

        """

        if extract_section and not isinstance(extract_section, list):
            raise RestClientConfigurationError("extract_section option is not a list")
        self.extract_section = extract_section
        self.create_attribute = create_attribute

    def _check_content(self):
        content_type = self._headers_lowercase.get("content-type", "unknown")
        if "json" not in content_type:
            raise TypeError(f"the REST response did not give a JSON but a {content_type}")

    def _parse(self):
        """ Returns the JSON contained in the Requests Response object, following the options
        specified in the JSON configuration

        :return: A dictionary containing the Requests Response object, adapted to the JSON
            configuration
        :rtype: ``dict``
        """

        # replace content by decoded content
        self.raw = copy.deepcopy(self._response.json())

        # subset the response dictionary
        json = copy.deepcopy(self._response.json())
        if isinstance(json, dict) and self.extract_section:
            for element in self.extract_section:
                if element in json:
                    json = json[element]
                else:
                    raise RestResourceMissingContentError(f"Element {element} could not be found")
        setattr(self, self.create_attribute, json)
        self.data = json


class CSVResponse(Response):
    """Wrap a REST response for content type text/csv.

    This class shows how to support different content types with their own
    content processing.

    """

    def _check_content(self):
        content_type = self._headers_lowercase.get("content-type", "unknown")
        if "text/csv" not in content_type:
            raise TypeError(f"the REST response did not give a CSV but a {content_type}")

    def _parse(self) -> List[List[str]]:
        """ processes a raw CSV into lines. For very large content this may be better served by a generator
        """
        content = self._response.content
        self.raw = content.decode("UTF-8")

        lines = self.raw.strip().split("\n")
        self.data = [line.split(",") for line in lines]
