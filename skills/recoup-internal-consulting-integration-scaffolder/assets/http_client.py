"""Read-only HTTPS JSON client template. Configure per provider; Python standard library only."""
import json
import os
import ssl
import time
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A provider-specific adapter may allow same-origin redirects explicitly.
        return None


class ReadOnlyClient:
    def __init__(self, base_url, key_env, *, token=None):
        parts = urlsplit(base_url)
        if parts.scheme != 'https' or not parts.netloc or parts.username or parts.password:
            raise ValueError('Use a credential-free HTTPS provider base URL')
        self.base_url = base_url.rstrip('/') + '/'
        self.origin = (parts.scheme, parts.netloc)
        self.token = token or os.environ.get(key_env)
        if not self.token:
            raise ValueError(f'Configure {key_env} through the selected account/environment')
        self.opener = build_opener(NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))

    def get(self, path):
        url = urljoin(self.base_url, path)
        parts = urlsplit(url)
        if (parts.scheme, parts.netloc) != self.origin:
            raise ValueError('Request must stay on the configured provider origin')
        request = Request(url, headers={'Authorization': f'Bearer {self.token}', 'Accept': 'application/json'})
        for attempt in range(3):
            try:
                with self.opener.open(request, timeout=30) as response:
                    return json.load(response)
            except HTTPError as exc:
                if exc.code != 429 or attempt == 2:
                    raise RuntimeError(f'Provider read failed: HTTP {exc.code}') from None
                try: delay = min(30, max(1, int(exc.headers.get('Retry-After', '2'))))
                except ValueError: delay = 2
                time.sleep(delay)
