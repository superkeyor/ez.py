import ast
from pathlib import Path
from setuptools import find_packages, setup


HERE = Path(__file__).resolve().parent
PACKAGE = 'ez'


def read_assignment(relative_path, name):
    """Read a literal module assignment without importing runtime dependencies."""
    source = ast.parse((HERE / relative_path).read_text(encoding='utf-8'))
    values = [
        node.value
        for node in source.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    ]
    if len(values) != 1:
        raise ValueError(f'Expected one literal {name} assignment in {relative_path}.')
    return ast.literal_eval(values[0])


cli_commands = read_assignment(f'{PACKAGE}/ez.py', '_CLI_COMMANDS')
version = read_assignment(f'{PACKAGE}/version.py', '__version__')


install_requires = [
    # Distribution
    'twine',

    # Dates and time zones
    'pytz',
    'tzlocal',

    # Files and system
    'Send2Trash',
    'Duplicate-Finder',  # Find duplicated files
    'psutil; sys_platform != "linux"',

    # Desktop, clipboard and credentials
    'pyperclip',
    'keyring',
    'mss',
    'pynput; sys_platform != "linux"',  # instead of pyautogui (problematic on macOS)
    'imessage_reader; sys_platform == "darwin"',

    # Office documents and Markdown conversion
    'markitdown[pdf,docx,pptx]',
    'openpyxl',
    'xlsxwriter',
    'xlwt',
    'xlrd',
    'python-docx',
    'python-pptx',
    'docx2pdf; sys_platform != "linux"',

    # PDF processing
    'PyMuPDF',
    'pdfCropMargins',
    'pdfannots',

    # HTTP and web
    'requests',
    'webdavclient3',
    'fake_useragent',
    'tldextract',
    'tenacity',

    # Text encoding, HTML/XML and eBooks
    'chardet',
    'beautifulsoup4',
    'lxml',
    'ebooklib',

    # Data analysis and storage
    'pandas',
    'numpy',
    'pyarrow',

    # Images, media downloads and subtitles
    'Pillow',
    'yt-dlp[default,curl-cffi]',
    'pysubs2',

    # Text to speech
    'gTTS',
    'edge-tts',  # Bash terminal commands

    # Cloud storage, spreadsheets and calendars
    'dropbox',
    'pydrive2',
    'gspread',
    'gcsa',  # Google Calendar

    # Email and Microsoft 365
    'yagmail',
    'imap-tools',  # replacing 'supermail', too thin a wrapper
    'O365',  # Microsoft Office 365
]


setup(
    name=PACKAGE,
    version=version,
    description='easy stuff',
    keywords='shell, cross-platform, easy, wrapper',
    long_description=(HERE / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url=f'https://github.com/superkeyor/{PACKAGE}.py',
    license='AGPLv3+',
    author='Keyor',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.11',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            f'{command}=ez.ez:_cli' for command in cli_commands
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
)
