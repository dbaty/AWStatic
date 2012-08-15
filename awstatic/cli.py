"""Client entry point."""

from argparse import ArgumentParser
import logging
import os
import sys

from awstatic import __version__ as VERSION
from awstatic.compat import SafeConfigParser
from awstatic.reporter import Reporter


DEFAULT_CONFIG_FILE = 'awstatic.ini'
DEFAULT_LOG_LEVEL = 'warning'


def main():
    args = parse_args()
    config_file = args.config_file
    config = get_config(config_file)
    pdb_mode = config.pop('pdb')
    r = Reporter(**config)
    try:
        r.run()
    except:
        logging.exception('An unexpected error occurred (see traceback '
                          'below). Program aborted.')
        if pdb_mode:
            import pdb
            pdb.post_mortem()
        sys.exit(1)
    config['logger'].info('All reports have been successfully generated.')
    return 0


def parse_args():  # pragma: no coverage
    parser = ArgumentParser()
    add = parser.add_argument
    add('-v', '--version',
        action='version',
        version='%%(prog)s %s' % VERSION)
    add('config_file',
        metavar='CONFIG_FILE',
        nargs='?',
        default=DEFAULT_CONFIG_FILE,
        help='The configuration file to use. Default is '
             '"./%s".' % DEFAULT_CONFIG_FILE)
    return parser.parse_args()


def get_config(config_file):
    """Return a valid configuration (as a dictionary to be passed on
    to the constructor of the ``Reporter`` class) from the given
    configuration file.
    """
    config_parser = SafeConfigParser()
    if config_parser.read(config_file) != [config_file]:
        sys.exit('The configuration file at "%s" could '
                 'not be read.' % config_file)
    options = dict(config_parser.items('awstatic'))

    # Check unknown directives
    for key in options.keys():
        if key not in ('awstats_dir', 'file_prefix', 'file_suffix',
                       'sites', 'out_dir', 'pdb'):
            sys.exit('Unknown option in configuration file: "%s". '
                     'Program aborted.' % key)

    # Check required directives
    for opt in ('awstats_dir', 'out_dir', 'sites'):
        if opt not in options.keys():
            sys.exit('A required directive is missing from the '
                     'configuration file: "%s".' % opt)

    # Check directories
    awstats_dir = options['awstats_dir']
    awstats_dir = os.path.abspath(awstats_dir)
    if not os.path.isdir(awstats_dir):
        sys.exit('The value of "awstats_dir" ("%s") should be a valid '
                 'directory.' % awstats_dir)
    out_dir = options['out_dir']
    out_dir = os.path.abspath(out_dir)
    if not os.path.isdir(os.path.dirname(out_dir)):
        sys.exit('The parent of "out_dir" ("%s") must be an existing '
                 'directory.' % out_dir)
    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        sys.exit('The value of "out_dir" ("%s") should be a directory.' %
                 out_dir)

    # Prepare config dict and provide default values for optional
    # directives
    config = {'awstats_dir': awstats_dir,
              'out_dir': out_dir,
              'file_prefix': options.get('file_prefix', 'awstats'),
              'file_suffix': options.get('file_suffix', 'txt'),
              'sites': [],
              'pdb': options.get('pdb', '').lower() in ('1', 'true')}
    for id_url in options['sites'].split():
        error = False
        try:
            site_id, url = id_url.split('=', 1)
        except ValueError:
            error = True
        # Too few (error is True) or too many (url is a list)
        # '='-separated components
        if error or not isinstance(url, str):
            sys.exit('Wrong syntax for "sites".')
        config['sites'].append((site_id, url))

    config['logger'] = get_logger(dict(config_parser.items('logger')))
    return config


def get_logger(options):
    logger = logging.getLogger('AWStatic')
    level = options.get('level', DEFAULT_LOG_LEVEL).lower()
    level = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR}[level]
    logger.setLevel(level)
    path = options.get('path', '-')
    if path == '-':
        handler = logging.StreamHandler()
    else:
        # Error log file must be absolute, we do not want to guess.
        if os.path.abspath(path) != path:
            sys.exit('The path to the error file must be absolute.')
        handler = logging.FileHandler(path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    sys.exit(main())
