# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import urlparse

REGEX_ID = r'/[-0-9a-fA-F,_]*[-0-9,_]+[-0-9a-fA-F,_]*'


def normalize_url(url, regex=REGEX_ID):
    if regex is None:
        regex = REGEX_ID

    try:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        path = re.sub(regex, "/ID", path)
        path = path.rstrip("/")
    except TypeError:
        path = None

    return path