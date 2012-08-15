from unittest import TestCase

import mock


class TestParser(TestCase):

    def _make_one(self):
        from awstatic.parser import Parser
        return Parser()

    @mock.patch('awstatic.parser.Parser.parse_file')
    def test_parse_dir(self, mock_parse_file):
        # Test that we read only the right files.
        import os
        here = os.path.dirname(__file__)
        in_dir = os.path.join(here, 'data', 'awstats')
        parser = self._make_one()
        parser.parse_dir('exemple.com', in_dir, 'awstats', 'txt')
        ap = lambda filename: os.path.join(in_dir, filename)
        expected = [((ap('awstats012012.exemple.com.txt'), '201201'), ),
                    ((ap('awstats022012.exemple.com.txt'), '201202'), ),
                    ((ap('awstats032012.exemple.com.txt'), '201203'), ),
                    ((ap('awstats042012.exemple.com.txt'), '201204'), ),
                    ((ap('awstats052012.exemple.com.txt'), '201205'), ),
                    ((ap('awstats062012.exemple.com.txt'), '201206'), )]
        self.assertEqual(mock_parse_file.call_args_list, expected)

    def test_parse_file_basics(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'data', 'awstats', 'basics.txt')
        parser = self._make_one()
        parser.parse_file(path, '201201')
        expected = {'GENERAL':
                        {'201201': {'TotalVisits': ['6'],
                                    'TotalUnique': ['6']}},
                    'VISITOR':
                        {'201201':
                             {'8.8.8.8.rev.sfr.net':
                                  {'host': '8.8.8.8.rev.sfr.net',
                                   'pages': '14',
                                   'hits': '38',
                                   'bandwidth': '1213892'},
                              'i04m-8-8-8-8.d4.club-internet.fr':
                                  {'host': 'i04m-8-8-8-8.d4.club-internet.fr',
                                   'pages': '2',
                                   'hits': '12',
                                   'bandwidth': '654661'},
                              }
                         }
                    }
        self.assertEqual(parser.data, expected)
