import os
from setuptools import find_packages
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
DESCRIPTION = 'AWStatic is a front-end for AWStats.'

REQUIRES = ()

setup(name='AWStatic',
      version='0.1.0',
      description=DESCRIPTION,
      long_description='\n\n'.join((README, CHANGES)),
      classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet :: Log Analysis'),
      author='Damien Baty',
      author_email='damien.baty.remove@gmail.com',
      url='https://github.com/dbaty/AWStatic',
      keywords='web statistics awstats',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      test_suite='awstatic.tests',
      entry_points='''
      [console_scripts]
      awstatic = awstatic.cli:main
      ''')
