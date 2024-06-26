import json
import urllib.parse  # use parse for Python 3
import requests
import logging
import model.util
from datetime import datetime, timedelta
from credentialutil import get_credentials
from model.model import oAuth_token

LOGFILE = 'eBay_Oauth_log.txt'
logging.basicConfig(level=logging.DEBUG, filename=LOGFILE, format="%(asctime)s: %(levelname)s - %(funcName)s: %(message)s", filemode='w')

class oauth2api(object):

    def generate_user_authorization_url(self, env_type, scopes, state=None):
        '''
            env_type = environment.SANDBOX or environment.PRODUCTION
            scopes = list of strings
        '''
        credential = get_credentials(env_type)
        scopes = ' '.join(scopes)
        param = {
            'client_id': credential.client_id,
            'redirect_uri': credential.ru_name,
            'response_type': 'code',
            'prompt': 'login',
            'scope': scopes
        }
        
        if state is not None:
            param.update({'state': state})
        
        query = urllib.parse.urlencode(param)  # updated for Python 3
        return env_type.web_endpoint + '?' + query

    def get_application_token(self, env_type, scopes):
        """
        Makes call for application token and stores result in credential object
        Returns credential object
        """
        logging.info("Trying to get a new application access token ...")
        credential = get_credentials(env_type)
        headers = model.util._generate_request_headers(credential)
        body = model.util._generate_application_request_body(credential, ' '.join(scopes))
        
        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = oAuth_token()
    
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            # Set token expiration time 5 minutes before actual expire time
            token.token_expiry = datetime.utcnow() + timedelta(seconds=int(content['expires_in'])) - timedelta(minutes=5)
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token

    def exchange_code_for_access_token(self, env_type, code):
        logging.info("Trying to get a new user access token ...")
        credential = get_credentials(env_type)
    
        headers = model.util._generate_request_headers(credential)
        body = model.util._generate_oauth_request_body(credential, code)
        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)
            
        content = json.loads(resp.content)
        token = oAuth_token()
        
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = datetime.utcnow() + timedelta(seconds=int(content['expires_in'])) - timedelta(minutes=5)
            token.refresh_token = content['refresh_token']
            token.refresh_token_expiry = datetime.utcnow() + timedelta(seconds=int(content['refresh_token_expires_in'])) - timedelta(minutes=5)
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token

    def get_access_token(self, env_type, refresh_token, scopes):
        """
        Refresh token call
        """
        
        logging.info("Trying to get a new user access token ...")
        credential = get_credentials(env_type)
    
        headers = model.util._generate_request_headers(credential)
        body = model.util._generate_refresh_request_body(' '.join(scopes), refresh_token)
        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = oAuth_token()
        token.token_response = content
    
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = datetime.utcnow() + timedelta(seconds=int(content['expires_in'])) - timedelta(minutes=5)
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token