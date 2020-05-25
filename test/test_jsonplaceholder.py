import unittest

import rest_client
from rest_client import APIConfig, RestClientConfigurationError
from rest_client import QueryParameter, BodyParameter, ResourceConfig
from rest_client import JsonResource
from rest_client.auth import UserPassAuthConfig


class JsonPlaceHolderConfig(APIConfig):
	url = 'https://jsonplaceholder.typicode.com'
	ep = ResourceConfig(path=['posts'], method='GET')



class TestJsonPlaceHolder(unittest.TestCase):

	def setUp(self):
		self.config = JsonPlaceHolderConfig()

	def test_minimal_config(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		y = 1

