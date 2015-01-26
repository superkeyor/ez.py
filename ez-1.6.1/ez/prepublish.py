# generate readme file and increase version number

from codecs import open  # To use a consistent encoding
from os import path
import os, sys
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, MODULE_PATH)
here = path.abspath(path.dirname(__file__))

# readme
from __init__ import __doc__ as doc
with open(path.join(os.path.dirname(here), 'README.rst'), encoding='utf-8', mode='w') as f:
    f.write(doc)

# version
from version import __version__ as ver
ver = ver.replace('.','')
ver=int(ver)
ver += 1
ver = list(str(ver))
ver = '.'.join(ver)
ver = '__version__ = \'' + ver + '\''
with open(path.join(here, 'version.py'), encoding='utf-8', mode='w') as f:
    f.write(ver)