from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree
import sys
from unittest import TestCase


@contextmanager
def temp_folder():
    tmp_dir = mkdtemp()
    try:
        yield tmp_dir
    finally:
        rmtree(tmp_dir)

PY3 = sys.version[0] == '3'
if PY3:  # pragma: no cover
    binary_type = bytes
else:  # pragma: no cover
    binary_type = str


def text_(s, encoding):
    if isinstance(s, binary_type):  # pragma: no cover
        return s.decode(encoding)
    return s  # pragma: no cover


class DummyLogger(object):
    pass
    #def info(self, *args, **kwargs):
    #    pass
    #debug = warning = info


class TestGetPeriods(TestCase):

    def call_fut(self, seq):
        from awstatic.reporter import get_periods
        return get_periods(seq)

    def test_basics(self):
        seq = ['201201', '201112', '201111', '20111101', 'ignore-me']
        expected = ['201201', '201112', '201111', '2011']
        self.assertEqual(self.call_fut(seq), expected)


class TestReporter(TestCase):

    def _make_one(self, **custom):
        from awstatic.reporter import Reporter
        # Provide only sane default values. Everything else should be
        # provided by tests that know what dummy and real values to
        # provide.
        kwargs = {'file_prefix': 'awstats',
                  'file_suffix': 'txt',
                  'logger': DummyLogger()}
        kwargs.update(custom)
        return Reporter(**kwargs)

    def test_prepare_out_dir(self):
        import os.path
        from awstatic.reporter import BACKUP_DIR_NAME
        from awstatic.reporter import TEMPLATE_STRUCTURE
        with temp_folder() as out_dir:
            reporter = self._make_one(out_dir=out_dir, awstats_dir=None,
                                      sites=())
            reporter._prepare_out_dir()
            contents = []
            for dirpath, dirnames, filenames in os.walk(out_dir):
                for l in (dirnames, filenames):
                    for filename in l:
                        path = os.path.join(dirpath, filename)
                        path = path.replace(os.sep, '/')
                        if os.path.isdir(path):
                            path += '/'
                        path = path[1 + len(out_dir):]
                        contents.append(path)
        expected = list(TEMPLATE_STRUCTURE)
        expected.append(BACKUP_DIR_NAME + '/')
        self.assertEqual(sorted(contents), sorted(expected))


class TestReports(TestCase):
    # Test '_create_report_*()' functions

    def test_create_report_top10(self):
        from awstatic.reporter import _create_report_top10
        data = {'SIDER': {'201202':
                              {'url1': {'url': 'url1',
                                        'pages': '14',
                                        'bandwidth': '114'},
                               'url2': {'url': 'url2',
                                        'pages': '12',
                                        'bandwidth': '112'}},
                          '201201':
                              {'url1': {'url': 'url1',
                                        'pages': '14',
                                        'bandwidth': '114'},
                               'url3': {'url': 'url3',
                                        'pages': '33',
                                        'bandwidth': '331'}},
                          '201112':
                              {'url3': {'url': 'url3',
                                        'pages': '32',
                                        'bandwidth': '332'}}}}
        report = _create_report_top10(data)
        expected = {'201202': [{'url': 'url1', 'pages': 14, 'bandwidth': 114},
                               {'url': 'url2', 'pages': 12, 'bandwidth': 112}],
                    '201201': [{'url': 'url3', 'pages': 33, 'bandwidth': 331},
                               {'url': 'url1', 'pages': 14, 'bandwidth': 114}],
                    '2012': [{'url': 'url3', 'pages': 33, 'bandwidth': 331},
                             {'url': 'url1', 'pages': 28, 'bandwidth': 228},
                             {'url': 'url2', 'pages': 12, 'bandwidth': 112}],
                    '201112': [{'url': 'url3', 'pages': 32, 'bandwidth': 332}],
                    '2011': [{'url': 'url3', 'pages': 32, 'bandwidth': 332}]}
        self.assertEqual(report, expected)

    def test_create_report_downloads(self):
        from awstatic.reporter import _create_report_downloads
        data = {'DOWNLOADS': {'201202':
                                  {'url1': {'url': 'url1',
                                            'hits': '14',
                                            'bandwidth': '114'},
                                   'url2': {'url': 'url2',
                                            'hits': '12',
                                            'bandwidth': '112'}},
                              '201201':
                                  {'url1': {'url': 'url1',
                                            'hits': '14',
                                            'bandwidth': '114'},
                                   'url3': {'url': 'url3',
                                            'hits': '33',
                                            'bandwidth': '331'}},
                              '201112':
                                  {'url3': {'url': 'url3',
                                            'hits': '32',
                                            'bandwidth': '332'}}}}
        report = _create_report_downloads(data)
        expected = {'201202': [{'url': 'url1', 'hits': 14, 'bandwidth': 114},
                               {'url': 'url2', 'hits': 12, 'bandwidth': 112}],
                    '201201': [{'url': 'url3', 'hits': 33, 'bandwidth': 331},
                               {'url': 'url1', 'hits': 14, 'bandwidth': 114}],
                    '2012': [{'url': 'url3', 'hits': 33, 'bandwidth': 331},
                             {'url': 'url1', 'hits': 28, 'bandwidth': 228},
                             {'url': 'url2', 'hits': 12, 'bandwidth': 112}],
                    '201112': [{'url': 'url3', 'hits': 32, 'bandwidth': 332}],
                    '2011': [{'url': 'url3', 'hits': 32, 'bandwidth': 332}]}
        self.assertEqual(report, expected)

    def test_create_report_referrers(self):
        from awstatic.reporter import _create_report_referrers
        data = {'PAGEREFS': {'201202':
                                 {'url1': {'url': 'url1',
                                           'pages': '14',
                                           'hits': '114'},
                                  'url2': {'url': 'url2',
                                           'pages': '12',
                                           'hits': '112'}},
                             '201201':
                                 {'url1': {'url': 'url1',
                                           'pages': '14',
                                           'hits': '114'},
                                  'url3': {'url': 'url3',
                                           'pages': '33',
                                           'hits': '331'}},
                             '201112':
                                 {'url3': {'url': 'url3',
                                           'pages': '32',
                                           'hits': '332'}}}}
        report = _create_report_referrers(data)
        expected = {'201202': [{'url': 'url1', 'pages': 14, 'hits': 114},
                               {'url': 'url2', 'pages': 12, 'hits': 112}],
                    '201201': [{'url': 'url3', 'pages': 33, 'hits': 331},
                               {'url': 'url1', 'pages': 14, 'hits': 114}],
                    '2012': [{'url': 'url3', 'pages': 33, 'hits': 331},
                             {'url': 'url1', 'pages': 28, 'hits': 228},
                             {'url': 'url2', 'pages': 12, 'hits': 112}],
                    '201112': [{'url': 'url3', 'pages': 32, 'hits': 332}],
                    '2011': [{'url': 'url3', 'pages': 32, 'hits': 332}]}
        self.assertEqual(report, expected)

    def test_create_report_keywords(self):
        from awstatic.reporter import _create_report_keywords
        data = {'KEYWORDS': {'201202':
                                 {'keyword1': {'keyword': 'keyword1',
                                               'searches': '14'},
                                  'keyword2': {'keyword': 'keyword2',
                                               'searches': '112'}},
                             '201201':
                                 {'keyword1': {'keyword': 'keyword1',
                                               'searches': '114'},
                                  'keyword3': {'keyword': 'keyword3',
                                               'searches': '331'}},
                             '201112':
                                 {'keyword3': {'keyword': 'keyword3',
                                               'searches': '332'}}}}
        report = _create_report_keywords(data)
        expected = {'201202': [{'keyword': 'keyword2', 'searches': 112},
                               {'keyword': 'keyword1', 'searches': 14}],
                    '201201': [{'keyword': 'keyword3', 'searches': 331},
                               {'keyword': 'keyword1', 'searches': 114}],
                    '2012': [{'keyword': 'keyword3', 'searches': 331},
                             {'keyword': 'keyword1', 'searches': 128},
                             {'keyword': 'keyword2', 'searches': 112}],
                    '201112': [{'keyword': 'keyword3', 'searches': 332}],
                    '2011': [{'keyword': 'keyword3', 'searches': 332}]}
        self.assertEqual(report, expected)

    def test_create_report_keywords_unquote(self):
        # Check that keywords are correctly unquoted
        from awstatic.compat import quote_plus
        from awstatic.reporter import _create_report_keywords
        encoded = b'\xc3\xa9l\xc3\xa9phant'
        decoded = text_(encoded, 'utf-8')
        quoted = text_(quote_plus(encoded), 'utf-8')
        data = {'KEYWORDS': {'201202': {quoted: {'keyword': quoted,
                                                 'searches': '14'}}}}
        report = _create_report_keywords(data)
        expected = {'201202': [{'keyword': decoded, 'searches': 14}],
                    '2012': [{'keyword': decoded, 'searches': 14}]}
        self.assertEqual(report, expected)

    def test_create_report_phrases(self):
        from awstatic.reporter import _create_report_phrases
        data = {'SEARCHWORDS': {'201202':
                                 {'phrase 1': {'phrase': 'phrase 1',
                                               'searches': '14'},
                                  'phrase 2': {'phrase': 'phrase 2',
                                               'searches': '112'}},
                                '201201':
                                    {'phrase 1': {'phrase': 'phrase 1',
                                                  'searches': '114'},
                                     'phrase 3': {'phrase': 'phrase 3',
                                                  'searches': '331'}},
                                '201112':
                                    {'phrase 3': {'phrase': 'phrase 3',
                                                  'searches': '332'}}}}
        report = _create_report_phrases(data)
        expected = {'201202': [{'phrase': 'phrase 2', 'searches': 112},
                               {'phrase': 'phrase 1', 'searches': 14}],
                    '201201': [{'phrase': 'phrase 3', 'searches': 331},
                               {'phrase': 'phrase 1', 'searches': 114}],
                    '2012': [{'phrase': 'phrase 3', 'searches': 331},
                             {'phrase': 'phrase 1', 'searches': 128},
                             {'phrase': 'phrase 2', 'searches': 112}],
                    '201112': [{'phrase': 'phrase 3', 'searches': 332}],
                    '2011': [{'phrase': 'phrase 3', 'searches': 332}]}
        self.assertEqual(report, expected)

    def test_create_report_phrases_unquote(self):
        # Check that phrases are correctly unquoted
        from awstatic.compat import quote_plus
        from awstatic.reporter import _create_report_phrases
        encoded = b"ceci n'est pas un \xc3\xa9l\xc3\xa9phant"
        decoded = text_(encoded, 'utf-8')
        quoted = text_(quote_plus(encoded), 'utf-8')
        data = {'SEARCHWORDS': {'201202': {quoted: {'phrase': quoted,
                                                    'searches': '14'}}}}
        report = _create_report_phrases(data)
        expected = {'201202': [{'phrase': decoded, 'searches': 14}],
                    '2012': [{'phrase': decoded, 'searches': 14}]}
        self.assertEqual(report, expected)
