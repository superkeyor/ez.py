# https://docs.python.org/2/distutils/setupscript.html#distutils-installing-package-data

# from distutils.core import setup   # does not have find_packages
from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path
here = path.abspath(path.dirname(__file__))
######################################################################################
PACKAGE = 'ez'
description='easy stuff'
keywords='shell, cross-platform, easy, wrapper'
packages = find_packages()
# packages.append('ez.timezone.pytz')
# install_requires = ['django-pipeline==1.1.22', 'south>=0.7']
# install_requires=['peppercorn']
# install_requires=['']
install_requires=['pytz', 'tzlocal', 'Send2Trash', 'keyring', 'pyperclip', 'gmail', 'O365', 'chardet', 'psutil',
                 'xlsxwriter', 'xlwt', 'xlrd', 'PyMuPDF', 'pdfCropMargins', 'python-docx', 'python-pptx',
                 'requests>=2.26.0', 'selenium-requests', 'selenium-wire', 'selenium<4',
                 'noraise', 'fake_useragent', 'tldextract',
                 'pynput', 'gspread>=3.7.0', 'tenacity', 'fire', 'parse']
# 'imessage_reader' not available on heroku/linux when installing ez
import platform
if platform.system()=='Darwin': install_requires.append('imessage_reader')
######################################################################################
# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

theNameSpace = {}
with open(path.join(here, PACKAGE, 'version.py'), encoding='utf-8') as f:
    exec(f.read(), theNameSpace)
version=theNameSpace['__version__']

setup(
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=['flask', 'flask.ext', 'flask.testsuite'],
    # packages=find_packages(where='.', exclude=(['tests', '*.tests', '*.tests.*'])),  # auto from __init__.py
    # find_packages uses fnmatchcase for its exclude filtering. You can test if your exclusion pattern matches a package name as follows:
    # >>> from fnmatch import fnmatchcase
    # >>> fnmatchcase('my.package.name.tests', 'tests')    False
    packages=packages,

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # for setuptools/distribute, you specify version info with the comparison operators (like ==, >=, or <=).
    # For example:
    # install_requires = ['django-pipeline==1.1.22', 'south>=0.7']
    # install_requires=['peppercorn'],
    install_requires=install_requires,

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    # extras_require = {
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # package_data is a low-down, dirty lie. It is only used when building binary packages (python setup.py bdist ...) 
    # but not when building source packages (python setup.py sdist ...)
    # using MANIFEST.in will work both for binary and for source distributions
    # see http://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distribute
    # https://pythonhosted.org/setuptools/setuptools.html#using-find-packages
    # include_package_data aims to include files from version control, better not use it:
    # include_package_data=True,
    # exclude_package_data={'': ['.gitignore'], 'images': ['*.xcf', '*.blend']},   # '' means all packages
    # exclude_package_data={'': ['.gitignore', 'pygmailconfig']},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },

    name=PACKAGE,
    description=description,
    # What does your project relate to?
    keywords=keywords,
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/development.html#single-sourcing-the-version
    version=version,

    # long_description=long_description,
    long_description='This module is for easy interaction with linux, Mac OS X, Windows shell.',

    # The project's main homepage.
    url='https://pypi.python.org/pypi/' + PACKAGE,
    license='GPLv3+',
    author='Jerry Zhu',
    author_email='jerryzhujian9@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
