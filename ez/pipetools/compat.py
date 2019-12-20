import sys

if sys.version < '3':
    
    
    range = xrange
    text_type = str
    string_types = str
    dict_items = lambda d: iter(d.items())
else:
    from builtins import map, filter, range
    text_type = str
    string_types = str
    dict_items = lambda d: list(d.items())
