'''
This module handle authentication against a variety of REST services
'''


import logging
import os
import threading
from netrc import netrc
from uritools import urisplit
import requests

from rest_client.exception import RestLoginError, RestClientConfigurationError


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
        '''
        returns a username/password tuple to use in basic authentication
        '''
        return (self.username, self.password)

    @staticmethod
    def is_valid_credential(credential):
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
                raise RestLoginError('provided password but not a username')
            else:
                return False

    # -------------------------------------------------------------------------------
    def login(self):
        '''
        placeholder to enforce subclasses to customize the login method
        '''
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

        self.netrc_path = os.path.expanduser(netrc_path)

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

        if username and password:
            parent_auth = UserPassAuth(rest_client=self.rest_client)
            parent_auth.login(username=username, password=password)
        elif netrc_path:
            parent_auth = NetRCAuth(rest_client=self.rest_client, auth_config_object=self.auth_config_object)
            parent_auth.login(netrc_path=netrc_path)
        else:
            raise RestLoginError('not enough data is provided to login')
        self.username = parent_auth.username
        self.password = parent_auth.password

        self.is_logged_in = True


# ==========================================================================================

class CASAuth(RESTAuthentication):
    '''
    Subclass of the RESTAuthentication that is able to use CAS to request and store
    a ticket-granting-ticket and subsequent service tickets.
    '''

    # -------------------------------------------------------------------------------------
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
        self.verify_ssl = False
        config = auth_config_object
        self.ticket_path = '/'.join(config.path)
        self.service = config.service_name
        self.tgt_volatile_storage = False 


        # Keep state in per-thread local storage
        self._thread_local = threading.local()


    # -------------------------------------------------------------------------------------
    def init_per_thread_state(self):
        """ Initializes a state per thread used.
        """
        # Ensure state is initialized just once per-thread
        if not hasattr(self._thread_local, 'init'):
            self._thread_local.init = True
            self._thread_local.renew_ticket = False

    # -------------------------------------------------------------------------------------    
    def login(self, server_url,  verify_ssl=False, 
              netrc_path=os.path.expanduser("~/.netrc"),
              username=None, password=None, 
              tgt_volatile_storage=False,
              granting_ticket_filepath=None,
              ticket_granting_ticket=None
              ):
        """
        CAS-auth requires a secondary auth, so it has two authentication levels...
        Allow logins via either netRC or user/pass.
        If netrc is true, try this. Else, try user/pass if supplied.
        If neither is available, raise error


        :param server_url: the URL of the CAS server
        :type server_url: ``string_type``

        :param verify_ssl: Whether the CAS client should verify SSL certificates upon making requests
        :type verify_ssl: ``bool``

        :param netrc_path: The path to Netrc
        :type netrc_path: ``string_type_or_none``

        :param username: The user for authenticating with the CAS end-point
        :type username: ``string_type_or_none``

        :param password: The password for authenticating with the CAS end-point
        :type password: ``string_type_or_none``

        :param granting_ticket_filepath: The local path where a "ticket getting ticket" will be saved
        :type granting_ticket_filepath: ``string_type``

        :param tgt_volatile_storage: Is the TGT stored on the filesystem or handed over to the user
        :type tgt_volatile_storage: ``boolean``
        """

        # the connection parameters
        self.server = server_url
        self.verify_ssl = verify_ssl

        # TGT in file or attribute
        self.tgt_volatile_storage = tgt_volatile_storage
        if tgt_volatile_storage:
            if not ticket_granting_ticket:
                raise RestClientConfigurationError('ticket_granting_ticket must be set if volatile_storage is True')
            self.__ticket_granting_ticket = ticket_granting_ticket
        else:
            if not granting_ticket_filepath:
                raise RestClientConfigurationError('TGT path must be set if volatile_storage is False')
            self.tgt_path = os.path.expanduser(granting_ticket_filepath)
            
            
        parent_auth = UserPassOrNetRCAuth(rest_client=self.rest_client)
        parent_auth.login(netrc_path=netrc_path, username=username, password=password)
        self.username = parent_auth.username
        self.password = parent_auth.password

        try:
            # be aware that if the olf TGT is valid, the validity of the username/pass is not tested until this expires!
            test_ticket = self.get_service_ticket()
        except RestLoginError as e:
            raise
        else:
            self.is_logged_in = True

    # -------------------------------------------------------------------------------------    
    def get_service_ticket(self):
        """ Retrieves the service ticket that will ultimately be used inside the request to the REST end-point.

            :return: The text or token to be used inside the Authorization header of the RESTful request
            :rtype: ``string_type``
        """
        body = {"service": self.service}
        response = requests.post(url=self.ticket_granting_ticket, data=body, verify=self.verify_ssl)
        if not response.ok:
            self.ticket_granting_ticket = self.request_new_tgt()
            response = requests.post(url=self.ticket_granting_ticket, data=body, verify=self.verify_ssl)
            if not response.ok:
                raise RuntimeError("Cannot authenticate against CAS using provided 'username' and 'password'. HTTP status code: '{status}'".format(status=response.status_code))
        return response.text


    # -------------------------------------------------------------------------------------
    @property
    def ticket_granting_ticket(self):
        """
        Reads the ticket getting ticket that will ultimately be used inside
        the request to the CAS end-point for retrieving a service ticket.
        The "tgtPath" parameter has to point to an existing location.

        :return: The URL to be used for retrieving a service ticket from the CAS end-point
        :rtype: ``string_type``
        """
        if self.tgt_volatile_storage:
            if not self.__ticket_granting_ticket:
                self.__ticket_granting_ticket = self.request_new_tgt()
            return self.__ticket_granting_ticket
        else:
            if not os.path.isfile(self.tgt_path):
                self._thread_local.renew_ticket = False
                raise RuntimeError("[CAS] File '{tgt_path}' does not exist.".format(tgt_path=self.tgt_path))
            else:
                with open(self.tgt_path, 'r') as tgt_file:
                    tgt = tgt_file.read().strip()
                logging.debug("[CAS] TGT contents are '%s'", tgt)  # printing credentials here!
                if tgt == "":
                    os.remove(self.tgt_path)
                    raise ValueError("[CAS] TGT file at '%s' was empty and has been removed."% self.tgt_path)
                else:
                    return tgt

    # -------------------------------------------------------------------------------------
    @ticket_granting_ticket.setter
    def ticket_granting_ticket(self, tgt):
        '''
        depending on method, store TGT in file or within class instance
        '''
        
        if self.tgt_volatile_storage:
            self.__ticket_granting_ticket = tgt
        else:
            logging.debug("[CAS] TGT URI is '%'", tgt)
            tgt_dir = os.path.dirname(self.tgt_path)
            if not os.path.isdir(tgt_dir):
                os.makedirs(tgt_dir)
            if os.path.isfile(self.tgt_path):
                os.remove(self.tgt_path)
            with open(self.tgt_path, "w") as tgt_file:
                tgt_file.write(tgt)


    # -------------------------------------------------------------------------------------    
    def request_new_tgt(self):
        """ Retrieves the ticket getting ticket that will ultimately be used inside the request to the CAS
            end-point for retrieving a service ticket.
            If the "tgtPath" parameter isn't pointing to an existing location, that location will be created.
            If the file at "tgtPath" exists, it will be replaced by the newly retrieved TGT.
        """
        
        ticket_url = "{server}/{path}".format(server=self.server, path=self.ticket_path)

        response = requests.post(url=ticket_url,
                                         data={"username": self.username, "password": self.password},
                                         verify=self.verify_ssl)
        if response.status_code == 401:
            raise RestLoginError('could not login using provided uername and password')
        elif (response.status_code < 200) or (response.status_code >= 300):
            raise RuntimeError("Cannot authenticate against CAS using provided 'username' and 'password'. HTTP status code: '{status}'".format(status=response.status_code))

        tgt = response.headers["location"]
        return tgt

    # -------------------------------------------------------------------------------------    
    def __call__(self, r):
        """ Is called when authentication is needed before issuing a RESTful request.
            Will retrieve and create a new TGT file if necessary.
            Will retrieve a new service ticket or token if necessary.
            Adds the Authorization header and supplies the correct service ticket or token to it.
        """
        # Initialize per-thread state, if needed
        self.init_per_thread_state()
        renew_ticket = self._thread_local.renew_ticket
        logging.debug("[CAS] Renewing service ticket")
        service_ticket = self.get_service_ticket()
        r.headers['Authorization'] = "CAS {service_ticket}".format(service_ticket=service_ticket)
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

    authentication_module = NoAuth


# ==========================================================================================
class UserPassAuthConfig(AuthConfig):
    '''
    Allow authentication via NetRC or User/Password
    '''

    authentication_module = UserPassAuth


# ==========================================================================================
class NetrcOrUserPassAuthConfig(AuthConfig):
    '''
    Allow authentication via NetRC or User/Password
    '''

    authentication_module = UserPassOrNetRCAuth


# ==========================================================================================
class CasAuthConfig(AuthConfig):
    '''
    CAS authentication specific for the CLS implementation below
    '''

    authentication_module = CASAuth

    # -------------------------------------------------------------------------------------
    def __init__(self, path, service_name):
        '''
        :param path: The absolute path for the ticket granting tickets
        :type path: ``list``

        :param service: The service name used to authenticate with the CAS end-point
        :type service: ``string_type``
        
        '''

        self.path = path
        self.service_name = service_name
