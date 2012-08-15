"""Compatibility layer for Python 3."""

import sys


PY3 = sys.version[0] == '3'

if PY3:  # pragma: no cover
    from configparser import SafeConfigParser
else:  # pragma: no cover
    from ConfigParser import SafeConfigParser  # pyflakes: ignore
if PY3:  # pragma: no cover
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
else:  # pragma: no cover
    from urllib import quote_plus  # pyflakes: ignore
    from urllib import unquote_plus  # pyflakes: ignore
