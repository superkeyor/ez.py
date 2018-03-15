from utils import foreach

__version__ = VERSION = 0, 3, 0
__versionstr__ = VERSION > foreach(str) | '.'.join

from main import pipe, X, maybe, xpartial
from utils import *

# prevent namespace pollution
import compat
for symbol in dir(compat):
    if globals().get(symbol) is getattr(compat, symbol):
        globals().pop(symbol)
