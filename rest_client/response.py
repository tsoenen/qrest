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
from .exception import RestResourceMissingContentError

disable_warnings(InsecureRequestWarning)
logger = logging.getLogger(__name__)

# =================================================================================================

class RestResponse(ABC):

	'''
	Abstract Base class wrapper around the REST response. This is meant to process the returned data
	obtained from the REST request into a python object
	'''

	def __init__(self, response: Type[requests.models.Response], options: Optional[dict] = None):
		""" RestResponse constructor

		    :param response: The Requests Response object
		    :param options: The options object specifying the JSON options for returning results

		"""
		if not isinstance(response, requests.models.Response):
			raise TypeError('RestResponse expects a requests.models.Response as input')

		self._response = response
		self.headers = response.headers
		self.raw = response.content
		self.options = options

		#prepare the content to a python object
		self.data = self._parse()

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
class JSONRestResponse(RestResponse):

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

		#subset the response dictionary
		json = copy.deepcopy(self._response.json())
		if isinstance(json, dict):
			if ("root" in self.options) and (len(self.options["root"]) > 0):
				for element in self.options["root"]:
					if element in json:
						json = json[element]
					else:
						raise RestResourceMissingContentError(f"Element {element} could not be found")

		# create data objects
		return json


#  =========================================================================================================
class CSVRestResponse(RestResponse):

	def _check_content(self):
		if not 'text/csv' in content_type:
			raise TypeError(f'the REST response did not give a CSV but a {content_type}')

	def _parse(self) -> list:
		''' processes a raw CSV into lines. For very large content this may be better served by a generator
		'''
		
		data = self._response.content
		self.raw = data.decode('UTF-8')
		data = self.raw.strip().split('\n')
		return [x.split(",") for x in data]
