from bcs_rest_client.utils import string_type, string_type_or_none
import requests
import os
import threading
from netrc import netrc
import logging
from uritools import urisplit
from requests.auth import _basic_auth_str

# ==========================================================================================
class AuthConfig(object):
	'''
	Configuration and validation for custom authentication schemas
	'''
	pass


class BasicAuthentication(requests.auth.AuthBase):
	'''
	Standard authentication methods and credentials
	'''

	def __init__(self, rest_client):
		"""
		basic auth that uses user/pass or netrc
		
		:param rest_client: A reference to the RESTclient object
		:type rest_client: ``RESTclient``

		"""

		self.rest_client = rest_client
		self.netrc_path = os.path.expanduser("~/.netrc")
		self.username = None
		self.password = None

	def __call__(self, r):
		r.headers['Authorization'] = _basic_auth_str(self.username, self.password)
		return r

	def is_valid_credential(self, credential):
		""" Determines whether the given credential is valid.
		    The credential should not be None and should not be the empty string.

		    :param credential: The credential to check
		    :type credential: ``string_type_or_none``
		"""
		return credential is not None and credential.strip() != ""

	def are_valid_credentials(self, username, password):
		""" Determines whether given credentials are valid.
		    Both username and password should not be None and should not be the empty string.

		    :param username: The username to check
		    :type username: ``string_type_or_none``

		    :param password: The password to check
		    :type password: ``string_type_or_none``
		"""
		return self.is_valid_credential(username) and self.is_valid_credential(password)

	# -------------------------------------------------------------------------------
	def login(self, username=None, password=None):
		""" Explicitly do a login with supplied username and password.
		    If username and password are supplied, it will use those to login.
		    If either or both username and/or password is missing, will try to retrieve the credentials from the netrc file.

		    :param username: The user for authenticating with the CAS end-point
		    :type username: ``string_type_or_none``

		    :param password: The password for authenticating with the CAS end-point
		    :type password: ``string_type_or_none``
		"""
		if not self.are_valid_credentials(username, password):
			if self.netrc_path is not None:
				logging.debug("[CAS] Username and/or password were None. Retrieving using netrc.")
				nrc = netrc(file=self.netrc_path)
				host = urisplit(self.rest_client.url).host
				try:
					(netrc_login, _, netrc_password) = nrc.authenticators(host)
				except TypeError:
					raise ValueError("No credentials found for host '{host}' or 'default' in the netrc file at location '{location}'".format(host=host, location=self.netrc_path))
				if self.are_valid_credentials(netrc_login, netrc_password):
					self.username = netrc_login
					self.password = netrc_password
				else:
					raise ValueError("No valid credentials found for host '{host}' or 'default' in the netrc file at location '{location}'".format(host=host, location=self.netrc_path))
			else:
				raise ValueError("No or empty username and/or password supplied while netrc path is None")
		else:
			self.username = username
			self.password = password


# ==========================================================================================	

class CASAuth(BasicAuthentication):

	def __init__(self, rest_client, config):
		"""
		CASAuth constructor

		:param rest_client: A reference to the RESTclient object
		:type rest_client: ``RESTclient``

		:param credential: The configuration object
		:type credential: ``BasicAuthConfig``

		"""

		super(CASAuth, self).__init__(rest_client)
		
		self.server = None
		self.ticket_path = '/'.join(config.path)
		self.service = config.service_name
		self.tgt_path = config.granting_ticket_filepath
		self.verify_ssl = config.verify_ssl

		
		# Keep state in per-thread local storage
		self._thread_local = threading.local()


	def init_per_thread_state(self):
		""" Initializes a state per thread used.
		"""
		# Ensure state is initialized just once per-thread
		if not hasattr(self._thread_local, 'init'):
			self._thread_local.init = True
			self._thread_local.renew_ticket = False


	def login(self, server_url, username=None, password=None):
		""" Explicitly do a login with supplied username and password.
		    If username and password are supplied, it will use those to login.
		    If either or both username and/or password is missing, will try to retrieve the credentials from the netrc file.
		    Finally, generates a TGT and writes it to disk.

		    :param username: The user for authenticating with the CAS end-point
		    :type username: ``string_type_or_none``

		    :param password: The password for authenticating with the CAS end-point
		    :type password: ``string_type_or_none``
		"""
		super(CASAuth, self).login(username=username, password=password)
		self.server = server_url 
		self.generate_tgt(overwrite=True)

	def get_service_ticket(self):
		""" Retrieves the service ticket that will ultimately be used inside the request to the REST end-point.

		    :return: The text or token to be used inside the Authorization header of the RESTful request
		    :rtype: ``string_type``
		"""
		tgt_url = self.read_tgt()
		body = {"service": self.service}
		ro = requests.post(url=tgt_url,
		                   data=body,
		                   verify=self.verify_ssl)
		if (ro.status_code != requests.codes.get("ok")):
			self.get_tgt_and_write()
			tgt_url = self.read_tgt()
			ro = requests.post(url=tgt_url, data=body)
			if (ro.status_code != requests.codes.get("ok")):
				raise RuntimeError("Cannot authenticate against CAS using provided 'username' and 'password'. HTTP status code: '{status}'".format(status=ro.status_code))
		return(ro.text)

	def get_tgt_and_write(self):
		""" Retrieves the ticket getting ticket that will ultimately be used inside the request to the CAS end-point for retrieving a service ticket.
		    If the "tgtPath" parameter isn't pointing to an existing location, that location will be created.
		    If the file at "tgtPath" exists, it will be replaced by the newly retrieved TGT.
		"""
		if not self.are_valid_credentials(self.username, self.password):
			logging.debug("[CAS] Username and/or password were not valid. Trying to do a login.")
			self.login()

		ticket_url = "{server}/{path}".format(server=self.server, path=self.ticket_path)
		
		ro = requests.post(url=ticket_url,
		                   data={"username": self.username, "password": self.password},
		                   verify=self.verify_ssl)
		if ((ro.status_code < 200) or (ro.status_code >= 300)):
			raise RuntimeError("Cannot authenticate against CAS using provided 'username' and 'password'. HTTP status code: '{status}'".format(status=ro.status_code))
		tgt_location = ro.headers["location"]
		logging.debug("[CAS] TGT URI is '{location}'".format(location=tgt_location))
		tgt_dir = os.path.dirname(self.tgt_path)
		if (not os.path.isdir(tgt_dir)):
			os.makedirs(tgt_dir)
		if os.path.isfile(self.tgt_path):
			os.remove(self.tgt_path)
		with open(self.tgt_path, "w") as tgt_file:
			tgt_file.write(tgt_location)

	def read_tgt(self):
		""" Reads the ticket getting ticket that will ultimately be used inside the request to the CAS end-point for retrieving a service ticket.
		    The "tgtPath" parameter has to point to an existing location.

		    :return: The URL to be used for retrieving a service ticket from the CAS end-point
		    :rtype: ``string_type``
		"""
		if (not os.path.isfile(self.tgt_path)):
			self._thread_local.renew_ticket = False
			raise RuntimeError("[CAS] File '{tgt_path}' does not exist.".format(tgt_path=self.tgt_path))
		else:
			with open(self.tgt_path, 'r') as tgt_file:
				tgt = tgt_file.read().strip()
			logging.debug("[CAS] TGT contents are '{tgt}'".format(tgt=tgt))
			if tgt == "":
				os.remove(self.tgt_path)
				raise ValueError("[CAS] TGT file at '{tgt_path}' was empty and has been removed.".format(tgt_path=self.tgt_path))
			else:
				return tgt

	def generate_tgt(self, overwrite=False):
		""" Generates a TGT file by calling "get_tgt_and_write".
		"""
		if overwrite or (not os.path.isfile(self.tgt_path)):
			logging.debug("[CAS] File '{tgt_path}' does not exist or 'overwrite' is True. A new one will be created.".format(tgt_path=self.tgt_path))
			self.get_tgt_and_write()
		else:
			logging.debug("[CAS] File '{tgt_path}' does exist and 'overwrite' is False. The current one will be used.".format(tgt_path=self.tgt_path))

	def __call__(self, r):
		""" Is called when authentication is needed before issuing a RESTful request.
		    Will retrieve and create a new TGT file if necessary.
		    Will retrieve a new service ticket or token if necessary.
		    Adds the Authorization header and supplies the correct service ticket or token to it.
		"""
		# Initialize per-thread state, if needed
		self.init_per_thread_state()
		renew_ticket = self._thread_local.renew_ticket
		if renew_ticket:
			logging.debug("[CAS] Renewing service ticket")
			service_ticket = self.get_service_ticket()
			r.headers['Authorization'] = "CAS {service_ticket}".format(service_ticket=service_ticket)
		else:
			self.generate_tgt()
			self._thread_local.renew_ticket = True
			return self.__call__(r)
		return r


# ==========================================================================================	
class BasicAuthConfig(AuthConfig):
	'''
	Configuration and validation for custom authentication schemas
	'''

	authentication_module = BasicAuthentication


# ==========================================================================================	
class CasAuthConfig(AuthConfig):
	'''
	CAS authentication specific for the CLS implementation below
	'''

	authentication_module = CASAuth

	def __init__(self, path, service_name, granting_ticket_filepath, verify_ssl):
		'''
		:param path: The relative path for the ticket granting tickets 
		:type path: ``list``

		:param service: The service name used to authenticate with the CAS end-point
		:type service: ``string_type``

		:param granting_ticket_filepath: The local path where a "ticket getting ticket" will be saved
		:type granting_ticket_filepath: ``string_type``

		:param verify_ssl: Whether the CAS client should verify SSL certificates upon making requests
		:type verify_ssl: ``bool``

		'''
		self.path = path
		self.service_name = service_name
		self.granting_ticket_filepath =  granting_ticket_filepath
		self.verify_ssl = verify_ssl

