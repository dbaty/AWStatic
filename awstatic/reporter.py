from collections import defaultdict
import json
import os
import shutil
from time import strftime

from awstatic.compat import PY3
from awstatic.compat import unquote_plus
from awstatic.parser import Parser
from awstatic.utils import interpolate
from awstatic.utils import get_number_of_days


BACKUP_DIR_NAME = '.backup'
DATA_DIR_NAME = 'data'
# Paths that denote directories must end with a slash.
TEMPLATE_STRUCTURE = ('assets/',
                      'assets/css/',
                      'assets/css/style.css',
                      'assets/img/',
                      'assets/img/loading.gif',
                      'assets/js/',
                      'assets/js/libs/',
                      'assets/js/libs/bootstrap-dropdown.js',
                      'assets/js/libs/handlebars-1.0.0.beta.6.min.js',
                      'assets/js/libs/jquery-1.8.0.min.js',
                      'assets/js/libs/jquery.flot-0.7.min.js',
                      'assets/js/ui.js',
                      'index.html',
                      '%s/' % DATA_DIR_NAME)


class Reporter(object):

    def __init__(self, awstats_dir, file_prefix, file_suffix,
                 sites, out_dir, logger):
        self.awstats_dir = awstats_dir
        self.file_prefix = file_prefix
        self.file_suffix = file_suffix
        self.sites = sites
        self.out_dir = out_dir
        self.backup_dir = os.path.join(self.out_dir, BACKUP_DIR_NAME)
        self.data_dir = os.path.join(self.out_dir, DATA_DIR_NAME)
        self.template_dir = os.path.join(os.path.dirname(__file__), 'template')
        self.log = logger

    def run(self):
        """Read statistics and generate report."""
        self._prepare_out_dir()
        self._interpolate_in_index_html()

        # 'data/sites.json' contains the list of the sites.
        sites_json = os.path.join(self.data_dir, 'sites.json')
        with open(sites_json, 'w+') as out:
            out.write(json.dumps([site_id for (site_id, url) in self.sites]))

        # Parse each AWStats report file.
        for site_id, url in self.sites:
            parser = Parser()
            self.log.info('Reading AWStats data for "%s"...', site_id)
            data = parser.parse_dir(site_id, self.awstats_dir,
                                    self.file_prefix, self.file_suffix)
            report = create_report(data, url)
            site_path = os.path.join(self.data_dir, '%s.json' % site_id)
            self.log.info('Writing "%s"...', site_path)
            with open(site_path, 'w+') as out:
                out.write(json.dumps(report))

        # Everything went fine, we can remove the backup.
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def _prepare_out_dir(self):
        """Prepare output directory.

        Here we backup the previous run (if any) in case something
        goes wrong later and we create template files.
        """
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
        elif not os.path.exists(self.backup_dir):
            os.mkdir(self.backup_dir)
            for filename in os.listdir(self.out_dir):
                if filename == BACKUP_DIR_NAME:
                    continue
                path = os.path.join(self.out_dir, filename)
                shutil.move(path, self.backup_dir)
        for res in TEMPLATE_STRUCTURE:
            filename = res.replace('/', os.sep)
            src_path = os.path.join(self.template_dir, filename)
            out_path = os.path.join(self.out_dir, filename)
            if res.endswith('/'):
                os.mkdir(out_path)
            else:
                shutil.copy(src_path, out_path)

    def _interpolate_in_index_html(self):
        """Replace dynamic content in ``index.html``."""
        path = os.path.join(self.out_dir, 'index.html')
        with open(path) as fp:
            content = fp.read()
        today = strftime('%d %B %Y')
        content = interpolate(content, last_update=today)
        with open(path, 'w+') as fp:
            fp.write(content)


def create_report(data, url):
    report = {'url': url}
    report['overview'] = _create_report_overview(data)
    report['top10'] = _create_report_top10(data)
    report['downloads'] = _create_report_downloads(data)
    report['referrers'] = _create_report_referrers(data)
    report['keywords'] = _create_report_keywords(data)
    report['phrases'] = _create_report_phrases(data)
    # FIXME: for each report, calculate all-time total
    report['periods'] = get_periods(report['overview'].keys())
    return report


def _create_report_overview(data):
    """Number of hits, pages, visits, visitors and bandwith."""
    empty_stats = {'hits': 0,
                   'pages': 0,
                   'bandwidth': 0,
                   'visits': 0}
    report = {}
    all_time = empty_stats.copy()
    for yyyymm, d in data['DAY'].items():
        yyyy = yyyymm[:4]
        year = report.get(yyyy, None)
        if year is None:
            year = report[yyyy] = empty_stats.copy()
        month = empty_stats.copy()
        for day in range(1, 1 + get_number_of_days(yyyymm)):
            yyyymmdd = '%s%02d' % (yyyymm, day)
            info = d.get(yyyymmdd, {})
            day_data = {'visitors': 0}  # not reported by AWStats
            for key in ('hits', 'pages', 'bandwidth', 'visits'):
                day_data[key] = int(info.get(key, 0))
                month[key] += day_data[key]
                year[key] += day_data[key]
                all_time[key] += day_data[key]
            report[yyyymmdd] = day_data
        month['visitors'] = data['GENERAL'][yyyymm]['TotalUnique'][0]
        report[yyyymm] = month
    report['all-time'] = all_time  # FIXME: not used (yet)
    return report


def _create_report_top10(data):
    keys = {'url': None, 'pages': int, 'bandwidth': int}
    discr = 'url'
    aggregate_keys = ('pages', 'bandwidth')
    return _create_report_helper(
        data, 'SIDER', keys, discr, aggregate_keys, 'pages', top=10)


def _create_report_downloads(data):
    keys = {'url': None, 'hits': int, 'bandwidth': int}
    discr = 'url'
    aggregate_keys = ('hits', 'bandwidth')
    return _create_report_helper(
        data, 'DOWNLOADS', keys, discr, aggregate_keys, 'hits', top=10)


def _create_report_referrers(data):
    keys = {'url': None, 'pages': int, 'hits': int}
    discr = 'url'
    aggregate_keys = ('pages', 'hits')
    return _create_report_helper(
        data, 'PAGEREFS', keys, discr, aggregate_keys, 'pages')


def _create_report_keywords(data):
    # In Python 3, 'unquote_plus()' must be called with a 'str', which
    # is the case. In Python 2, if the quoted keyword is a 'unicode'
    # object, unquoting it does not yield back the original keyword.
    #
    # In Python 2:
    #    >>> encoded = '\xc3\xa9'
    #    >>> decoded = unicode(encoded, 'utf-8')
    #    >>> decoded
    #    u'\xe9'
    #    >>> quote_plus(encoded)
    #    '%C3%A9'
    # Now the following is fine:
    #    >>> unquote_plus('%C3%A9')
    #    '\x3\xa9'
    # But we cannot do that. Since 'unquote_plus()' requires a 'str'
    # in Python 3, we pass is a 'unicode' object in Python 2, and
    # unquoting the 'unicode' object does not return the decoded
    # string:
    #    >>> unquote_plus(unicode('%C3%A9'))
    #    u'\xc3\xa9'
    #
    # This is why, in Python 2, we first encode the 'unicode' object,
    # then unquote it, and finally decode it back to have a 'unicode'
    # object.
    if PY3:  # pragma: no cover
        converter = unquote_plus
    else:
        converter = lambda uni: unquote_plus(
            uni.encode('utf-8')).decode('utf-8')
    keys = {'keyword': converter, 'searches': int}
    discr = 'keyword'
    aggregate_keys = ('searches', )
    return _create_report_helper(
        data, 'KEYWORDS', keys, discr, aggregate_keys, 'searches', top=30)


def _create_report_phrases(data):
    # See comments in '_create_report_keywords()' for details about
    # the block below.
    if PY3:  # pragma: no cover
        converter = unquote_plus
    else:
        converter = lambda uni: unquote_plus(
            uni.encode('utf-8')).decode('utf-8')
    keys = {'phrase': converter, 'searches': int}
    discr = 'phrase'
    aggregate_keys = ('searches', )
    return _create_report_helper(
        data, 'SEARCHWORDS', keys, discr, aggregate_keys, 'searches', top=30)


def _create_report_helper(data, section_key, keys, discr, aggregate_keys,
                          sort_on, top=None):
    """An helper for several '_create_report_*()' functions (**not**
    including '_create_report_overview()', though).

    ``data``
        The raw data returned by ``awstatic.parser.Parser()``.

    ``section_key``
        The name of the section to look for in ``data``. See
        ``awstatic.parser.Parser()`` for a list of available keys.

    ``keys``
        Must be a dictionary. The keys of this dictionary will be
        looked up in ``data`` (see ``awstatic.parser.SECTIONS`` for a
        list of available keys). The values are a callable that will
        convert the value (e.g. ``int()`` or
        ``urllib.unquote_plus()``), or ``None`` if no conversion is
        needed.

    ``discr``
        The discriminant to look for in ``data``. It should be one of
        the keys of ``keys``.

    ``aggregate_keys``
        A list of keys (amongst those listed in ``keys``) that should
        be aggregated in the year report.

    ``sort_on``
        The key to sort on, should one of those listed in ``keys`` and
        ``aggregate_keys``.

    ``top``
        The maximum number of entries to keep, or ``None`` if all
        entries must be kept.

    I reckon it is a bit painful to read...
    """
    report = {}
    # 'years' will aggregate month data. Is a dict of dict:
    #    {'yyyy': {discr1: {...}, discr2: {...}, ...}}
    # For example, for the top 10, it will look like this:
    #     {'2012': {'url1': {'pages': 10, 'bandwidth': 200},
    #               'url2': {'pages': 20, 'bandwidth': 300}}
    empty_aggregate_dict = lambda: {key: 0 for key in aggregate_keys}
    years = defaultdict(
        lambda: defaultdict(empty_aggregate_dict))
    # We are going to iterate over each key of the report, i.e. over
    # each month.
    for yyyymm, d in data[section_key].items():
        # Build a dictionary with the keys listed in ``keys`` and
        # convert values. This is where we convert strings to
        # integers.
        items = []
        for item in d.values():
            converted_item = {}
            for key, converter in keys.items():
                value = item[key]
                if converter is not None:
                    value = converter(value)
                converted_item[key] = value
            items.append(converted_item)
        report[yyyymm] = items
        # Aggregate data for this year.
        yyyy = yyyymm[:4]
        for item in items:
            for key in aggregate_keys:
                years[yyyy][item[discr]][key] += item[key]
    # Sort data for each month.
    for month, items in report.items():
        items = sorted(items, key=lambda i: i[sort_on], reverse=True)
        if top:
            items = items[:top]
        report[month] = items
    # Sort data for each year. The key is the year, the value is a
    # dictionary, where the key is the discriminant value (for example
    # the URL in the top 10 pages report, of the keyword for the
    # keywords report) and the value is a dictionary that contains the
    # data (and has ``keys`` as keys).
    for year, dicts in years.items():
        items = []
        for discr_value, d in dicts.items():
            item = {discr: discr_value}
            item.update(d)
            items.append(item)
        items = sorted(items, key=lambda i: i[sort_on], reverse=True)
        if top:
            items = items[:top]
        report[year] = items
    return report


def get_periods(keys):
    """Return periods of time to display (sorted with the most recent
    first).

    ``keys`` must be a sequence of strings that should be formatted as
    'YYYYMM'. Keys that have less or more than 6 characters are
    ignored. This function returns all given months plus all years
    that have at least two months listed.

    >>> get_periods(['201201', '201202', '201112'])
    ['201202', '201201', '2012', '201112']
    """
    periods = []
    years = defaultdict(lambda: 0)
    for key in keys:
        if len(key) != 6:
            continue
        mm = key[4:]
        yyyy = key[:4]
        years[yyyy] += 1
        periods.append(''.join((yyyy, mm)))
    periods.extend(filter(lambda y: years[y] > 1, years.keys()))
    periods.sort(reverse=1)
    return periods
