import json

from StringIO import StringIO
from unittest import TestCase

from tornado import httpclient, httpserver

import tornado_recaptcha


class TestRecaptchaClient(TestCase):

    """
    Test the recaptcha client

    """

    def test_extract_params_from_request_bad_request_param(self):
        """
        Can extract params correctly
        """
        client = RecaptchaClient()
        # test calling without an httpserver.HTTPRequest
        success, params = client._extract_params_from_request('request')
        self.assertFalse(success)
        self.assertEqual(params, {})

    def test_extract_params_from_request_no_recaptcha_data(self):
        """
        test calling with a request that does not have a recaptch key in
        """
        client = RecaptchaClient()
        request_data = {'some_key': 1}
        request = httpserver.HTTPRequest('POST', 'http://someurl.com',
                body=json.dumps(request_data))
        success, params = client._extract_params_from_request(request)
        self.assertFalse(success)
        self.assertEqual(params, {})

    def test_extract_params_from_request_missing_recaptcha_data(self):
        """
        test having a missing recaptcha params
        """
        client = RecaptchaClient()
        request_data = {
            'recaptcha': {
                'challenge': 'are you the gatekeeper?',
                'wrong_key': 'no'}}
        request = httpserver.HTTPRequest('POST', 'http://someurl.com',
            body=json.dumps(request_data))
        success, params = client._extract_params_from_request(request)
        self.assertFalse(success)
        self.assertEqual(params, {})

    def test_extract_params_from_request(self):
        """
        test successful extraction
        """
        client = RecaptchaClient()
        request_data = {
            'recaptcha': {
                'challenge': 'are you the gatekeeper?',
                'response': 'no'}}
        request = httpserver.HTTPRequest('POST', 'http://someurl.com',
            body=json.dumps(request_data), remote_ip='123.123.123.123')
        success, params = client._extract_params_from_request(request)
        self.assertTrue(success)
        expected_params = {
            'challenge': 'are you the gatekeeper?',
            'response': 'no',
            'remoteip': '123.123.123.123'}
        self.assertEqual(params, expected_params)

    def test_parse_response_bad_response_param(self):
        """
        Can parse response correctly
        """
        client = RecaptchaClient()
        success, msg = client._parse_response('response')
        self.assertFalse(success)
        self.assertEqual(msg, '')

    def test_parse_response_with_error_response(self):
        """
        test calling with an error response
        """

        client = RecaptchaClient()
        request = httpclient.HTTPRequest('http://someurl.com')
        response = httpclient.HTTPResponse(request, 404)
        success, msg = client._parse_response(response)
        self.assertFalse(success)
        self.assertEqual(msg, '')

    def test_parse_response_successful_challenge(self):
        """
        Can parse a successful challenge
        """
        client = RecaptchaClient()
        request = httpclient.HTTPRequest('http://someurl.com')
        response = httpclient.HTTPResponse(request, 200,
                buffer=StringIO('true\notherstuff'))
        success, msg = client._parse_response(response)
        self.assertTrue(success)
        self.assertEqual(msg, '')

    def test_parse_response_failure(self):
        """
        Can parse a failed challenge
        """
        client = RecaptchaClient()
        request = httpclient.HTTPRequest('http://someurl.com')
        response = httpclient.HTTPResponse(request, 200,
                buffer=StringIO('false\nincorrect-captcha-sol'))
        success, msg = client._parse_response(response)
        self.assertFalse(success)
        self.assertEqual(msg, 'incorrect-captcha-sol')

