#!/usr/bin/env python3
"""Video Studio device connection and credential-backed MCP stdio transport."""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

GATEWAY = 'https://video-studio-agent.life-efficient.chatgpt.site'
STUDIO = 'https://icaire-video-studio.life-efficient.chatgpt.site'
SERVICE = 'Video Studio Agent'
ACCOUNT = 'personal-connection'
MAX_BYTES = 12 * 1024 * 1024
TOKEN_PATTERN = re.compile(r'vst_[a-f0-9]{64}\Z')
SECURE_BACKENDS = {
    ('keyring.backends.Windows', 'WinVaultKeyring'),
    ('keyring.backends.macOS', 'Keyring'),
    ('keyring.backends.SecretService', 'Keyring'),
    ('keyring.backends.kwallet', 'DBusKeyring'),
    ('keyring.backends.kwallet', 'DBusKeyringKWallet4'),
    ('keyring.backends.kwallet', 'DBusKeyringKWallet5'),
    ('keyring.backends.libsecret', 'Keyring'),
}


class ConnectionError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Credentials:
    """Only an operating-system credential backend, never a file fallback."""
    def __init__(self):
        try:
            import keyring
            backend = keyring.get_keyring()
        except Exception:
            raise ConnectionError('Install keyring and enable your operating system credential store.') from None
        identity = (type(backend).__module__, type(backend).__name__)
        if identity not in SECURE_BACKENDS:
            raise ConnectionError('A supported OS credential store is required. File and fallback backends are disabled.')
        self.backend = backend

    def get(self):
        try:
            token = self.backend.get_password(SERVICE, ACCOUNT)
        except Exception:
            raise ConnectionError('The operating system credential store could not be unlocked.') from None
        if token is not None and (not isinstance(token, str) or not TOKEN_PATTERN.fullmatch(token)):
            raise ConnectionError('The saved connection is invalid. Reconnect Video Studio.')
        return token

    def save(self, token):
        if not isinstance(token, str) or not TOKEN_PATTERN.fullmatch(token):
            raise ConnectionError('Studio returned an invalid credential.')
        try:
            self.backend.set_password(SERVICE, ACCOUNT, token)
            if self.backend.get_password(SERVICE, ACCOUNT) != token:
                raise ValueError()
        except Exception:
            raise ConnectionError('The connection could not be saved in the operating system credential store.') from None

    def delete(self):
        if self.get() is None:
            return
        try:
            self.backend.delete_password(SERVICE, ACCOUNT)
        except Exception:
            raise ConnectionError('The saved credential could not be removed. Use your operating system credential manager.') from None


def post(path, payload, token=None):
    if path not in ('/agent', '/device/start', '/device/poll'):
        raise ConnectionError('Unsupported Studio endpoint.')
    body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    if len(body) > MAX_BYTES:
        raise ConnectionError('The request is too large.')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'VideoStudio-Agent/0.1.4'}
    if token is not None:
        if path != '/agent' or not TOKEN_PATTERN.fullmatch(token):
            raise ConnectionError('Invalid credential destination.')
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(GATEWAY + path, data=body, headers=headers, method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=125) as response:
            if response.status in (202, 204):
                return None
            if response.status not in ((200, 201) if path == '/device/start' else (200,)) or response.headers.get_content_type() != 'application/json':
                raise ConnectionError('Studio returned an unexpected response.')
            data = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as error:
        status = error.code
        error.close()
        if status in (401, 403):
            raise ConnectionError('Studio access was denied. Reconnect in the browser or ask the Studio owner to check access.') from None
        raise ConnectionError('Studio could not complete this request. Retry the connection.') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ConnectionError('Studio could not be reached. Check your connection and retry.') from None
    if len(data) > MAX_BYTES:
        raise ConnectionError('The Studio response is too large.')
    try:
        result = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        raise ConnectionError('Studio returned an invalid response.') from None
    if not isinstance(result, dict):
        raise ConnectionError('Studio returned an invalid response.')
    return result


def connect(credentials, request=post, open_browser=webbrowser.open, sleep=time.sleep, clock=time.monotonic, log=None):
    log = log or (lambda message: print(message, file=sys.stderr, flush=True))
    result = request('/device/start', {'label': 'Local agent'})
    try:
        device_code, user_code = result['deviceCode'], result['userCode']
        verification_uri = result['verificationUri']
        parsed = urllib.parse.urlsplit(verification_uri)
        if parsed.scheme != 'https' or parsed.netloc != urllib.parse.urlsplit(STUDIO).netloc or parsed.path != '/' or parsed.fragment:
            raise ValueError()
        if urllib.parse.parse_qs(parsed.query) != {'connect': [user_code]}:
            raise ValueError()
        if not isinstance(device_code, str) or not 32 <= len(device_code) <= 512 or not re.fullmatch(r'[A-Z0-9]{4}-[A-Z0-9]{4}', user_code):
            raise ValueError()
        expires = int(result['expiresIn'])
        interval = int(result.get('interval', 5))
        if not 1 <= expires <= 900 or not 1 <= interval <= 30:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ConnectionError('Studio returned an invalid approval request.') from None
    log('Approve Video Studio in your browser. Check that the displayed code is ' + user_code + '.')
    if not open_browser(verification_uri):
        log('Open this approval page: ' + verification_uri)
    deadline = clock() + expires
    while clock() < deadline:
        sleep(interval)
        if clock() >= deadline:
            break
        approval = request('/device/poll', {'deviceCode': device_code})
        if not isinstance(approval, dict):
            raise ConnectionError('Studio returned an unexpected approval response.')
        status = approval.get('status')
        if status in ('authorized', 'approved'):
            credentials.save(approval.get('token'))
            log('Video Studio connected. The credential is saved in your operating system credential store.')
            return
        if status in ('authorization_pending', 'pending'):
            continue
        if status == 'slow_down':
            interval = min(interval + 5, 60)
            continue
        if status in ('access_denied', 'denied'):
            raise ConnectionError('The connection request was declined.')
        if status in ('expired_token', 'expired', 'invalid_grant'):
            raise ConnectionError('The approval request expired or was already used. Start a new connection.')
        raise ConnectionError('Studio returned an unexpected approval status.')
    raise ConnectionError('The approval request expired. Start a new connection.')


def serve(credentials, input_stream=None, output_stream=None, request=post):
    input_stream = input_stream or sys.stdin.buffer
    output_stream = output_stream or sys.stdout
    while True:
        line = input_stream.readline(MAX_BYTES + 2)
        if not line:
            return
        request_id = None
        notification = False
        try:
            if len(line) > MAX_BYTES or not line.endswith(b'\n'):
                raise ConnectionError('The MCP request is too large or incomplete.')
            message = json.loads(line)
            if not isinstance(message, dict) or message.get('jsonrpc') != '2.0' or not isinstance(message.get('method'), str):
                raise ConnectionError('Invalid MCP request.')
            request_id = message.get('id')
            notification = 'id' not in message
            token = credentials.get()
            if not token:
                raise ConnectionError('Connect Video Studio in the browser before starting this MCP server.')
            result = request('/agent', message, token)
            if notification:
                continue
            if not isinstance(result, dict) or result.get('jsonrpc') != '2.0' or result.get('id') != request_id:
                raise ConnectionError('Studio returned an invalid MCP response.')
        except (ValueError, UnicodeDecodeError):
            result = {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32700, 'message': 'Invalid JSON request.'}}
        except ConnectionError as error:
            result = {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32001, 'message': str(error)}}
        if not notification:
            output_stream.write(json.dumps(result, separators=(',', ':')) + '\n')
            output_stream.flush()
        if len(line) > MAX_BYTES or not line.endswith(b'\n'):
            return


def main():
    parser = argparse.ArgumentParser(description='Connect Video Studio through browser approval and an OS credential store.')
    parser.add_argument('command', choices=('connect', 'status', 'disconnect', 'serve'))
    args = parser.parse_args()
    try:
        credentials = Credentials()
        if args.command == 'connect':
            connect(credentials)
        elif args.command == 'status':
            print('Connected credential available.' if credentials.get() else 'No saved connection.')
        elif args.command == 'disconnect':
            credentials.delete()
            print('Local credential removed. Revoke the connection in Studio to disable any other saved copy.')
        else:
            serve(credentials)
    except ConnectionError as error:
        print(str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Connection canceled.', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
