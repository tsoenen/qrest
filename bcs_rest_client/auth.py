from bcs_rest_client.utils import string_type, string_type_or_none
import requests
import os
import threading
from netrc import netrc
import logging
from uritools import urisplit
from requests.auth import _basic_auth_str

from bcs_rest_client.exception import BCSRestLoginError


# ==========================================================================================
class RESTAuthentication(requests.auth.HTTPBasicAuth):
	'''
	Standard authentication methods and credentials
	This basic authentication does not complain if user is not logging in
	explicitely. This is the most silent form of authentication
	'''
	
	is_logged_in = False
	username = None
	password = None

	def __init__(self, rest_client, auth_config_object=None):
		"""
		basic auth that uses user/pass or netrc
		this is a subclass of HTTPBasicAuth, but differs in that it requires a specific call to
		login() to allow netrc and embedding. 
		
		:param rest_client: A reference to the RESTclient object
		:type rest_client: ``RESTclient``

		"""

		self.rest_client = rest_client
		self.auth_config_object = auth_config_object
		

	@property
	def login_tuple(self):
		return (self.username, self.password)
		
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
		
		if self.is_valid_credential(username):
			return True
		else:
			if self.is_valid_credential(password):
				raise BCSRestLoginError('provided password but not a username')
			else:
				return False

	# -------------------------------------------------------------------------------
	def login(self):
		raise NotImplementedError('Define login procedure in subclass')




# ==========================================================================================	
class NoAuth(RESTAuthentication):
	'''
	Access REST server without authentication
	'''
	
	is_logged_in = True
	
	def login(self):
		raise Exception('no login required for this service')
	

# ==========================================================================================	
class UserPassAuth(RESTAuthentication):
	'''
	Authentication that enforces username / password
	'''

	is_logged_in = False

	# -------------------------------------------------------------------------------
	#def __init__(self, rest_client):
	#	super(UserPassAuth, self).__init__(rest_client)

	
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
			raise ValueError("No or empty username and/or password supplied")
		else:
			self.username = username
			self.password = password

		self.is_logged_in = True


# ==========================================================================================	
class NetRCAuth(RESTAuthentication):
	'''
	Authentication that enforces username / password
	'''

	netrc_path = os.path.expanduser("~/.netrc")
	is_logged_in = False

	# -------------------------------------------------------------------------------
	#def __init__(self, rest_client, config):
		#super(UserPassAuth, self).__init__(rest_client)


	# -------------------------------------------------------------------------------
	def login(self, netrc_path=os.path.expanduser("~/.netrc")):
		""" Explicitly do a login with supplied username and password.
		    If username and password are supplied, it will use those to login.
		    If either or both username and/or password is missing, will try to retrieve the credentials from the netrc file.

		    :param username: The user for authenticating with the CAS end-point
		    :type username: ``string_type_or_none``

		    :param password: The password for authenticating with the CAS end-point
		    :type password: ``string_type_or_none``
		"""
		
		self.netrc_path = netrc_path

		if self.netrc_path is not None:
			logging.debug("Retrieving using netrc.")
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
			raise ValueError("No Netrc path supplied")



# ==========================================================================================	
class UserPassOrNetRCAuth(RESTAuthentication):
	'''
	wrapper to allow both netRC and User+Pass logins
	'''
	
	def login(self, netrc_path=os.path.expanduser("~/.netrc"), username=None, password=None):
		"""
		Allow logins via either netRC or user/pass.
		If netrc is true, try this. Else, try user/pass if supplied.
		If neither is available, raise error

		:param netrc_path: The path to Netrc 
		:type netrc_path: ``string_type_or_none``

		:param username: The user for authenticating with the CAS end-point
		:type username: ``string_type_or_none``

		:param password: The password for authenticating with the CAS end-point
		:type password: ``string_type_or_none``
		"""

		if netrc_path:
			parent_auth = NetRCAuth(rest_client=self.rest_client, auth_config_object=self.auth_config_object)
			parent_auth.login(netrc_path=netrc_path)
		elif username and password:
			parent_auth = UserPassAuth(rest_client=self.rest_client)
			parent_auth.login(username=username, password=password)
		else:
			raise BCSRestLoginError('not enough data is provided to login')
		self.username = parent_auth.username
		self.password = parent_auth.password

		self.is_logged_in = True
	



# ==========================================================================================	

class CASAuth(RESTAuthentication):

	def __init__(self, rest_client, auth_config_object):
		"""
		CASAuth constructor

		:param rest_client: A reference to the RESTclient object
		:type rest_client: ``RESTclient``

		:param auth_config_object: The configuration object
		:type auth_config_object: ``AuthConfig``

		"""

		super(CASAuth, self).__init__(rest_client)
		
		self.server = None
		config =  auth_config_object
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


	def login(self, server_url, netrc_path=os.path.expanduser("~/.netrc"), username=None, password=None):
		"""
		CAS-auth requires a secondary auth, so it has two authentication levels...
		Allow logins via either netRC or user/pass.
		If netrc is true, try this. Else, try user/pass if supplied.
		If neither is available, raise error

		:param netrc_path: The path to Netrc 
		:type netrc_path: ``string_type_or_none``

		:param username: The user for authenticating with the CAS end-point
		:type username: ``string_type_or_none``

		:param password: The password for authenticating with the CAS end-point
		:type password: ``string_type_or_none``
		"""

		self.server = server_url 

		if netrc_path:
			parent_auth = NetRCAuth(rest_client=self.rest_client)
			parent_auth.login(netrc_path=netrc_path)
		elif username and password:
			parent_auth = UserPassAuth(rest_client=self.rest_client)
			parent_auth.login(username=username, password=password)
		else:
			raise BCSRestLoginError('not enough data is provided to login')
		self.username = parent_auth.username
		self.password = parent_auth.password
			
		try:
			self.generate_tgt(overwrite=True)
		except BCSRestLoginError as e:
			raise 
		else:
			self.is_logged_in = True

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
		#if (ro.status_code != requests.codes.get("ok")):  # why not just ro.ok?
		if ro.ok:
			self.get_tgt_and_write()
			tgt_url = self.read_tgt()
			ro = requests.post(url=tgt_url, data=body, verify=self.verify_ssl)
			if (ro.status_code != requests.codes.get("ok")):
				raise RuntimeError("Cannot authenticate against CAS using provided 'username' and 'password'. HTTP status code: '{status}'".format(status=ro.status_code))
		return(ro.text)

	def get_tgt_and_write(self):
		""" Retrieves the ticket getting ticket that will ultimately be used inside the request to the CAS
		    end-point for retrieving a service ticket.
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
		if ro.status_code == 401:
			raise BCSRestLoginError('could not login using provided uername and password')
		elif ((ro.status_code < 200) or (ro.status_code >= 300)):
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
# ==========================================================================================
# ==========================================================================================
class AuthConfig(object):
	'''
	Configuration and validation for custom authentication schemas
	'''
	pass


# ==========================================================================================	
class NoAuthConfig(AuthConfig):
	'''
	Configuration and validation for custom authentication schemas
	'''

	authentication_modules = NoAuth



# ==========================================================================================	
class UserPassAuthConfig(AuthConfig):
	'''
	Allow authentication via NetRC or User/Password
	'''

	authentication_module = UserPassAuth

	def __init__(self, verify_ssl=False):
		self.verify_ssl = verify_ssl


# ==========================================================================================	
class NetrcOrUserPassAuthConfig(AuthConfig):
	'''
	Allow authentication via NetRC or User/Password
	'''

	authentication_module = UserPassOrNetRCAuth

	def __init__(self, verify_ssl=False):
		self.verify_ssl = verify_ssl



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

