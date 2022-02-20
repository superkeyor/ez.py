# insert path for pysecretes local and heroku
import sys, os
exec("try:HERE=os.path.dirname(os.path.abspath(__file__));_=sys.path.remove(HERE) if HERE in sys.path else 0;sys.path.insert(0,HERE)\nexcept:HERE=os.getcwd()") # HERE for interactive run
sys.path.insert(0,'/') if '/' not in sys.path else None

from . ez import *
from . firefox import *

__all__=[
'Firefox', 'BY', 'KEYS',
'JDict', 'TimeStamp', 'Moment', 'GSheet', 
'fire', 'requests', 'sqlite3', 'json', 'io', 'os', 'sys', 'platform', 'string', 'random', 're', 'datetime', 'tzlocal', 'pd', 'np', 'urlparse', 'BeautifulSoup', 
]
