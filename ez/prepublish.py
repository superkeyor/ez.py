# generate readme file and increase version number

from codecs import open  # To use a consistent encoding
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# version
from version import __version__ as ver
ver = ver.replace('.','')
ver=int(ver)
ver += 1
ver = list(str(ver))
ver = '.'.join(ver)
ver = '__version__ = \'' + ver + '\''
with open(os.path.join(HERE, 'version.py'), encoding='utf-8', mode='w') as f:
    f.write(ver)