"""
    Version 0.1.0
    2011/05/18

    Copyright (C) Anupam Aiyappa 2010-2011
    webpurify.py
    Python interface to the Web Purify API
    E-mail info@phpscrap.com

    http://www.phpscrap.com/
    http://www.webpurify.com/documentation/methods/

    Dual licensed under the MIT and GPL licenses:
    http://www.opensource.org/licenses/mit-license.php
    http://www.gnu.org/licenses/gpl.html

    A python interface to the `Web Purify <http://webpurify.com>`_ API.
    This is profanity filter web service - which helps identify profanity
    and replace them with the necessary symbols.

    You will need an API key for this to work.

    Usage Example:

       from webpurify import *

       text = 'this really sucks'
       web_purifier = WebPurify('api_key_goes_here')
       web_purified_text = web_purifier.replace(text)

"""

import os, sys
import json
import httplib, urllib

class WebPurifyError(Exception):
    """Base class for all web purify exceptions."""

class WebPurify(object):
    """A class for working with the web purify API"""

    rest_api_url = 'api1.webpurify.com'
    controller = 'webpurify.live.'

    def __init__(self, api_key = ''):
        global WEB_PURIFY_API_KEY
        WEB_PURIFY_API_KEY = api_key

    def check(self, text = ''):
        """
        A profanity checking method. If profanity is found it returns 1.
        If the text is clean 0 (zero) is returned.

        """
        params = {'text' : text}
        response = self.get_json_response(self.generate_params(params, check))
        return {'found' : int(response['rsp']['found'])}

    def checkcount(self, text = ''):
        """
        A profanity checking method. Returns the number of profane words found
        in the submitted text. If the text is clean 0 (zero) is returned.

        """
        params = {'text' : text}
        response = self.get_json_response(self.generate_params(params, 'checkcount'))
        return {'found' : int(response['rsp']['found'])}


    def replace(self, text = '', replace_symbol= '*'):
        """
        This method accepts text and uses the "replace" API call
        which replaces all profanities with character and returns
        total number of profanities found.

        """
        params = {'text' : text, 'replacesymbol' : replace_symbol}
        response = self.get_json_response(self.generate_params(params, 'replace'))
        return {'text' : str(response['rsp']['text']), 'found' : int(response['rsp']['found'])}

    def webpurify_return(self, text = ''):
        """
        A profanity search method. Returns the number of profane words found and
        a list of the profane words. If the text is clean 0 (zero) is returned.

        """
        params = {'text' : text}
        response = self.get_json_response(self.generate_params(params, 'return'))
        if (int(response['rsp']['found']) == 0):
            return {'found' : int(response['rsp']['found'])}
        else:
            return {'expletive': response['rsp']['expletive'], 'found' : int(response['rsp']['found'])}

    def addtoblacklist(self, word = ''):
        """
        A profanity word management method. Adds submitted word to the blacklist
        of the associated license key. The words will be filtered along with
        words WebPurify filters by default.

        """
        return self.list_updates(word, 'addtoblacklist')

    def addtowhitelist(self, word = ''):
        """
        A profanity word management method. Adds submitted word to the whitelist
        of the associated license key

        """
        return self.list_updates(word, 'addtowhitelist')

    def removefromblacklist(self, word = ''):
        """
        A profanity word management method. Removes submitted word from the
        blacklist of the associated license key

        """
        return self.list_updates(word, 'removefromblacklist')

    def removefromwhitelist(self, word = ''):
        """
        A profanity word management method. Removes submitted word from the
        whitelist of the associated license key

        """
        return self.list_updates(word, 'removefromwhitelist')


    def list_updates(self, word, method):
        params = {'word' : word}
        response = self.get_json_response(self.generate_params(params, method))
        return {'success' : response['rsp']['success']}


    def getwhitelist(self):
        """
        A profanity word management method. Returns the custom whitelist of
        the associated license key

        """
        return self.get_list('getwhitelist')

    def getblacklist(self):
        """
        A profanity word management method. Returns the custom whitelist of the
        associated license key

        """
        return self.get_list('getblacklist')

    def get_list(self, method):
        """
        Returns empty list if no words found

        """

        params = {}
        response = self.get_json_response(self.generate_params(params, method))
        try:
            word_list = response['rsp']['word']
        except:
            word_list = ''

        return {'word' : word_list}


    def get_json_response(self, params):
        """
        This method accepts parameters and uses the method passed to make
        the API call which returns json response.

        """
        connection = httplib.HTTPConnection(self.rest_api_url)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        try:
            connection.request("POST", "/services/rest/", params, headers)
        except WebPurifyConnectionError:
            raise WebPurifyConnectionError
        #JSON decode the response from the API request
        response = json.loads(connection.getresponse().read())

        # Raises exception and returns Error Message
        if response['rsp']['@attributes']['stat'] != "ok":
            raise WebPurifyError(response['rsp']['err']['@attributes']['msg'])

        connection.close()
        return response


    def generate_params(self, params, method):
        """
        Append addtional pararmeters associated with the API calls.
        URLencode the parameters to be passed in the request

        """
        params['method'] = self.controller + method
        params['api_key'] = WEB_PURIFY_API_KEY
        params['format'] = 'json'

        return urllib.urlencode(params)
        