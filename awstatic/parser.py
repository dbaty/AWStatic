import codecs
from collections import defaultdict
import os


_special = object()

SECTIONS = {
    # A list of keys or '_special' if each line has a different
    # meaning (in which case we store all values of the line as a
    # list).
    'BROWSER': ('id', 'hits'),
    'DAY': ('yyyymmdd', 'pages', 'hits', 'bandwidth', 'visits'),
    'DOWNLOADS': ('url', 'hits', 'status_206', 'bandwidth'),
    'ERRORS': ('error', 'hits', 'bandwidth'),
    'GENERAL': _special,
    'KEYWORDS': ('keyword', 'searches'),
    'OS': ('id', 'hits'),
    'PAGEREFS': ('url', 'pages', 'hits'),
    'SEARCHWORDS': ('phrase', 'searches'),
    'SEREFERRALS': ('id', 'pages', 'hits'),
    'SIDER': ('url', 'pages', 'bandwidth', 'entry', 'exit'),
    'VISITOR': ('host', 'pages', 'hits', 'bandwidth'),
    }


class Parser(object):
    """A parser for AWStats report files.

    Data is stored in the ``data`` attribute as a dictionary. See
    'tests/test_parser.py' for the structure of this dictionary. The
    keys of this dictionary are:

    ``BROWSER``
        Keys are browser identifiers (e.g. "firefox4.0.1", or
        "opera9.80"), values are dictionaries with a ``hits`` key.

    ``DAY``
        Keys are the days of the month (as a string formatted as
        YYYYMMDD), values are dictionaries with the following keys:
        ``hits``, ``bandwidth``, ``pages`` and ``visits``.

    ``DOWNLOADS``
        The most downloaded files: keys are the relative URL, values
        are dictionaries with the following keys: ``hits`` and
        ``bandwidth``.

    ``ERRORS``
        Keys are the HTTP status code (e.g. "404"), values are
        dictionaries with the following keys: ``hits``, ``bandwidth``.

    ``GENERAL``
        Contains, amongst other things, the number of visits
        (``TotalVisits``) and visitors (``TotalUnique``), both being a
        list with a single (string) value.

    ``KEYWORDS``
        Each key is a single search keyword. Values are dictionaries
        that include a ``searches`` key.

    ``OS``
        Keys are OS identifiers (e.g. "winxp", "winlong", "macosx",
        "linux" or "linuxubuntu"), values are dictionaries with a
        ``hits`` key.

    ``PAGEREFS``
        Keys are the referrers (URLs), values are dictionaries with
        the following values: ``hits`` and ``pages``.

    ``SEARCHWORDS``
        Each key is a search phrase. Values are dictionaries that
        include a ``searches`` key.

    ``SEREFERRALS``
        Keys are the search engine identifiers ("google", "yahoo",
        etc.). Values are dictionaries with the following keys:
        ``pages``, ``hits``.

    ``SIDER``
        The most viewed pages: keys are the relative URL, values are
        dictionaries with the following keys: ``pages`` and
        ``bandwidth``.

    ``VISITOR``
        Keys are the (DNS reversed) host of the visitor, values are
        dictionaries with the following keys: ``hits``, ``bandwidth``
        and ``pages``.

    The parser does not make available everything from AWStats report
    files.
    """

    def __init__(self):
        self.data = {}

    def _read_section(self, fp, first_line):
        name, length = first_line.split()
        name = name[len('BEGIN_'):]
        length = int(length)
        lines = []
        while length > 0:
            lines.append(fp.readline().strip())
            length -= 1
        fp.readline()  # eat ending line ('END_<section_name>')
        data_keys = SECTIONS.get(name, None)
        if not data_keys:  # unknown/unsupported section name
            return None, None
        data = defaultdict(dict)
        for line in lines:
            values = line.split()
            key = values[0]
            if data_keys is _special:
                data[key] = values[1:]
            else:
                for i, data_key in enumerate(data_keys):
                    data[key][data_key] = values[i]
        return name, data

    def parse_file(self, path, yyyymm):
        """Parse a single file that corresponds to the given date
        (formatted as YYYYMM).
        """
        with codecs.open(path, 'r', 'utf-8') as fp:
            while 1:
                line = fp.readline()
                if not line:  # end of file
                    break
                while 1:
                    if line.startswith('BEGIN_'):
                        break
                    line = fp.readline()
                section, data = self._read_section(fp, line)
                if not data:
                    continue
                if not section in self.data:
                    self.data[section] = defaultdict(dict)
                self.data[section][yyyymm] = data

    def parse_dir(self, site_id, in_dir, prefix, suffix):
        """Parse all files of the given directory that are related to
        the given site.
        """
        suffix = '.%s.%s' % (site_id, suffix)
        for filename in os.listdir(in_dir):
            if not (filename.startswith(prefix) and filename.endswith(suffix)):
                continue
            mmyyyy = filename[len(prefix):-len(suffix)]
            yyyymm = mmyyyy[2:] + mmyyyy[:2]
            self.parse_file(os.path.join(in_dir, filename), yyyymm)
        return self.data
