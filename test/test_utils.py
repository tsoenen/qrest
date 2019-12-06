import unittest
from rest_client.utils import URLValidator
from rest_client.exception import RestClientConfigurationError

class TestURLValidator(unittest.TestCase):

	def setUp(self):
		self.validator = URLValidator()

	def tearDown(self):
		pass

	def test_good_urls(self):
		'''
		check if a valid URL is set to valid
		'''
		self.validator.check('http://google.com', require_path=False)
		self.validator.check('https://www.google.com/search?q=test', require_path=False)
		self.validator.check('https://www.google.com/search?q=test', require_path=True)

	def test_bad_urls(self):
		'''
		check if an invalid URL is set to invalid
		'''

		with self.assertRaises(RestClientConfigurationError):
			self.validator.check('http://google.com', require_path=True)

		with self.assertRaises(RestClientConfigurationError):
			self.validator.check('test', require_path=True)
