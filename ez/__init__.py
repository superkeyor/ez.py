# insert path for pysecretes local and heroku
# use THERE to avoid conflict with fz; well, better delete it when done
import sys, os
exec("try:THERE=os.path.dirname(os.path.abspath(__file__));_=sys.path.remove(THERE) if THERE in sys.path else 0;sys.path.insert(0,THERE)\nexcept:THERE=os.getcwd()") # THERE for interactive run
sys.path.insert(1,'/') if '/' not in sys.path else None
del THERE

from . ez import *
from . firefox import *

__all__=[
'Firefox', 'BY', 'KEYS',
'JDict', 'TimeStamp', 'Moment', 'GSheet', 
'fire', 'requests', 'sqlite3', 'json', 'io', 'os', 'sys', 'platform', 'string', 'random', 're', 'datetime', 'tzlocal', 'pd', 'np', 'urlparse', 'BeautifulSoup', 
]
