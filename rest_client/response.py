'''
This module contains the Response objects. A response object is a wrapper around the data the comes from the
REST server after the client asks for it. 
'''

import copy
import requests
import logging
from abc import ABC, abstractmethod
from typing import Optional, Type

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ================================================================================================
# local imports
from .exception import RestResourceMissingContentError, RestClientConfigurationError

disable_warnings(InsecureRequestWarning)
logger = logging.getLogger(__name__)

# =================================================================================================

class Response(ABC):

	'''
	Abstract Base class wrapper around the REST response. This is meant to process the returned data
	obtained from the REST request into a python object
	'''

	_response = None
	headers = None
	raw = None
	options = None

	@abstractmethod
	def __init__(self):
		""" RestResponse constructor
		This should be overridden by subclasses so that required parameters are visible through introspection
		"""


	def __call__(self, response: Type[requests.models.Response]):
		""" RestResponse wrapper call
		    :param response: The Requests Response object
		"""
		if not self.options:
			# raise RestClientConfigurationError('configuration is not set for API Response')
			logger.warn('No options are provided')
		
		if not isinstance(response, requests.models.Response):
			raise TypeError('RestResponse expects a requests.models.Response as input')

		self._response = response
		self.headers = response.headers
		self.raw = response.content

		#prepare the content to a python object
		self._parse()
		return self

	def fetch(self):
		'''
		systematic function to indicate that the required content is to be delivered
		'''
		return self.data


	@abstractmethod
	def _check_content(self):
		pass


	@abstractmethod
	def _parse(self):
		pass



#  =========================================================================================================
class JSONResponse(Response):

	def __init__(self, extract_section: Optional[list] = None, create_attribute: Optional[str] = 'results'):
		'''
		Special Wrapper to handle JSON responses. It takes the response object and creates a dictionary.
		Optionally it allows extraction of a payload subsection to a user-defined attribute. In all cases the
		raw data goes to the 'data' property'.
		
		:param extract_section: This indicates which part of the obtained JSON response contains the main
		    payload that should be extracted. The tree is provided as a list of items to traverse
		:param create_attribute: The "results_name" which is the property that will be generated to contain
		    the previously obtained subsection of the json tree
		
		'''

		if extract_section and not isinstance(extract_section, list):
			raise RestClientConfigurationError("extract_section option is not a list")
		self.extract_section = extract_section
		self.create_attribute = create_attribute

	def _check_content(self):
		content_type = self.headers.get('content-type', 'unknown')
		if not "json" in content_type:
			raise TypeError(f'the REST response did not give a JSON but a {content_type}')

	def _parse(self):
		""" Returns the JSON contained in the Requests Response object, following the options specified in the JSON configuration

		    :return: A dictionary containing the Requests Response object, adapted to the JSON configuration
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


#  =========================================================================================================
class CSVRestResponse(Response):

	def _check_content(self):
		content_type = self.headers.get('content-type', 'unknown')
		if not 'text/csv' in content_type:
			raise TypeError(f'the REST response did not give a CSV but a {content_type}')

	def _parse(self) -> list:
		''' processes a raw CSV into lines. For very large content this may be better served by a generator
		'''
		
		data = self._response.content
		self.raw = data.decode('UTF-8')
		data = self.raw.strip().split('\n')
		return [x.split(",") for x in data]
