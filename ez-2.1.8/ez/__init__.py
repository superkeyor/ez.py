from easyshell import *
from easyshell import __doc__ as doc1
from pyg import Mail, mail, AddEvent, addevent, Sheet
from pyg import Mail2, mail2, AddEvent2, addevent2, Sheet2
from pyg import __doc__ as doc2
from version import __version__
try:
    from pyperclip import copy as SetClip
    from pyperclip import copy as setclip
    from pyperclip import paste as GetClip
    from pyperclip import paste as getclip
except:
    pass    
__doc__ = doc1 + '\n\n\n\n' + doc2
del doc1, doc2