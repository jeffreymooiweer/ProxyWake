import re
from urllib.parse import urlparse, urlunparse


def mask_secret(value, visible=4):
    if not value:
        return ''
    if len(value) <= visible * 2:
        return '*' * len(value)
    return f'{value[:visible]}…{value[-visible:]}'


def mask_url(url):
    if not url:
        return ''
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = parsed.hostname or ''
            if parsed.username:
                netloc = f'{parsed.username}:***@{netloc}'
            if parsed.port:
                netloc = f'{netloc}:{parsed.port}'
            parsed = parsed._replace(netloc=netloc)
            return urlunparse(parsed)
        if re.search(r'[?&](token|key|secret|auth)=', url, re.I):
            return re.sub(r'([?&](?:token|key|secret|auth)=)[^&]+', r'\1***', url, flags=re.I)
    except ValueError:
        pass
    return url
