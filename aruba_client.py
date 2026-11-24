import os
import httpx
import base64
import hashlib
import hmac
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

class ArubaInstantOnClient:
    def __init__(self):
        self.base_url = "https://sso.arubainstanton.com"
        self.client_id = None
        self.access_token = None
        self.session = httpx.Client(timeout=30.0)

    def get_urlecode(self, bytes_data):
        encoded_text = base64.urlsafe_b64encode(bytes_data).rstrip(b'=').decode('utf-8')
        encoded_text = encoded_text.replace('+', '-').replace('/', '_')
        return encoded_text

    def generate_pkce(self):
        random_number_generator = os.urandom(32)
        code_verifier = self.get_urlecode(random_number_generator).rstrip('=')
        code_challenge = self.get_urlecode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip('=')
        return code_verifier, code_challenge

    def authenticate(self):
        username = os.getenv('ARUBA_USERNAME')
        password = os.getenv('ARUBA_PASSWORD')

        if not username or not password:
            raise ValueError("ARUBA_USERNAME and ARUBA_PASSWORD environment variables must be set")

        login_request = {
            'username': username,
            'password': password
        }

        content_type = 'application/x-www-form-urlencoded'
        response = self.session.post(f"{self.base_url}/aio/api/v1/mfa/validate/full", data=login_request, headers={'Content-Type': content_type})
        response.raise_for_status()

        token = response.json()
        self.access_token = token['access_token']

        oauth_settings_response = self.session.get("https://portal.instant-on.hpe.com/settings.json")
        oauth_settings_response.raise_for_status()

        oauth_settings = oauth_settings_response.json()
        self.client_id = oauth_settings['ssoClientIdAuthZ']

        state_random_number_generator = os.urandom(32)
        state = self.get_urlecode(state_random_number_generator).rstrip('=')

        code_verifier, code_challenge = self.generate_pkce()

        auth_url = f"{self.base_url}/as/authorization.oauth2?client_id={self.client_id}&redirect_uri=https://portal.arubainstanton.com&response_type=code&scope=profile%20openid&state={state}&code_challenge_method=S256&code_challenge={code_challenge}&sessionToken={self.access_token}"
        response = self.session.get(auth_url, follow_redirects=True)
        response.raise_for_status()

        redirect_uri = response.url
        query_params = parse_qs(urlparse(str(redirect_uri)).query)
        login_code = query_params['code'][0]

        token_auth = {
            'client_id': self.client_id,
            'redirect_uri': 'https://portal.arubainstanton.com',
            'code': login_code,
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code'
        }

        token_response = self.session.post(f"{self.base_url}/as/token.oauth2", data=token_auth, headers={'Content-Type': content_type})
        token_response.raise_for_status()

        token = token_response.json()
        self.access_token = token['access_token']
      

    def get_access_token(self):
        if not self.access_token:
            self.authenticate()
        return self.access_token

    def list_sites(self):
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "x-ion-api-version": "7"
        }

        response = self.session.get(
            "https://nb.portal.arubainstanton.com/api/sites/",
            headers=headers
        )
        response.raise_for_status()

        return response.json()["elements"]

    def resolve_site_id(self, site_identifier: str):
        sites = self.list_sites()
        exact_matches = [site for site in sites if site['id'] == site_identifier]
        if exact_matches:
            return exact_matches[0]['id']

        case_insensitive_matches = [site for site in sites if site['name'].strip().lower() == site_identifier.strip().lower()]
        if case_insensitive_matches:
            if len(case_insensitive_matches) > 1:
                raise ValueError(f"Multiple sites match the name '{site_identifier}': {', '.join(site['name'] for site in case_insensitive_matches)}")
            return case_insensitive_matches[0]['id']

        partial_matches = [site for site in sites if site['name'].strip().lower().startswith(site_identifier.strip().lower())]
        if partial_matches:
            if len(partial_matches) > 1:
                raise ValueError(f"Multiple sites match the name '{site_identifier}': {', '.join(site['name'] for site in partial_matches)}")
            return partial_matches[0]['id']

        raise ValueError(f"No site found with identifier '{site_identifier}'")

    def get_site_details(self, site_identifier: str):
        site_id = self.resolve_site_id(site_identifier)
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "x-ion-api-version": "7"
        }

        response = self.session.get(
            f"https://nb.portal.arubainstanton.com/api/sites/{site_id}",
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    def list_devices(self, site_identifier: str):
        site_id = self.resolve_site_id(site_identifier)
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "x-ion-api-version": "7"
        }

        response = self.session.get(
            f"https://nb.portal.arubainstanton.com/api/sites/{site_id}/inventory",
            headers=headers
        )
        response.raise_for_status()

        return response.json()["elements"]

    def list_clients(self, site_identifier: str):
        site_id = self.resolve_site_id(site_identifier)
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "x-ion-api-version": "7"
        }

        response = self.session.get(
            f"https://nb.portal.arubainstanton.com/api/sites/{site_id}/clientSummary",
            headers=headers
        )
        response.raise_for_status()

        return response.json()
