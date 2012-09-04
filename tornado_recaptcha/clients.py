import json
import logging
import urllib

from tornado import gen, httpclient, httpserver

logger = logging.getLogger(__name__)
ENDPOINT = 'http://www.google.com/recaptcha/api/verify'


class RecaptchaClient(object):

    """
    Handle checking captcha challenges and responses. 
    
    """

    def __init__(self, private_key, *args, **kwargs):
        assert private_key is not None, "private_key cannot be None"
        assert private_key is not '', "private_key cannot be an empty string"

        self.private_key = private_key

    @gen.engine
    def check_challenge(self, request, callback):
        """
        Check a recaptcha challenge

        """
        extract_status, params = self._extract_params_from_request(request)
        if extract_status is False:
            logger.warn('Failed to extract params')
            callback(False)
            return

        # add private key to params 
        params['privatekey'] = self.private_key
            
        request = httpclient.HTTPRequest(ENDPOINT, method='POST',
                body=urllib.urlencode(params))
        client = httpclient.AsyncHTTPClient()
        response = yield gen.Task(client.fetch, request)
        success, msg = self._parse_response(response)
        callback(success)

    def _extract_params_from_request(self, request):
        """
        Pull needed params from a rquest body.

        :param HTTPRequest request: Instance of
            `:py:tornado.httpclient.HTTPRequest` whose body contains the
            recaptcha params.
        :rtype: tuple of format (bool, dict). `bool` indicates whether or
            not the params were successfully extracted. `dict` will contain
            the params when `bool` is `True`.
        """
        if not isinstance(request, httpserver.HTTPRequest):
            logger.warn('Called without a proper HTTPRequest')
            return (False, {})

        request_data = json.loads(request.body)

        if 'recaptcha' not in request_data.keys():
            logger.warn('No recaptcha data found in request')
            return (False, {})

        desired_keys = ['challenge', 'response']
        recaptcha_data = request_data['recaptcha']
        params = {}
        for key in desired_keys:
            try:
                params[key] = recaptcha_data[key]
            except KeyError:
                logger.warn('%s not found in reCaptcha data', key)
                return (False, {})

        # add remote ip to params
        params['remoteip'] = request.remote_ip
        return (True, params)

    def _parse_response(self, response):
        """
        Parse success and error msg from response

        :param HTTPResponse response: Instance of
            `:py:torando.httpclient.HTTPResponse'.
        :rtype: tuple of format (bool, string). `bool` indicates whether or
            not the challange was successfully answered. `string` represents
            the error state returned. If change is successful `string` will
            be an empty string ('')
        """
        if not isinstance(response, httpclient.HTTPResponse):
            logger.warn('Called without proper HTTPResponse')
            return (False, '')

        if response.code != 200:
            logger.warn('Called with a non-200 response')
            return (False, '')

        if response.body.find('true') != -1:
            logger.debug('Successful challenge.')
            return (True, '')

        parts = response.body.splitlines()
        logger.warn('Failed challenge. ReCaptcha says: \"%s\"', parts[-1])
        return (False, parts[-1])
