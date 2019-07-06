"""
This file contains the base API client object, implemented as a wrapper around
urllib3.
"""
import os.path
import logging
import json
import time
import certifi
import urllib3
from . import exceptions

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


class FutrliClient(object):
    """
    Represent a client, which can be used to authenticate against the Futrli
    web API and perform various tasks. This class wraps urllib3 functionality
    as thinly as possible to ensure that subclasses and third-party tools can
    add custom functionality without a lot of extra work.
    """
    BASE_URL = 'https://api.prod.futrlidev.com/'
    ENCODING = 'utf8'
    KEEP_ALIVE = True
    USER_AGENT = 'py-futrli 0.1a'

    def __init__(self, **kwargs):
        """
        kwargs:
        - email (required)
        - password (required)
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self._email = kwargs.get('email')
        self._pass = kwargs.get('password')
        self.__connection_pool = None
        self._auth_token = None

    def authenticate(self, **urlopen_kw):
        "Perform authentication against the API"
        urlopen_kw['body'] = json.dumps(
            {'email': self._email, 'password': self._pass})
        urlopen_kw['headers'] = urlopen_kw.get('headers', {})
        urlopen_kw['headers']['Content-Type'] = 'application/json'
        resp = self._request(
            'POST', '/login/', **urlopen_kw)
        self._auth_token = resp['token']
        return resp

    def get_org_list(self, **urlopen_kw):
        """Returns a list of organizations and various attributes as
        dictionary values"""
        endpoint = '/organisations/list/'
        return self._request('GET', endpoint, **urlopen_kw)['organisations']

    def upload_financial_data(
            self, filename, org_id, action='REPLACE', **urlopen_kw):
        """Upload financial data to the organization identified by org_id.
        Data will be encoded by this method, pass CSV data directly.
        `filename` parameter refers to a full path to a file to upload as
        financial data to futrli. This name is uploaded to Futrli as part of
        the PUT request.

        `action` refers to what to do when the data being uploaded corresponds
        to the same date, parent, and child as existing data. Valid options
        include:

        - ADD: add new entries to the existing ones, duplicating if necessary
        - REPLACE: replace the old entries with new ones (the default)
        - IGNORE: ignore duplicates in the new upload data (drop them)
        """
        with open(filename) as fhndl:
            data = fhndl.read()
        urlopen_kw['body'] = data
        params = {'organisation_id': org_id}
        urlopen_kw['headers'] = urlopen_kw.get('headers', {})
        urlopen_kw['headers']['Content-Type'] = 'text/csv'
        # Test the data
        endpoint = '/csv/non-financial-data/?' + urlencode(params)
        resp = self._request(
            'PUT', endpoint, **urlopen_kw)
        self.log.debug(
            'will add %d new records and found %d existing matches',
            len(resp['new_accounts']), len(resp['existing_accounts']))
        # Now actually accept the upload
        params['name'] = os.path.basename(filename)
        params['action'] = action
        endpoint = '/csv/non-financial-data/accept/?' + urlencode(params)
        return self._request(
            'PUT', endpoint, **urlopen_kw)

    @property
    def _connection_pool(self):
        """
        Returns an initialized connection pool. If the pool becomes broken
        in some way, it can be destroyed with :meth:`_destroy_pool` and a
        subsequent call to this attribute will initialize a new pool.
        """
        if self.__connection_pool is None:
            self._create_pool()
        return self.__connection_pool

    def _request(self, method, path, **urlopen_kw):
        """
        Wrapper around the ConnectionPool request method to add rate limiting
        and response handling.

        HTTP GET parameters should be passed as 'fields', and will be properly
        encoded by urllib3 and correctly placed into the request uri. For
        POST and PUT operations, the ``body`` kwarg should be supplied and
        already in encoded form (that's generally done by one of the methods
        above.)

        Any headers passed as kwargs will be merged with underlying ones that
        are required to make the API function properly, with the headers
        passed here overriding built-ins (such as to override the user_agent
        for a particular request).
        """
        if self._auth_token:
            # set up the authorization header, but allow for manual override
            urlopen_kw['headers'] = urlopen_kw.get('headers', {})
            urlopen_kw['headers']['Authorization'] = urlopen_kw['headers'].get(
                'Authorization', "Token {}".format(self._auth_token))
        try:
            self.rate_limit_lock.acquire()
        except AttributeError:
            pass
        response = self._connection_pool.request(
            method.upper(), path, **urlopen_kw)
        return self._handle_response(response)

    def _destroy_pool(self):
        """
        Tear down the existing HTTP(S)ConnectionPool such that a subsequent
        call to :attr:`_connection_pool` generates a new pool to work with.
        Useful in cases where authentication timeouts occur.
        """
        self.__connection_pool = None

    def _create_pool(self):
        """Use the handy urllib3 connection_from_url helper to create a
        pool of the correct type for HTTP/HTTPS.
        This also seeds the pool with the base URL so that subsequent requests
        only use the URI portion rather than an absolute URL.

        Stores a reference to the pool for use with :attr:`_connection_pool`
        """
        headers = urllib3.util.make_headers(
            keep_alive=self.KEEP_ALIVE,
            user_agent=self.USER_AGENT)
        self.__connection_pool = urllib3.connectionpool.connection_from_url(
            self.BASE_URL, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),
            headers=headers)

    def _handle_response(self, response):
        """
        In the case of a normal response, deserializes the response from
        JSON back into dictionary form and returns it. In case of a response
        code of 300 or higher, raises an :class:`exceptions.APIError`
        exception.
        Note that if you are seeing weirdness in the API response data, look
        at the :attr:`ENCODING` attribute for this class.
        """
        if response.status > 299:
            raise exceptions.APIError(response.status, response=response)
        return json.loads(response.data.decode(self.ENCODING))
