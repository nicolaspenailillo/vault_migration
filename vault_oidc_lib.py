import webbrowser
import http.server
import hvac
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

# CHANGEME: these params might have to be changed to match your Vault configuration.
# Specifically
# 1. auth/oidc/role/XXX allowed_redirect_uris must contain the
#    OIDC_REDIRECT_URI string used below.
# 2. Role must match your environment's role for this client.
OIDC_CALLBACK_PORT = 8250
OIDC_REDIRECT_URI = f'http://localhost:{OIDC_CALLBACK_PORT}/oidc/callback'
ROLE = '' # Use None (not empty string) for the default Role
SELF_CLOSING_PAGE = '''
<!doctype html>
<html>
<head>
<script>
// Closes IE, Edge, Chrome, Brave
window.onload = function load() {
  window.open('', '_self', '');
  window.close();
};
</script>
</head>
<body>
  <p>Authentication successful, you can close the browser now.</p>
  <script>
    // Needed for Firefox security
    setTimeout(function() {
          window.close()
    }, 5000);
  </script>
</body>
</html>
'''

class VaultOIDCHandler:
    def __init__(self, vault_url, role='', callback_port=OIDC_CALLBACK_PORT):
        self.vault_url = vault_url
        self.role = role
        self.callback_port = callback_port
        self.redirect_uri = f'http://localhost:{callback_port}/oidc/callback'
        self.client = hvac.Client(url=vault_url)
        self.token = None
        self.client.secrets.kv.default_kv_version = 2

    
    def authenticate(self):
        auth_url_response = self.client.auth.oidc.oidc_authorization_url_request(
            role=self.role,
            redirect_uri=self.redirect_uri,
        )
        auth_url = auth_url_response['data']['auth_url']
        if auth_url == '':
            raise ValueError('OIDC auth_url is empty.')

        params = urllib.parse.parse_qs(auth_url.split('?')[1])
        auth_url_nonce = params['nonce'][0]
        auth_url_state = params['state'][0]

        webbrowser.open(auth_url)
        self.token = self._login_oidc_get_token(auth_url_nonce, auth_url_state)

        auth_result = self.client.auth.oidc.oidc_callback(
            code=self.token,
            path='oidc',
            nonce=auth_url_nonce,
            state=auth_url_state,
        )
        new_token = auth_result['auth']['client_token']
        print(f'Client token returned: {new_token}')

        # If you want to continue using the client here
        # update the client to use the new token
        self.client.token = new_token
    
    def _login_oidc_get_token(self, nonce, state):
        class AuthHandler(BaseHTTPRequestHandler):
            token = ''

            def do_GET(self):
                params = urllib.parse.parse_qs(self.path.split('?')[1])
                self.server.token = params['code'][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str.encode(SELF_CLOSING_PAGE))

        server_address = ('', self.callback_port)
        httpd = HTTPServer(server_address, AuthHandler)
        httpd.handle_request()
        return httpd.token

# migrate all keys on engine
def migrate_engine(client_old, client_new , engine, new_path_prefix=None, new_engine_name=None):
    keys_list = []
    def process_metadata(metadata,prefix=""):
        for data in metadata["data"]["keys"]:
            if '/' in data:
                prefix_next= prefix + data
                keys_on_data = client_old.adapter.request("GET", f"v1/{engine}/metadata/{prefix_next}/?list=1")
                process_metadata(keys_on_data,prefix_next)
            else:
                path = prefix+data
                try:
                    value = client_old.secrets.kv.v2.read_secret_version(
                        mount_point=engine, path=path)
                    new_engine = engine

                    if new_engine_name != None:
                        new_engine = new_engine_name
                    output_path = path

                    if new_path_prefix != None:
                        output_path = new_path_prefix + path

                    client_new.secrets.kv.v2.create_or_update_secret(
                        mount_point=new_engine,
                        path=output_path,
                        secret=value["data"]["data"],
                    )
                    # THIS IS FOR DELETE MIGRATED KEYS ON NEW. TESTING ONLY
                    # client_new.secrets.kv.v2.delete_metadata_and_all_versions(
                    #     mount_point=new_engine,
                    #     path=output_path,
                    # )
                    keys_list.append(output_path)
                except hvac.exceptions.InvalidPath:
                    print(path, "not valid, continuing with next")
                except Exception as e:
                    print(f"Caught an exception: {e}")
                    sys.exit(1)
                    
    engine_data = client_old.adapter.request("GET", f"v1/{engine}/metadata/?list=1")
    process_metadata(engine_data)
    return keys_list

if __name__ == '__main__':
    # Example of using the library
    vault_client = VaultOIDCHandler('https://vault_url.com', role='')
    vault_client.authenticate()
    if vault_client.token:
        # Do something
        pass
