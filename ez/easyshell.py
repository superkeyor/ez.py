__author__ = "jerryzhujian9@gmail.com"

__doc__ = """This module is for easy interaction with linux, Mac OS X, Windows shell.
=============================================
jerryzhujian9_at_gmail.com
Tested under python 2.7
To see your python version
in terminal: python -V
or in python: import sys; print (sys.version)
=============================================
Install:
https://pypi.python.org/pypi/ez
pip install ez
no dependencies

Almost all commands support the usage of '~', '..', '.', '?', '*' in path (ls,fls only support regular expression).
Symbolic link itself is the target of file operations; the actual file should be safe.

see also pyg.py
debug(1/0)
    # 0 = everything will be actually executed
    # 1 = simulate operations of cp, mv, execute; other commands will be actually performed.
          will print out simulated commands, useful for debugging and for counting files when necessary.
error(msg)

readx(path, sheet=0, r=[1,], c=None)  # Read xlsx, xls file into a list
savex(path, data, header=None, delimiter=",", sheet_name='Sheet1') # Write a list of list to a xlsx (xlsxwriter), xls(xlwt), csv file

fullpath(path) fp()
pwd() or cwd()  # Returns current working director.
csd() # Returns full path of current script directory, i.e. the directory where the running script is. 
csf() # Returns current script name without ext.
parentdir(path) pr() # Returns the parent directory of a path.
joinpath(path1[, path2[, ...]])   jp() # Returns the joined path. Supports vectorization.
splitpath(path) sp() # Returns a list of path elements: [path, file, ext]. Supports vectorization.
cd(path)    # Changes to a new working directory.
stepfolder(-1)

trim(string,how[,chars])
join(sep,string1,string2), join(sep,array) # Glues together strings with sep. Supports vectorization.
sort(array)
replace(theList,theItem,replacement), remove(theList,theItem)

ls([path[, regex]], full=True, dotfile=False)    # Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
lsd([path[, regex]], full=False, dotfolder=False)
fls([path[, regex, dotf=False]])   # Returns a list of files with their full paths in flattened path (i.e. walk each subdirectory).
# the filter only works for short file name not for full file name, i.e. the file name itself not its full path
# regular expression is case-sensitive
# usage: ls(); ls(cwd()); ls(cwd(), "\.py$")

mkdir("path/to/a/directory")    # Makes a directory (also any one of the "path", "to", "a" directories if not exits).
rn(old, new) # Renames old to new.
exists(path)    # Returns the existence of path (0 or 1).
rm(path)    # Deletes a file or folder. Supports wildcards, vectorization.
cp(source, destination)  # Copies source file(s) or folder to destination. Supports wildcards, vectorization.
mv(source, destination)  # Moves source file(s) or folder to destination. Supports wildcards, vectorization.

sprintf(formatString, *args, **kwargs)
evaluate(exp)
# Executes a shell command
# execute/esp/espR no capture output (subprocess.call), execute1 discard--not return--captured, execute2 captures output (subprocess.Popen)
execute, execute1, execute2    
esp, esp1, esp2 # execute sprintf shell commands
espR, espR1, espR2 # execute sprintf R codes
with nooutput():
    print 'this is will not be printed in stdout'
pprint(text,color='green') # color print; ppprint() # "pretty-print" arbitrary Python data structures
beep()  # Beeps to notify user.
which(name) # Prints where a module is and in which module a function is. which('python') returns which python is being used.
help(name)/doc(name) # name is a string, Prints the doc string of a module/class/function
    when write a module, add:
    __doc__ = three double quotes blabla three double quotes         <-----this is module's docstring, use explicit

    when write a function/class:
    def function(arg):
        three double quotes Returns, blabla three double quotes      <-----this is function's doctoring, use implicit
        return sth
ver(package_name) version(package_name), see a package's version.  package_name could be 'python'
whos(name),whos() list imported functions/packages

logon(file="log.txt", mode='a', status=True, timestamp=True), logoff()

tree([path[, forest=True]) # Prints a directory tree structure. 
    forest=True (default) prints only folders, i.e., print less to show the big forest
    forest=False prints files plus folders

[starts, ends] = regexp(string, pattern); regexp(string, pattern, method='split/match'), regexpi
regexprep(string, pattern, replace, count=0), regexprepi

iff(expression, result1, result2), ifelse()
clear(module, recursive=False)

num(string)
isempty(s)
Randomize(x), randomize(x) # Sets a randomization seed.
RandomizeArray(list=[])   randomizearray(list=[])  # Shuffles a list in place.
Random(a,b) random(a,b) # Returns a random integer N such that a <= N <= b.
RandomChoice(seq), randomchoice(seq) # Returns a random element from sequence
Permute(iterable=[]) permute(iterable=[]) # Returns permutations in a list

unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]

JDict() # Jerry's dictionary, customized ordered dictionary class with convient attributes and methods, see help(JDict)
Moment(timezone)    # Generates the current datetime in specified timezone, or local naive datetime if omitted.

SetClip(content), setclip(content)   # Copy/Write something to current clipboard
content = GetClip(), content = getclip()   # Read out content from current clipboard and assign to a variable

lines(path='.', pattern='\.py$|.ini$|\.c$|\.h$|\.m$', recursive=True) # Counts lines of codes, counting empty lines as well.
keygen(length=8, complexity=3)  # generate a random key
hashes(filename): # Calculate/Print a file's md5 32; sha1 32; can handle big files in a memory efficient way
pinyin()
hanzifreq()
pipe usage: result = [1,2,3,0] > ez.pipe | len | str (or [1,2,3,0]>ez.pipe|len|str) # http://0101.github.io/pipetools/doc/
"""

# reference: abspath for ../ ./, expanduser for ~, glob to resolve wildcards, fnmatch.translate wildcards to re
import os, sys, platform, string, random, shutil, re, subprocess, glob, ConfigParser, fnmatch
from os.path import abspath, basename, dirname, splitext, isfile, isdir, realpath, expanduser

_DEBUG_MODE = 0
def ShellDebug(debugMode=1):
    global _DEBUG_MODE
    _DEBUG_MODE = debugMode
debug = ShellDebug    

#def ReadConfig(item):
#    """Read a variable from the config.ini file"""
#    config = ConfigParser.RawConfigParser()
#    config.read("config.ini")
#    return config.get("Default",item).strip("\"\" ")

from os import getcwd as pwd
from os import getcwd as cwd

def error(msg):
    raise Exception(msg)

def fullpath(path):
    """
    fullpath(path) # Returns the full path by resolving ~ and relative path.
    note: no trailing / returned, at least on mac os x
    """
    # https://stackoverflow.com/a/40311142/2292993
    # os.path.abspath returns the absolute path, but does NOT resolve symlinks
    # os.path.realpath will first resolve any symbolic links in the path, and then return the absolute path.
    # both abspath and realpath imply os.path.normpath
    # neither abspath or realpath will resolve ~ to the user's home directory
    # abspath and realpath: if fullpath provided, simply return fullpath. if not, resolved relative to pwd
    return os.path.abspath(os.path.expanduser(path))
fp = fullpath

def csd():
    """(),Returns full path of current script directory, i.e. the directory where the running script is.
    if in interactive mode, return current working directory
    It should always be the best to call csd() at the top of a script, 
    during which the running script has not change any working directory yet. 
    Therefore the internal call of sys.argv[0], if given not in full path, can be resolved to correct full path
    """
    # https://stackoverflow.com/a/22424821/2292993
    import __main__ as main
    is_interactive = not hasattr(main, '__file__')
    if is_interactive:
        return os.getcwd()
    else:
        # for difference between __file__ and sys.argv[0]
        # see https://stackoverflow.com/questions/5851588/difference-between-file-and-sys-argv0
        # os.path.split returns (head,tail), here for path = , same effect as splitpath
        path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        # hack when a script is packed into an app, which returns xxx.app/Contents/Resources
        return os.path.abspath(os.path.join(path,os.pardir,os.pardir,os.pardir)) if path.endswith('.app/Contents/Resources') else path

def stepfolder(step=-1):
    """
    folder = stepfolder(step)
    step: regex of folder, eg '01', if multiple match, return only the first matched
          integer -1 (default, backward) +2 (forward) 2 (same as +2)
    folder: target folder path
    Usage:
          Under a projFolder, there might be 01Original, 02Slicing, 03Motion...
          Use this function to go to a specific "step folder"
    """
    import __main__ as main
    is_interactive = not hasattr(main, '__file__')
    if is_interactive:
        theCSD = os.getcwd()
    else:
        path = splitpath(os.path.abspath(sys.argv[0]))[0]
        # hack when a script is packed into an app, which returns xxx.app/Contents/Resources
        theCSD = os.path.abspath(os.path.join(path,os.pardir,os.pardir,os.pardir)) if path.endswith('.app/Contents/Resources') else path
    projFolder = parentdir(theCSD)
    if isinstance(step,str):
        folder = lsd(projFolder,step)
        folder = folder[0]
        folder = joinpath(projFolder,folder)
    elif isinstance(step,int):
        steps = lsd(projFolder,'^\d\d')  # a list of all folders like 01Original, 06Set
        currentStep = splitpath(theCSD)[1]
        try:
            currentStepNum = steps.index(currentStep)
            targetStep = steps[currentStepNum+step]
        except:
            targetStep = currentStep
        folder = joinpath(projFolder,targetStep)
    return folder

def csf():
    """(),Returns current script file name without ext, i.e. the name of the running script without ext.
    different from csd(), even if working directory changes, csf() still return correct sys.argv[0]
    """
    import __main__ as main
    is_interactive = not hasattr(main, '__file__')
    if is_interactive:
        path = os.getcwd()
    else:
        # os.path.split returns (head, tail)
        file = os.path.split(os.path.abspath(sys.argv[0]))[1]
    return file

def parentdir(path):
    """parentdir(path), Returns the parent directory of a path."""
    path = fullpath(path)
    dir = os.path.dirname(path)
    ext = os.path.splitext(path)[1]
    file = os.path.basename(path)[0:-len(ext)] if len(ext) != 0 else os.path.basename(path)
    # if isfile
    if len(ext) != 0:
        return os.path.abspath(os.path.join(os.path.abspath(os.path.join(path, os.pardir)), os.pardir))
    else:
        return os.path.abspath(os.path.join(path, os.pardir))
pr = parentdir

def joinpath(*args):
    """joinpath(path1[, path2[, ...]])   # Returns the joined path. Supports vectorization.
    """
    vectorization = False
    # to see whether there is an list/tuple input
    for arg in args:
        if type(arg) in [list, tuple]:
            vectorization = True
            length = len(arg)
            break
    if vectorization:
        # fill arg which is a string
        # args is by default an unmutable tuple
        args = list(args)
        for j in range(0,len(args)):
            arg = args[j]
            if type(arg) in [str]:
                args[j] = [arg]*length

        results = []
        for i in range(0,length):
            result = ''
            for j in range(0,len(args)):
                result = os.path.join(result, args[j][i])
            results.append(result)
        return results
    else:
        return os.path.join(*args)
jp = joinpath

def splitpath(path):
    """splitpath(path), Split path into [dir, file, ext]. e.g., file=easyshell, ext=.py
    Supports vectorization."""

    # os.path.split only returns (head, tail), so do not use

    # vectorization
    if type(path) in [list, tuple]:
        dirs = []; files = []; exts = []
        for p in path:
            [dir, file, ext] = splitpath(p)
            dirs.append(dir); files.append(file); exts.append(ext)
        return [dirs, files, exts]

    path = fullpath(path)
    dir = os.path.dirname(path)
    ext = os.path.splitext(path)[1]
    file = os.path.basename(path)[0:-len(ext)] if len(ext) != 0 else os.path.basename(path)
    return [dir, file, ext]
sp = splitpath

def trim(s, how=4, *args):
    """Merge multiple spaces to single space in the middle, and remove trailing/leading spaces
    trim(s, how=4 [,chars])
        s: a string 
        how: a num 1=left only; 
                   2=right only; 
                   3=left and right; 
                   4 (default)=left and right and merge middle
        chars: if not given (default), space, horizontal tab, line feed, carriage return
               if given and not None, remove characters in chars instead
    eg, "Hi        buddy        what's up    Bro"  --> "Hi buddy what's up bro"
        trim(s,4,'\nx')
        " Hi        buddy        what's up    Bro\nx" --> " Hi        buddy        what's up    Bro"
    """
    if (how==1):
        s = str.lstrip(s,*args)
    elif (how==2):
        s = str.rstrip(s,*args)
    elif (how==3):
        s = str.strip(s,*args)
    elif (how==4):
        chars = args[0]
        if chars==' ': chars='\s'
        expression = '(?<=[(%s)])(%s)*|^(%s)+|(%s)+$' % (chars,chars,chars,chars)
        # http://stackoverflow.com/a/25734388/2292993
        s = re.sub(expression, "", s, count=0)
    return(s)

def join(sep='',*args):
    """glue together strings/array with sep
    1) join('','string1','string2',...)
    2) Input only supports vectorization
            join('|',['string1','string2'],['string3','string4'],...) -> [string1|string3,string2|string4]
    3) numeric/mixed array works too (the built-in '.'.join() only supports string array)
            join(',',['this','is',1,'array'])
            join('_',[1,2,2]) >> 1_2_2
    """
    # len(args) only refers to *args itself
    # in the case of (sep), len(args) == 0
    assert len(args) >= 1, "Give me more inputs"
    if len(args) == 1:
        theList = args[0]
        theList = [str(x) for x in theList]
        return sep.join(theList)
    else:        
        vectorization = False
        # to see whether there is an list/tuple input
        for arg in args:
            if type(arg) in [list, tuple]:
                vectorization = True
                length = len(arg)
                break
        if vectorization:
            # fill arg which is a string
            # args is by default an unmutable tuple
            args = list(args)
            for j in range(0,len(args)):
                arg = args[j]
                if type(arg) in [str]:
                    args[j] = [arg]*length
    
            results = []
            for i in range(0,length):
                # a bit tricy because of result + = result and .join
                result = args[0][i]
                for j in range(1,len(args)):
                    result = sep.join([result, args[j][i]])
                results.append(result)
            return results
        else:
            return sep.join(args)

def replace(theList, theItem, replacement):
    """replace(theList, theItem, replacement)
    replace all occurance of theItem in theList with replacement
    theItem could be a value, e.g., 3, 'cat' or a condition '>3' '!="cat"' or a (lambda) function
    supports numeric list, string list, or mixed
    Be careful when theItem is condition and theList is mixed (e.g., 'cat'>3 is true)
    
    Returns the changed list but the passed-in list is NOT changed.
    
    e.g., 
    replace([0,-1,1],'<0',0)
    replace([0,-1,1],-1,0)
    replace([0,-1,1],'!=0',0)
    replace([0,-1,1],'-1',1)   # <-- will not replace, because -1 and '-1' not the same
    replace(['c','a','t','cat'],'!="cat"','cat')  #<--notice the quotes around "cat", otherwise report error
    replace([0,-1,1],lambda x: x<0,0)
    """
    # http://www.python-course.eu/deep_copy.php
    from copy import deepcopy
    theList = deepcopy(theList)
    # check if it is a function
    # http://stackoverflow.com/questions/624926/how-to-detect-whether-a-python-variable-is-a-function
    # http://stackoverflow.com/questions/3655842/how-to-test-whether-a-variable-holds-a-lambda
    # http://www.diveintopython.net/power_of_introspection/lambda_functions.html
    if hasattr(theItem,'__call__'):
        for index, item in enumerate(theList):
            if theItem(item):   # pass item to the function
                theList[index] = replacement
    else:
        if type(theItem) not in [str]:
            cnd = ' == theItem'
        else:
            if theItem[0] in ['<','=','!','>']:   # startswith
                cnd = theItem
            else:
                cnd = ' == theItem'
        for index, item in enumerate(theList):
            if eval('item' + cnd):
                theList[index] = replacement
    return theList

def remove(theList, theItem):
    """remove(theList, theItem)
    remove all occurance of theItem in theList
    theItem could be a value, e.g., 3, 'cat' or a condition '>3' '!="cat"' or a (lambda) function
    supports numeric list, string list, or mixed
    Be careful when theItem is condition and theList is mixed (e.g., 'cat'>3 is true)
    
    Returns the changed list but the passed-in list is NOT changed.
    
    e.g., 
    ([0,-1,1],'<0')
    ([0,-1,1],-1)
    ([0,-1,1],'!=0')
    ([0,-1,1],'-1')   # <-- will not remove, because -1 and '-1' not the same
    (['c','a','t','cat'],'!="cat"')  #<--notice the quotes around "cat", otherwise report error
    ([0,-1,1],lambda x: x<0)
    """
    # http://www.python-course.eu/deep_copy.php
    from copy import deepcopy
    theList = deepcopy(theList)
    # check if it is a function
    # http://stackoverflow.com/questions/624926/how-to-detect-whether-a-python-variable-is-a-function
    # http://stackoverflow.com/questions/3655842/how-to-test-whether-a-variable-holds-a-lambda
    # http://www.diveintopython.net/power_of_introspection/lambda_functions.html
    
    # list remove,pop can cause index shift
    # http://stackoverflow.com/questions/497426/deleting-multiple-elements-from-a-list    
    if hasattr(theItem,'__call__'):
        for index, item in enumerate(theList):
            if theItem(item):   # pass item to the function
                theList[index] = '!!!'
    else:
        if type(theItem) not in [str]:
            cnd = ' == theItem'
        else:
            if theItem[0] in ['<','=','!','>']:   # startswith
                cnd = theItem
            else:
                cnd = ' == theItem'
        for index, item in enumerate(theList):
            if eval('item' + cnd):
                theList[index] = '!!!'
    
    for i in range(0,theList.count('!!!')):
        theList.remove('!!!') # remove
    return theList
    
def sort(*args, **kwargs):
    """wrapper of sorted, passed in list does not change, returns a sorted list"""
    return sorted(*args, **kwargs)

def cd(path):
    """cd(path), Changes to a new directory."""
    path = fullpath(path)
    os.chdir(path)
    print "Start working in " + os.getcwd()

def ls(path="./", regex=".*", full=True, dotfile=False, sort=True):
    """ls([path[, regex]], full=True, dotfile=False, sort=True)    # Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
    """
    def _FilterList(list, pattern_regex):
        # match_pattern = re.compile(pattern_regex, re.IGNORECASE).search
        match_pattern = re.compile(pattern_regex).search
        return filter(match_pattern, list)
    def _ListingParse(path="./", pattern_regex=".*"):
        # ls() or ls('homebrew'), ls("homebrew", "\.py$")
        if os.path.isdir(path):
            path = path
            pattern_regex = pattern_regex
        # ls('*.py'), ls('homebrew/*.py')
        else:
            path, pattern = os.path.split(path)
            pattern_regex = fnmatch.translate(pattern)
        return path, pattern_regex

    path = fullpath(path)
    pattern_regex = regex
    path, pattern_regex = _ListingParse(path, pattern_regex)

    files = _FilterList(os.listdir(path), pattern_regex)
    if not dotfile: files = _FilterList(files,'^[^\.]')
    if full: files = [os.path.join(path,file) for file in files]
    result = [file for file in files if os.path.isfile(file)]
    if sort: 
        return sorted(result)
    else:
        return result

def lsd(path="./", regex=".*", full=False, dotfolder=False, sort=True):
    """lsd([path[, regex]], full=False, dotfolder=False, sort=True), Returns a list of all (including hidden) folders with their (optionally) full paths in path, filtered by regular expression."""
    def _FilterList(list, pattern_regex):
        # match_pattern = re.compile(pattern_regex, re.IGNORECASE).search
        match_pattern = re.compile(pattern_regex).search
        return filter(match_pattern, list)
    def _ListingParse(path="./", pattern_regex=".*"):
        # ls() or ls('homebrew'), ls("homebrew", "\.py$")
        if os.path.isdir(path):
            path = path
            pattern_regex = pattern_regex
        # ls('*.py'), ls('homebrew/*.py')
        else:
            path, pattern = os.path.split(path)
            pattern_regex = fnmatch.translate(pattern)
        return path, pattern_regex

    path = fullpath(path)
    pattern_regex = regex
    path, pattern_regex = _ListingParse(path, pattern_regex)

    # os.listdir() bug on Redhat (maybe all linux) personally came across on Mon, Feb 05 2018
    # os.listdir() also list files if the dir is not working directory
    # so change working directory and change back
    olddir = os.getcwd()
    os.chdir(path)
    files = _FilterList(os.listdir(path), pattern_regex)
    if not dotfolder: files = _FilterList(files,'^[^\.]')
    if full: files = [os.path.join(path,file) for file in files]
    result = [file for file in files if not os.path.isfile(file)]
    os.chdir(olddir)
    if sort: 
        return sorted(result)
    else:
        return result

def fls(path="./", regex=".*", dotf=False, sort=True):
    """fls([path[, regex=".*", dotf=False], sort=True])   # Returns a list of files with their full paths in flattened path (i.e. walk each subdirectory).
    """
    def _FilterList(list, pattern_regex):
        # match_pattern = re.compile(pattern_regex, re.IGNORECASE).search
        match_pattern = re.compile(pattern_regex).search
        return filter(match_pattern, list)
    def _ListingParse(path="./", pattern_regex=".*"):
        # ls() or ls('homebrew'), ls("homebrew", "\.py$")
        if os.path.isdir(path):
            path = path
            pattern_regex = pattern_regex
        # ls('*.py'), ls('homebrew/*.py')
        else:
            path, pattern = os.path.split(path)
            pattern_regex = fnmatch.translate(pattern)
        return path, pattern_regex

    path = fullpath(path)
    pattern_regex = regex
    path, pattern_regex = _ListingParse(path, pattern_regex)

    flatFiles = []
    for root, dirs, files in os.walk(path):
        # skip any folder whose name starts with . and its any subfolders
        if not dotf:
            # operationally, check if the path root has /.folder
            parts = root.split(os.sep)
            dotfolders = [part for part in parts if len(part)>=2 and part.startswith('.') and part!='..']
            if len(dotfolders)>0: continue

        filteredFiles = _FilterList(files, pattern_regex)
        if not dotf: filteredFiles = _FilterList(filteredFiles,'^[^\.]')
        ## If there is matched
        if filteredFiles:
            for file in filteredFiles:
                fileFullName = os.path.join(root, file)
                flatFiles.append(fileFullName)
    result = flatFiles
    if sort: 
        return sorted(result)
    else:
        return result

def mkdir(path):
    """mkdir("path/to/a/directory") , Makes a directory (also any one of the "path", "to", "a" directories if not exits)."""
    path = fullpath(path)
    if not os.path.exists(path):
        os.makedirs(path)
        print "Created: " + path

def exists(path):
    """Returns the existence of path (0 or 1, supports wildcards such as "../homebrew/*.pyc" but not regular expression)."""
    path = fullpath(path)
    paths = glob.glob(path)
    return True if paths else False

def rn(*args):
    """Rename a file or folder.
    rn(old, new)
    to parent folder must exist already; otherwise error
    old and new cannot be the same, otherwise error
    note: input could be a list/tuple, vectorization supported
    in case new name exists
          if old and new both folders, move old to new as subfolder
          if old and new both files, overwrite the new file with old file without prompt
    rn('a','b')-->rename folder a to folder b
    """
    vectorization = False
    # to see whether there is an list/tuple input
    for arg in args:
        if type(arg) in [list, tuple]:
            vectorization = True
            length = len(arg)
            break
    if vectorization:
        # fill arg which is a string
        # args is by default an unmutable tuple
        args = list(args)
        for j in range(0,len(args)):
            arg = args[j]
            if type(arg) in [str]:
                args[j] = [arg]*length

        for i in range(0,length):
            rn(args[0][i],args[1][i])
        return

    source = fullpath(args[0])
    destination = fullpath(args[1])
    if source == destination: raise Exception('Cannot rename to the same name')

    ext = os.path.splitext(destination)[1]
    # if destination dirlike
    if ext == '':
        # if destination dir exist
        if os.path.isdir(destination):
            # raise Exception('Cannot rename to exising folder name')
            mv(source,destination)
        else:
            os.rename(source,destination)
    else:
        if not os.path.isdir(os.path.dirname(destination)):
            raise Exception('Destination parent folder does not exist')
        else:
            os.rename(source,destination)

    # if os.path.isfile(source):
    #     os.rename(source, destination)
    #     print "Renamed file: " + "->".join([source, destination])
    # elif os.path.isdir(source):
    #     os.rename(source, destination)
    #     print "Renamed folder: " + "->".join([source, destination])
    # else:
    #     print source + " not renamed to " + destination

def rm(path):
    """Deletes a file or folder.
    rm(path)
    removes a folder recursively or a file; file supports wildcards
    if a path does not exist, nothing happens.
    note: input could be a list/tuple, vectorization supported
    """
    # vectorization
    if type(path) in [list,tuple]:
        for p in path:
            rm(p)
        return

    if not path: return  # rm('')
    path = fullpath(path)
    paths = glob.glob(path)
    if not paths: return # wildcard found nothing to remove

    for path in paths:
        if os.path.isfile(path):
            os.remove(path)
            # print "Removed file: " + path
        elif os.path.isdir(path):
            shutil.rmtree(path)
            # print "Removed folder: " + path
        # else:
            # print path + " not removed"

def cp(source, destination, ignores=None, debugMode=False):
    """
    Copies a source file or folder to destination.
    accepts ignore, which is a list of ignore_patterns, supports wildcards (not regex)
    e.g. ['*.pyc', 'tmp*']
    This will copy everything except .pyc files and files or directories whose name starts with tmp.
    other examples ['*.py', '*.sh', 'specificfile.file'],       ['.git*'],      ['.*']

    support vectorization
    destination folder does not have to exist already
    e.g.,
    1) both works cp('a.txt','folder'), cp('a.txt','folder/b.txt')
    the former copy still has the same name 'a.txt', the latter copy new name 'b.txt'
    also cp(['a.txt','b.txt']),'folder')
    2) folder: cp('a','b')-->if b not exists, cp contents of a to b; if b exist, a becomes subfolder of b
    kinda combines rn and mv
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False

    vectorization = False
    for arg in [source,destination]:
        if type(arg) in [list, tuple]:
            vectorization = True
            length = len(arg)
            break
    if vectorization:
        args = [source,destination]
        for j in range(0,len(args)):
            arg = args[j]
            if type(arg) in [str]:
                args[j] = [arg]*length

        for i in range(0,length):
            cp(args[0][i],args[1][i],ignores=ignores)
        return

    if (not source) or (not destination): return  # cp('','')
    source = fullpath(source)
    destination = fullpath(destination)
    sources = glob.glob(source)
    if not sources: return  # wildcard found nothing to copy

    for source in sources:
        if os.path.isfile(source):
            if not debug_mode_in_effect:
                # prepare destination dir if not exist
                ext = os.path.splitext(destination)[1]
                # if destination dirlike
                if ext == '':
                    # if destination dir not exist
                    if not os.path.isdir(destination):
                        os.makedirs(destination)
                else:
                    destDir = os.path.dirname(destination)
                    if not os.path.isdir(destDir):
                        os.makedirs(destDir)

                shutil.copy(source, destination)
                # print "Copied file: " + "->".join([source, destination])
            else:
                pprint("Simulation! Copied file: " + "->".join([source, destination]), 'yellow')
        elif os.path.isdir(source):
            if not debug_mode_in_effect:
                # if destination dir not exist, shutil.copytree will auto create
                # shutil.copytree will raise error if destination dir exists
                if os.path.isdir(destination):
                    destination = os.path.join(destination,os.path.basename(source))
                if ignores:
                    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*ignores))
                else:
                    shutil.copytree(source, destination)
                # print "Copied folder: " + "->".join([source, destination])
            else:
                pprint("Simulation! Copied folder: " + "->".join([source, destination]), 'yellow')
        # else:
        #     print source + " not copied to " + destination

def mv(source, destination, debugMode=False):
    """Moves a source file or folder to destination.
    support vectorization
    destination parent folder does not have to exist already
    mv('a.txt','folder'), mv('a.txt','folder/a.txt'), mv('a.txt','folder/b.txt')
    mv('a','b')-->get b/a, b now has a as subfolder, regardless of b exists or not
                  use ez.rn('a','b') to change name a->b
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False

    vectorization = False
    for arg in [source,destination]:
        if type(arg) in [list, tuple]:
            vectorization = True
            length = len(arg)
            break
    if vectorization:
        args = [source,destination]
        for j in range(0,len(args)):
            arg = args[j]
            if type(arg) in [str]:
                args[j] = [arg]*length

        for i in range(0,length):
            mv(args[0][i],args[1][i])
        return

    if (not source) or (not destination): return  # mv('','')
    source = fullpath(source)
    destination = fullpath(destination)
    sources = glob.glob(source)
    if not sources: return  # wildcard found nothing to copy

    # prepare destination dir if not exist
    ext = os.path.splitext(destination)[1]
    # if destination dirlike
    if ext == '':
        # if destination dir not exist
        if not os.path.isdir(destination):
            os.makedirs(destination)
    else:
        destDir = os.path.dirname(destination)
        if not os.path.isdir(destDir):
            os.makedirs(destDir)

    for source in sources:
        if not debug_mode_in_effect:
            shutil.move(source, destination)
            # print "Moved: " + "->".join([source, destination])
        elif debug_mode_in_effect:
            pprint("Simulation! Moved: " + "->".join([source, destination]), 'yellow')
        # else:
        #     print source + " not moved to " + destination

def lns(source, destination):
    """Creates a soft link / symbolic link /shortcut."""
    source = fullpath(source)
    destination = fullpath(destination)

    os.symlink(source, destination)
    print "Symbolic link: " + "->".join([source, destination])

def execute2(cmd, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', debugMode=False, *args, **kwargs):
    """Executes a bash command. can capture output
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging) or simulation
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    shell: 'bash', 'tcsh', 'sh' (internally converted to '/bin/'+shell)
    return: ...regardless of verbose...
            returns shell output as a list with each elment is a line of string (whitespace stripped both sides) from output
            if error occurs, return None, also always print out the error message to screen
            if no output or all empty output, return [] 
               note execute2('printf "\n\n"')-->[]; but execute2('printf "\n\n3"')-->['', '', '3']
    note: if use this function interactively, one can return _ = execute2() to a dummy variable
          alternatively, in ipython, execute2(); (add semicolon) to suppress the returned contents
          or use execute(), which does not return the output to a python variable
          seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    if not debug_mode_in_effect:
        if verbose in [1,3]: pprint("Command: " + cmd + "\n> > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > ")

        # https://askubuntu.com/a/731237
        if redirect:
            if redirectMode == 'a':
                if shell in ['tcsh']:
                    # cmdSuffix = ' |& tee -a "' + redirect + '"'
                    cmdSuffix = ' 2>&1 | tee -a "' + redirect + '"'
                else:
                    cmdSuffix = ' 2>&1 | tee -a "' + redirect + '"'
            else:
                if shell in ['tcsh']:
                    # cmdSuffix = ' |& tee "' + redirect + '"'
                    cmdSuffix = ' 2>&1 | tee "' + redirect + '"'
                else:
                    cmdSuffix = ' 2>&1 | tee "' + redirect + '"'
        else:
            cmdSuffix = ''

        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            subprocess.call('chmod +x '+save, shell=True)
            print('\nCommand saved at '+save+'\n')

        # https://stackoverflow.com/a/40139101/2292993
        def _execute_cmd(cmd):
            if os.name == 'nt' or platform.system() == 'Windows':
                # set stdin, out, err all to PIPE to get results (other than None) after run the Popen() instance
                # shell=True can do shell pipes, filename wildcards, environment variable expansion, and expansion of ~
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            else:
                # tcsh -xef 
                # -x : echo commands to terminal before executing them
                # -e : terminate script when encountering any error
                # -f : do not process user's ~/.cshrc file
                # for subprocess(), if cmd is a string, set shell=True; if a list, set shell=False
                # also, The executable argument specifies a replacement program to execute. It is very seldom needed. 
                # If shell=True, on Unix the executable argument specifies a replacement shell for the default /bin/sh
                # this shell is not effected by the actual shell terminal used when execute python
                # when using executable, i.e., subprocess.Popen(executable="/bin/"+shell), you cannot pass arg to it. that's why I use prefix+cmd to implement tcsh -xef
                # p = subprocess.Popen('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' -c "'+cmd+'"'+cmdSuffix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                # well, -c seems not to be able to handle $var: eg, error for /bin/bash -c "x=33333333333333; echo $x"
                # another issue with -c is sometimes "Argument list too long" "getconf ARG_MAX"
                # save the command to a temp file, then execute
                # the temp file solution can bypass both above issues
                import tempfile
                tmpfd, tmpPath = tempfile.mkstemp(suffix='.sh')
                with os.fdopen(tmpfd, 'w') as tmp:
                    tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
                p = subprocess.Popen('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' "'+tmpPath+'"'+cmdSuffix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable="/bin/bash")
            # the Popen() instance starts running once instantiated (??)
            # additionally, communicate(), or poll() and wait process to terminate
            # communicate() accepts optional input as stdin to the pipe (requires setting stdin=subprocess.PIPE above), return out, err as tuple
            # if communicate(), the results are buffered in memory
            
            # Read stdout from subprocess until the buffer is empty !
            # if error occurs, the stdout is '', which means the below loop is essentially skipped
            # A prefix of 'b' or 'B' is ignored in Python 2; 
            # it indicates that the literal should become a bytes literal in Python 3 
            # (e.g. when code is automatically converted with 2to3).
            # return iter(p.stdout.readline, b'')
            for line in iter(p.stdout.readline, b''):
                # # Windows has \r\n, Unix has \n, Old mac has \r
                # if line not in ['','\n','\r','\r\n']: # Don't print blank lines
                    yield line
            while p.poll() is None:                                                                                                                                        
                sleep(.1) #Don't waste CPU-cycles
            # Empty STDERR buffer
            err = p.stderr.read()
            if p.returncode != 0:
                # responsible for logging STDERR 
                if verbose in [2,3]: print "Error: " + str(err)
                yield None
            # delete temp file
            os.remove(tmpPath)

        out = []
        for line in _execute_cmd(cmd):
            # error did not occur earlier
            if line is not None:
                # trailing comma to avoid a newline (by print itself) being printed
                if verbose in [2,3]: print line,
                out.append(line.strip())
            else:
                # error occured earlier
                out = None

        # post-process for returning value
        if out is None:
            return None
        else:
            # https://stackoverflow.com/a/3845453/2292993
            # filter() check if one or all empty string
            if len(out)==0 or len(filter(None,out))==0:
                return []
            else:
                return out
    else:
        pprint("Simulation! Execute command: " + cmd + "\n< < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < ", 'yellow')
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            subprocess.call('chmod +x '+save, shell=True)
            print('\nCommand saved at '+save+'\n')
        return None

def execute1(cmd, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', debugMode=False, *args, **kwargs):
    """
    a wrapper of execute2(), but does not return the output to a python variable, discard captures
    execute, esp (subprocess.call) seem to work better with AFNI commands, while execute1/2, esp1/2 (based on subprocess.Popen) sometimes fail
    Executes a bash command.
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    execute2(cmd, verbose=verbose, save=save, saveMode=saveMode, redirect=redirect, redirectMode=redirectMode, shell=shell, debugMode=debug_mode_in_effect, *args, **kwargs)

def esp2(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', skipdollar=0, debugMode=False, *args, **kwargs):
    """
    Execute a SPrintf, can capture output
    a shortcut for execute2(sprintf(cmdString))
    return: ...regardless of verbose...
        returns shell output as a list with each elment is a line of string (whitespace stripped both sides) from output
        if error occurs, return None, also always print out the error message to screen
        if no output or all empty output, return [] 
           note execute2('printf "\n\n"')-->[]; but execute2('printf "\n\n3"')-->['', '', '3']
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example:
            var_to_be_in_bash = 'blabla'
            cmd = '''
echo $var_to_be_in_bash
echo "new line"
'''
            ez.esp(cmd)
            # Command: echo blabla
            # Actual output: blabla    
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    # # caller's caller
    # caller = inspect.currentframe().f_back.f_back
    import inspect
    caller = inspect.currentframe().f_back
    # for esp1()
    if kwargs: 
        if kwargs['insideCalling']:
            caller = inspect.currentframe().f_back.f_back
    cmd = sprintf(cmdString, caller.f_locals, skipdollar=skipdollar)
    return execute2(cmd, verbose=verbose, save=save, saveMode=saveMode, redirect=redirect, redirectMode=redirectMode, shell=shell, debugMode=debug_mode_in_effect, *args, **kwargs)

def esp1(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', skipdollar=0, debugMode=False, *args, **kwargs):
    """
    Execute a SPrintf, but does not return the output to a python variable, discard captured
    a shortcut for execute2(sprintf(cmdString)) without return
    execute, esp (subprocess.call) seem to work better with AFNI commands, while execute1/2, esp1/2 (based on subprocess.Popen) sometimes fail
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example:
            var_to_be_in_bash = 'blabla'
            cmd = '''
echo $var_to_be_in_bash
echo "new line"
'''
            ez.esp(cmd)
            # Command: echo blabla
            # Actual output: blabla
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    esp2(cmdString, verbose=verbose, save=save, saveMode=saveMode, redirect=redirect, redirectMode=redirectMode, shell=shell, skipdollar=skipdollar, debugMode=debug_mode_in_effect, insideCalling=True)

def espR2(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', skipdollar=1, debugMode=False, *args, **kwargs):
    """
    a shortcut for execute2(sprintf(cmdString)), can capture output
    write cmdString (R codes) to a temp file, then call "Rscript temp.R", finally remove the temp file
    Execute a SPrintf    
    return: ...regardless of verbose...
        returns shell output as a list with each elment is a line of string (whitespace stripped both sides) from output
        if error occurs, return None, also always print out the error message to screen
        if no output or all empty output, return [] 
           note execute2('printf "\n\n"')-->[]; but execute2('printf "\n\n3"')-->['', '', '3']
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging) or simulation
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example: 
            ez.espR('iris$Species')
            # print out iris$Species, Levels: setosa versicolor virginica    
    """
    # # caller's caller
    # caller = inspect.currentframe().f_back.f_back
    import inspect
    caller = inspect.currentframe().f_back
    # for esp()
    if kwargs: 
        if kwargs['insideCalling']:
            caller = inspect.currentframe().f_back.f_back
    cmd = sprintf(cmdString,caller.f_locals,skipdollar=skipdollar)
    
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    
    if not debug_mode_in_effect:
        # save R source code
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            print('\nCommand saved at '+save+'\n')
        
        import tempfile
        # create temp file with specified suffix
        fd, path = tempfile.mkstemp(suffix='.R')
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            # not save this command line
            result = execute2('Rscript --no-save --no-restore ' + path, verbose=verbose, save=None, saveMode='a', redirect=redirect, redirectMode=redirectMode, shell=shell, debugMode=debug_mode_in_effect, *args, **kwargs)
        # delete it when it is done (can still delete after return)
        # A finally clause is always executed before leaving the try statement, whether an exception has occurred or not. 
        finally:
            os.remove(path)
        return result
    else:
        pprint("Simulation! Execute command: " + cmd + "\n< < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < ", 'yellow')
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            print('\nCommand saved at '+save+'\n')
        return None

def espR1(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', skipdollar=1, debugMode=False, *args, **kwargs):
    """
    a shortcut for execute2(sprintf(cmdString)) without return, dsicard captured
    write cmdString (R codes) to a temp file, then call "Rscript temp.R", finally remove the temp file
    Execute a SPrintf, but does not return the output to a python variable
    cmdString: R codes
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example: 
            ez.espR('iris$Species')
            # print out iris$Species, Levels: setosa versicolor virginica
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    espR2(cmdString, verbose=verbose, save=save, saveMode=saveMode, redirect=redirect, redirectMode=redirectMode, skipdollar=skipdollar, debugMode=debug_mode_in_effect, insideCalling=True)

def execute(cmd, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', debugMode=False, *args, **kwargs):
    """
    a wrapper of subprocess.call, cannot capture output, does not return the output to a python variable
    execute, esp (subprocess.call) seem to work better with AFNI commands, while execute1/2, esp1/2 (based on subprocess.Popen) sometimes fail
    Executes a shell command.
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False

    if not debug_mode_in_effect:
        if verbose in [1,3]: pprint("Command: " + cmd + "\n> > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > ")
        if verbose in [0,1]: 
            output=False
        else:
            output=True

        # https://askubuntu.com/a/731237
        if redirect:
            if redirectMode == 'a':
                if shell in ['tcsh']:
                    # cmdSuffix = ' |& tee -a "' + redirect + '"'
                    cmdSuffix = ' 2>&1 | tee -a "' + redirect + '"'
                else:
                    cmdSuffix = ' 2>&1 | tee -a "' + redirect + '"'
            else:
                if shell in ['tcsh']:
                    # cmdSuffix = ' |& tee "' + redirect + '"'
                    cmdSuffix = ' 2>&1 | tee "' + redirect + '"'
                else:
                    cmdSuffix = ' 2>&1 | tee "' + redirect + '"'
        else:
            cmdSuffix = ''

        # save cmd
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            subprocess.call('chmod +x '+save, shell=True)
            print('\nCommand saved at '+save+'\n')

        if os.name == 'nt' or platform.system() == 'Windows':
            if output:
                subprocess.call(cmd, shell=True)
            else:
                subprocess.call(cmd, shell=True, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        else:
            if output:
                # subprocess.call('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' -c "'+cmd+'"'+cmdSuffix, shell=True, executable="/bin/bash") 
                import tempfile
                tmpfd, tmpPath = tempfile.mkstemp(suffix='.sh')
                try:
                    with os.fdopen(tmpfd, 'w') as tmp:
                        tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
                    subprocess.call('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' "'+tmpPath+'"'+cmdSuffix, shell=True, executable="/bin/bash")
                finally:
                    os.remove(tmpPath)
            else:
                # subprocess.call('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' -c "'+cmd+'"'+cmdSuffix, shell=True, executable="/bin/bash", stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
                import tempfile
                tmpfd, tmpPath = tempfile.mkstemp(suffix='.sh')
                try:
                    with os.fdopen(tmpfd, 'w') as tmp:
                        tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
                    subprocess.call('/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+' "'+tmpPath+'"'+cmdSuffix, shell=True, executable="/bin/bash", stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
                finally:
                    os.remove(tmpPath)
        print ""

    else:
        pprint("Simulation! Execute command: " + cmd + "\n< < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < ", 'yellow')
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/'+('tcsh -xef' if shell in ['tcsh'] else shell)+'\n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            subprocess.call('chmod +x '+save, shell=True)
            print('\nCommand saved at '+save+'\n')

def esp(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', skipdollar=0, debugMode=False, *args, **kwargs):
    """
    a shortcut for execute(sprintf(cmdString)), cannot capture output
    Execute a SPrintf, but does not return the output to a python variable
    execute, esp (subprocess.call) seem to work better with AFNI commands, while execute1/2, esp1/2 (based on subprocess.Popen) sometimes fail
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example:
            var_to_be_in_bash = 'blabla'
            cmd = '''
echo $var_to_be_in_bash
echo "new line"
'''
            ez.esp(cmd)
            # Command: echo blabla
            # Actual output: blabla
    """
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    # # caller's caller
    # caller = inspect.currentframe().f_back.f_back
    import inspect
    caller = inspect.currentframe().f_back
    cmd = sprintf(cmdString, caller.f_locals, skipdollar=skipdollar)
    execute(cmd, verbose=verbose, save=save, saveMode=saveMode, redirect=redirect, redirectMode=redirectMode, shell=shell, debugMode=debug_mode_in_effect, *args, **kwargs)

def espR(cmdString, verbose=3, save=None, saveMode='a', redirect=None, redirectMode='a', shell='bash', skipdollar=1, debugMode=False, *args, **kwargs):
    """
    a shortcut for execute(sprintf(cmdString)), cannot capture output
    write cmdString (R codes) to a temp file, then call "Rscript temp.R", finally remove the temp file
    Execute a SPrintf, but does not return the output to a python variable
    cmdString: R codes
    verbose: any screen display here does not affect returned values
            0 = nothing to display
            1 = only the actual command
            2 = only the command output
            3 = both the command itself and output
    save: None, or a file path to save the cmd (shebang prepended), can still save even if error occurs (for debugging)
    saveMode: 'a' (append) or 'w' (overwrite), ignored if save=None.
    redirect: None, or a file path to save the redirected cmd execution output. compatible with logon(); works also cmd itself has redirection (eg, tee)
    redirectMode: 'a' (append) or 'w' (overwrite), ignored if redirect=None.
    if skipdollar=1 (1/0), $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    note: seems to recognize execute('echo $PATH'), but not alias in .bash_profile
    Example: 
            ez.espR('iris$Species')
            # print out iris$Species, Levels: setosa versicolor virginica
    """
    # # caller's caller
    # caller = inspect.currentframe().f_back.f_back
    import inspect
    caller = inspect.currentframe().f_back
    # for esp()
    if kwargs: 
        if kwargs['insideCalling']:
            caller = inspect.currentframe().f_back.f_back
    cmd = sprintf(cmdString,caller.f_locals,skipdollar=skipdollar)
    
    if debugMode:
        debug_mode_in_effect = True
    else:
        if _DEBUG_MODE:
            debug_mode_in_effect = True
        else:
            debug_mode_in_effect = False
    
    if not debug_mode_in_effect:
        # save R source code
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            print('\nCommand saved at '+save+'\n')

        import tempfile
        # create temp file with specified suffix
        fd, path = tempfile.mkstemp(suffix='.R')
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            # not save this command line
            execute('Rscript --no-save --no-restore ' + path, verbose=verbose, save=None, saveMode='a', redirect=redirect, redirectMode=redirectMode, shell=shell, debugMode=debug_mode_in_effect, *args, **kwargs)
        # delete it when it is done (can still delete after return)
        # A finally clause is always executed before leaving the try statement, whether an exception has occurred or not. 
        finally:
            os.remove(path)
    else:
        pprint("Simulation! Execute command: " + cmd + "\n< < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < < ", 'yellow')
        if saveMode=='w': rm(save)
        if save:
            if os.path.exists(save):
                with open(save, 'a') as tmp:
                    tmp.write(cmd.replace('"','\"').replace("'","\'")+'\n\n') 
            else:
                with open(save, 'a') as tmp:
                    tmp.write('#!/bin/Rscript \n\n'+cmd.replace('"','\"').replace("'","\'")+'\n\n')
            print('\nCommand saved at '+save+'\n')
        return None

def condorize(executables=[], submit=True, luggage=None, email=None, memory=None, disk=None, getenv=True, universe='vanilla', log='condor.log', submitfile='condor.sub',showstats=True):
    """
    specific for waisman server
    generate a condor submission/configuration file for a list of scripts

    #### example:
    condor=True
    for subj in subjects:
        src_dset = ez.jp(inputDir,subj,subj+'+orig.HEAD')
        subjDir = ez.jp(outputDir,subj)
        ez.mkdir(subjDir)
        anat_dset = ez.jp(outputDir,subj,subj+'+orig.HEAD')
        ez.cd(subjDir)

        # copy anat, just in case any changes would occur to anat (header)
        cmd = '''
    3dcopy $src_dset $subjDir/$subj+orig.HEAD
    cd $subjDir
    @SSwarper $anat_dset $subj
    '''
        ez.esp(cmd,save=ez.jp(subjDir,'zzz.'+subj+'.cmd'),saveMode='w',redirect=ez.jp(subjDir,'zzz.'+subj+'.log'),redirectMode='w',shell='tcsh',debugMode=condor)
        if condor: ez.condorize([ez.jp(subjDir,'zzz.'+subj+'.cmd')],submit=True,email='jerryzhujian9@gmail.com' if subj==subjects[-1] else None,showstats=False)

    if condor: ez.condorstats()
    if (not condor): ez.mail('jerryzhujian9@gmail.com',ez.csf() + ' at ' + ez.Moment().datetime,startTime)
    #### example end

    executables=[], list of bash, python, etc script files, full or relative path
            something generated by ez.execute
    submit=True/False, actually submit the condor job or not, regardless, always generate condor configuration file 
    luggage=None, should be a single string, eg, "file1,file2,file3", full or relative (to pwd) path. eg, 'ez.pyc'
            internally for condor syntax transfer_input_files=file1,file2,file3
            could be folder path as well (with or without trailing /, eg, /usr/path, see below)
                A directory may be specified by appending the forward slash character (/) as a trailing path separator. 
                This syntax is used for both Windows and Linux submit hosts. 

                A directory example using a trailing path separator is input_data/. 
                When a directory is specified with the trailing path separator, the contents of the directory are transferred, 
                but the directory itself is not transferred. It is as if each of the items 
                within the directory were listed in the transfer list. 

                When there is no trailing path separator, the directory is transferred, its contents are transferred, 
                and these contents are placed inside the transferred directory.
    email=None, call shell command "mail" to send out mail when condor job done (ignored if submit=False)
    showstats=True/False, show condor stats, regardless of submit=True/False
    memory=None, request_memory, unit MB, eg, 2000
    disk=None, request_disk, unit KB, eg, 6500000 (choose a size for the largest file your script might generate during processing?)
    getenv=True, If getenv is set to True, then condor_submit will copy all of the user's current shell environment variables 
           at the time of job submission into the job ClassAd.
           better to be True, so that $PATH could be copied which may affect AFNI version used
    universe='vanilla', vanilla | standard | scheduler | local | grid | java | vm | parallel | docker
    
    log='condor.log', log file is appended, for the whole list of executables, if not fullpath, relative to pwd
    submitfile='condor.sub', saved/overwritten condor file, if not fullpath, relative to pwd
    out auto saved as executable_file_name.ext.out, the same path as each executable
    err auto saved as executable_file_name.ext.err, the same path as each executable

    Further condor help:     
    watch -n 2 condor_q
    condor_q: See my current condor jobs
    condor_q -better-analyze <job_id>
    condor_status: cores being used
    condor_run: run small jobs    condor_run "echo hello"
    condor_submit: use submit files to submit jobs to vendor
    condor_rm [job number/username]: condor_rm 96231.0
    """
    luggage = 'transfer_input_files='+luggage if luggage else ''
    memory = 'request_memory='+str(memory) if memory else ''
    disk = 'request_disk='+str(disk) if disk else ''
    condor = """
universe=%s
getenv=%s
%s
%s
%s
log=%s
""" % (universe,str(getenv),luggage,memory,disk,log)

    for e in executables:
        # make executable, otherwise permission error from condor
        subprocess.call('chmod +x '+e, shell=True)
        condor = condor + """
executable=%s
output=%s.out
error=%s.err
queue
""" % (e, e, e)

    submitfile = 'condor.sub'
    with open(submitfile, 'w') as tmp:
        tmp.write(condor.replace('"','\"').replace("'","\'")+'\n\n')
    print('Condor submit file saved at '+submitfile)

    if email:
        # awk print should be single quoted (not double!)
        cmd = "(condor_submit %s; condor_wait %s; printf '%s' %s | mail -s 'Condor run complete. Scheduled on %s' %s) &" % (submitfile,log,'current parentdir: %s\n%s\n'+Moment().datetime+' (started)\n'+'%s (finished)\n'+'\n'.join(executables),"$(du -csh ../ | grep total | awk '{print $1}') \"$(condor_q | grep jobs | awk '{print $0}')\" $(date +'%Y-%m-%d_%H-%M-%S')",Moment().date,email)
    else:
        cmd = "condor_submit %s" % submitfile
    
    if submit:
        # execute(cmd)
        # https://stackoverflow.com/a/34459371/2292993
        # Use subprocess.Popen() with the close_fds=True parameter, which will allow the spawned subprocess to be detached from 
        # the Python process itself and continue running even after Python exits.
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
        pprint('Submitted: \n' + cmd,'green')
    else:
        pprint('To submit, execute: \n' + cmd,'yellow')
    if showstats: sleep(5); condorstats()

def condorstats():
    
    status = execute2('condor_status -total',0)[-1].split()
    unclaimed = '%s/%s unclaimed/total' % (status[4],status[1])
    allqueue = 'Queue (all):\t\t' + execute2('condor_q -allusers -nobatch',0)[-1]
    myqueue = 'Queue (mine):\t\t' + execute2('condor_q',0)[-1]
    
    # pprint("Some users' reports...",'blue')
    # execute('condor_userprio -most',2)
    
    pprint("\nSome condor stats...",'blue')
    print unclaimed + '\n' + allqueue + '\n' + myqueue + '\n'

from contextlib import contextmanager
@contextmanager
def nooutput():
    """Temporarily suppress stdout, stderr in a context
    with nooutput():
        print 'this is will not be printed in stdout'
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

from pprint import pprint as ppprint
def pprint(text,color='green'):
    """
    # color print to terminal (may not work on any terminal)
    (text,color='green')
    color: string, case insentive, out of black, red, green, yellow, blue, magenta, cyan, white
    """
    # http://blog.mathieu-leplatre.info/colored-output-in-console-with-python.html
    color = color.lower()
    colors = {'black':0, 'red':1, 'green':2, 'yellow':3, 'blue':4, 'magenta':5, 'cyan':6, 'white':7}
    color = colors[color]
    def _has_colors(stream):
        if not hasattr(stream, "isatty"):
            return False
        if not stream.isatty():
            return False # auto color only on TTYs
        try:
            import curses
            curses.setupterm()
            return curses.tigetnum("colors") > 2
        except:
            # guess false in case of error
            return False
    if _has_colors(sys.stdout):
        seq = "\x1b[1;%dm" % (30+color) + text + "\x1b[0m"
        sys.stdout.write(seq+'\n')
    else:
        sys.stdout.write(text+'\n')

def beep():
    """Beeps to notify user."""
    sys.stdout.write("\a")
    sys.stdout.flush()

def which(name):
    """
    name without or with package name, i.e., ez.help, help
    which(name), Prints where a module is and in which module a function is.
    which('python') returns which python is being used and version info."""
    name_no_prefix = name.split('.')[-1]
    if name_no_prefix == 'python':
        from distutils.sysconfig import get_python_lib
        print get_python_lib()
        print (sys.version)
    else:
        try:
            print sys.modules[name_no_prefix]
        except:
            for module in sys.modules.keys():
                try:
                    import inspect
                    caller = inspect.currentframe().f_back
                    if name_no_prefix in eval('dir('+ module + ')', caller.f_locals):
                        print 'function ' + name_no_prefix + '() in ' + module
                        # print sys.modules[module]
                        # print ''
                except:
                    pass

def doc(package_prefixed_name):
    """
    name with a package name, i.e., ez.help
    help(name)/doc(name) # name is a string, Prints the doc string of a module/class/function
    when write a module, add:
    __doc__ = three double quotes blabla three double quotes         <-----this is module's docstring, use explicit

    when write a function/class:
    def function(arg):
        three double quotes Returns, blabla three double quotes      <-----this is function's doctoring, use implicit
        return sth
    """
    import inspect
    caller = inspect.currentframe().f_back
    print eval(package_prefixed_name + '.__doc__', caller.f_locals)
help = doc

def ver(package_name='python'):
    """
    ver(package_name) version(package_name), see a package's version.  package_name could be 'python'
    """
    print package_name + ' version installed:'
    if package_name == 'python':
        print (sys.version)
    else:
        # https://docs.python.org/2.7/reference/simple_stmts.html#exec
        theNameSpace = {}
        exec('import ' + package_name, theNameSpace)
        print theNameSpace[package_name].__version__
version = ver

def evaluate(exp):
    """
    evaluate(exp), evaluate a statement or expression, combining python built-in eval() and exec()
    python eval() only works for expression--returns something, exec() for statement--not returns anything
    an expression:  x+1,      x = eval('x+1')
    a statement:    x = x+1   exec('x = x+1')
    """
    import inspect
    caller = inspect.currentframe().f_back
    try:
        return eval(exp,caller.f_locals)
    except SyntaxError:
        # https://docs.python.org/2.7/reference/simple_stmts.html#exec
        exec(exp,caller.f_locals)

def who(name=''):
    """
    whos(name),whos() list imported functions/packages
    """
    import inspect
    caller = inspect.currentframe().f_back
    theList = eval('dir('+ name + ')', caller.f_locals)
    theList = sorted(theList)
    theNameSpace = name if name != '' else 'Current'
    print theNameSpace + ' namespace has the following existing functions/modules:\n'
    # http://stackoverflow.com/questions/19863388/modify-print-function-for-multiple-columns-python
    def pretty_print(theList, ncols):
        columns = len(theList)//200+ncols
        lines = ("".join(s.ljust(20) for s in theList[i:i+columns-1])+theList[i:i+columns][-1] for i in range(0, len(theList), columns))
        return "\n".join(lines)
    print pretty_print(theList,4)
whos = who

# def sedawk(path, regex=".*", search=None, replace=None, recursion=True):
#     """Searches and replaces the matched content in every file with regular expression."""
#     path = fullpath(path)
#     pattern_regex = regex
#     files = fls(path, pattern_regex) if recursion else ls(path, pattern_regex)
#     for file in files:
#         with open(file, 'r') as fileHandler: content = fileHandler.read()
#         if re.search(search,content):
#             content = re.sub(search, replace, content)
#             with open(file, 'w') as fileHandler: fileHandler.write(content)
#             print "Updated " + file

def SetLog(file="log.txt", mode='a', status=True, timestamp=True):
    """
    (file="log.txt", mode='a', status=True, timestamp=True)
    alias: SetLog, setlog
    convenient shortcut: logon(), logoff()
    internally and actually, SetLog=setlog=log=logon. Feel confused? just use logon() and logoff()

    Usage:
          logging on: log("thelog.txt")
          logging off: log(status=False)  # no need to pass in the file parameter, auto recognize log file

    file: could be .csv to generate excel file, or be different to genereate multiple files
    mode: a=append; w=overwrite
    status: True  logging on, Prints output to both terminal and a file (log.txt, default name) globally
            False logging off, Prints output only to terminal
    timestamp: True/False, insert timestamp at the beginning and end in the log file

    Note, use this function carefully, because it changes the sys.stdout globally.
    """
    import sys, datetime

    class Logger(object):
        def __init__(self, file):
            self.file = file
            sys.stdout = sys.__stdout__
            print "log on with " + fullpath(self.file)
            self.terminal = sys.stdout
            self.log = open(file, mode)
            if timestamp:
                self.log.write("++++++++++log on at " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "\n")
                self.log.flush()

        def flush(self):
            self.terminal.flush()
            try:
                self.log.flush()
            except:  # in case self.log closed
                pass
            
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()

        def off(self):
            if timestamp:
                self.log.write("++++++++++log off at " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "\n")
            self.log.write('\n')
            self.log.flush()
            self.log.close()
            sys.stdout = sys.__stdout__
            print "log off with " + fullpath(self.file)

    if status:
        # restore first if it has been changed
        try:
            sys.stdout.off()
        except AttributeError:
            pass

        sys.stdout = Logger(file)
    else:
        try:
            sys.stdout.off()
        except AttributeError:
            pass
log = SetLog
setlog = SetLog

def logon(file="log.txt", mode='a', status=True, timestamp=True):
    """
    (file="log.txt", mode='a', status=True, timestamp=True)
    wrapper of log()
    logon(file="log.txt", mode='a', status=True, timestamp=True)

    Usage: logon(), logoff()

    file: could be .csv to generate excel file, or be different to genereate multiple files
    mode: a=append; w=overwrite
    status: True  logging on, Prints output to both terminal and a file (log.txt, default name) globally
            False logging off, Prints output only to terminal
    timestamp: True/False, insert timestamp at the beginning and end in the log file

    Note, use this function carefully, because it changes the sys.stdout globally.
    """
    SetLog(file=file,mode=mode,status=status,timestamp=timestamp)

def logoff():
    """
    wrapper of log()
    logon(), logoff()
    turn off the file redirection, does not accept any parameter, auto recognize log file
    """
    SetLog(status=False)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# print directory tree structure starts
# modified from http://code.activestate.com/recipes/577091/
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def tree(path='./', forest=True):
    """
    tree([path[, forest=True]) # Prints a directory tree structure. 
    forest=True (default) prints only folders, i.e., print less to show the big forest
    forest=False prints files plus folders
    """
    import sys, os
    global PRINT_FILES; PRINT_FILES = not forest
    path = os.path.abspath(os.path.expanduser(path))

    def walk(root, dirs, files, prefix=''):
        if PRINT_FILES and files:
            file_prefix = prefix + ('|' if dirs else ' ') + '   '
            for name in files:
                print(file_prefix + name)
            print(file_prefix)
        dir_prefix, walk_prefix = prefix + '+---', prefix + '|   '
        for pos, neg, name in enumerate2(dirs):
            if neg == -1:
                dir_prefix, walk_prefix = prefix + '\\---', prefix + '    '
            path = os.path.join(root, name)
            try:
                dirs, files = listdir(path)[:2]
                print(dir_prefix + name + '\t(' + str(len(files)) +  ' files)')
            except:
                print(dir_prefix + name)
            else:
                walk(path, dirs, files, walk_prefix)

    def listdir(path):
        dirs, files, links = [], [], []
        for name in os.listdir(path):
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name):
                dirs.append(name)
            elif os.path.isfile(path_name):
                files.append(name)
            elif os.path.islink(path_name):
                links.append(name)
        return dirs, files, links

    def enumerate2(sequence):
        length = len(sequence)
        for count, value in enumerate(sequence):
            yield count, count - length, value

    dirs, files = listdir(path)[:2]
    print(path)
    walk(path, dirs, files)
    if not dirs:
        print('No subfolders exist')
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# print directory tree structure ends
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def regexp(string, pattern, method='find'):
    """regexp(string, pattern, method='find'), returns starting/ending indices in two lists
    [starts, ends] = regexp('abcfffgdefff','f{3}') -->[[3,9],[5,11]]  0 based
    if not find, returns [[],[]]

    method='split'
    ('Words, words, words.','\W+') --> ['Words', 'words', 'words', '']
    if not split, returns original string

    method='match'
    text = "He was carefully disguised but captured quickly by police."
    (text, '\w+ly') --> ['carefully', 'quickly']
    if not match, returns []

    seems like always a good idea to use r'' with regular expression, eg,
    newValue=ez.regexprep(oldValue,r'^(\d{1,2})(,|.)',r'\1|',1)

    python regular expression notes:
    1) special trick:
    matching string not starting with my:     ^(?!my)\w+$

    group back reference \ 1 \ 2. (Perl is $1 $2)   
    >>> re.sub(r'(\w+) (\w+)',r'\2 \1','Joe Bob')
        'Bob Joe'

    either or 
    (img|hdr)
    note: [ab] either character a or b, only work for single character

    2) general usage:
    . one character
    ^ $  start end
    [^ ] exclude
    [] include
    * >= 0
    + >= 1
    ? 0 or 1
    {n} exact n
    {m,n} m to n
    {n,} n or more
    \d  \D = [^0-9]
    \w [a-zA-Z0-9_]  \W = [^a-zA-Z0-9_]
    \s white space, tab etc
    letters only [a-zA-Z]
    \ t \ r \ n
    """
    # re.match() checks for a match only at the beginning of the string,
    # while re.search() checks for a match anywhere in the string
    import re
    if method == 'find':
        theMatch = re.finditer(pattern, string)
        starts=[]; ends=[]
        for ind, matchObj in enumerate(theMatch):
             starts.append(matchObj.start())
             ends.append(matchObj.end()-1)
        return [starts, ends]
    elif method == 'split':
        return re.split(pattern, string)
    elif method == 'match':
        return re.findall(pattern, string)

def regexpi(string, pattern, method='find'):
    """ignore cases
    regexp(string, pattern, method='find'), returns starting/ending indices in two lists
    [starts, ends] = regexp('abcfffgdefff','f{3}') -->[[3,9],[5,11]]  0 based
    if not find, returns [[],[]]

    method='split'
    ('Words, words, words.','\W+') --> ['Words', 'words', 'words', '']
    if not split, returns original string

    method='match'
    text = "He was carefully disguised but captured quickly by police."
    (text, '\w+ly') --> ['carefully', 'quickly']
    if not match, returns []

    seems like always a good idea to use r'' with regular expression, eg,
    newValue=ez.regexprep(oldValue,r'^(\d{1,2})(,|.)',r'\1|',1)

    python regular expression notes:
    1) special trick:
    matching string not starting with my:     ^(?!my)\w+$

    group back reference \1 \2. (Perl is $1 $2)   
    >>> re.sub(r'(\w+) (\w+)',r'\2 \1','Joe Bob')
        'Bob Joe'

    either or 
    (img|hdr)
    note: [ab] either character a or b, only work for single character

    2) general usage:
    . one character
    ^ $  start end
    [^ ] exclude
    [] include
    * >= 0
    + >= 1
    ? 0 or 1
    {n} exact n
    {m,n} m to n
    {n,} n or more
    \d  \D = [^0-9]
    \w [a-zA-Z0-9_]  \W = [^a-zA-Z0-9_]
    \s white space, tab etc
    letters only [a-zA-Z]
    \ t \ r \ n    
    """
    # re.match() checks for a match only at the beginning of the string,
    # while re.search() checks for a match anywhere in the string
    import re
    if method == 'find':
        theMatch = re.finditer(pattern, string, flags=re.IGNORECASE)
        starts=[]; ends=[]
        for ind, matchObj in enumerate(theMatch):
             starts.append(matchObj.start())
             ends.append(matchObj.end()-1)
        return [starts, ends]
    elif method == 'split':
        return re.split(pattern, string, flags=re.IGNORECASE)
    elif method == 'match':
        return re.findall(pattern, string, flags=re.IGNORECASE)

def regexprep(string, pattern, replace, count=0):
    """(string, pattern, replace, count=0)
    ('Baked Beans And Spam', '\sAnd\s', ' & ') --> 'Baked Beans & Spam'

    count: maximum number of pattern occurrences to be replaced; count must be a non-negative integer.
    If omitted or zero, all occurrences will be replaced

    seems like always a good idea to use r'' with regular expression, eg,
    newValue=ez.regexprep(oldValue,r'^(\d{1,2})(,|.)',r'\1|',1)

    python regular expression notes:
    1) special trick:
    matching string not starting with my:     ^(?!my)\w+$

    group back reference \1 \2. (Perl is $1 $2)   
    >>> re.sub(r'(\w+) (\w+)',r'\2 \1','Joe Bob')
        'Bob Joe'

    either or 
    (img|hdr)
    note: [ab] either character a or b, only work for single character

    2) general usage:
    . one character
    ^ $  start end
    [^ ] exclude
    [] include
    * >= 0
    + >= 1
    ? 0 or 1
    {n} exact n
    {m,n} m to n
    {n,} n or more
    \d  \D = [^0-9]
    \w [a-zA-Z0-9_]  \W = [^a-zA-Z0-9_]
    \s white space, tab etc
    letters only [a-zA-Z]
    \ t \ r \ n    
    """
    return re.sub(pattern, replace, string, count=count)

def regexprepi(string, pattern, replace, count=0):
    """case-sensitive
    (string, pattern, replace, count=0)
    ('Baked Beans And Spam', '\sAND\s', ' & ') --> 'Baked Beans & Spam'

    count: maximum number of pattern occurrences to be replaced; count must be a non-negative integer.
    If omitted or zero, all occurrences will be replaced

    seems like always a good idea to use r'' with regular expression, eg,
    newValue=ez.regexprep(oldValue,r'^(\d{1,2})(,|.)',r'\1|',1)

    python regular expression notes:
    1) special trick: 
    matching string not starting with my:     ^(?!my)\w+$

    group back reference \1 \2. (Perl is $1 $2)   
    >>> re.sub(r'(\w+) (\w+)',r'\2 \1','Joe Bob')
        'Bob Joe'

    either or 
    (img|hdr)
    note: [ab] either character a or b, only work for single character

    2) general usage:
    . one character
    ^ $  start end
    [^ ] exclude
    [] include
    * >= 0
    + >= 1
    ? 0 or 1
    {n} exact n
    {m,n} m to n
    {n,} n or more
    \d  \D = [^0-9]
    \w [a-zA-Z0-9_]  \W = [^a-zA-Z0-9_]
    \s white space, tab etc
    letters only [a-zA-Z]
    \ t \ r \ n    
    """
    return re.sub(pattern, replace, string, count=count, flags=re.IGNORECASE)

def sprintf(formatString, *args, **kwargs):
    """
    note: if specify skipdollar=1, $ (but not others) syntax will be entirely skipped, useful for R codes (df$col), or certain bash codes
    see usage 3&4

    (formatString, *args, **kwargs)
    data dictionary is passed as *args, right now **kwargs only for skipdollar

    # -------------------------------------------------------------------------
    Examples:
    language = 'Python'; number = 2
    theDict = {"language": "Matlab", "number": 1}
    
    
    
    # usage 1: you have to pass unnamed/positional args manually
    # evaluated first before other methods in the following
    # call formatString % args
    s = sprintf('%02d\n is bigger than\n %02d',4,3)
    s = sprintf('%02d\n is bigger than\n %02d',[4,3])
    s = sprintf('%02d\n is bigger than\n %02d',(4,3))
    s = sprintf('%s has %03d quote types', language, number)
    s = sprintf('%s', language)
    


    # usage 2: if '%(' found in the string, call formatString % args
    # the following methods will be skipped
    s = sprintf('%(language)s has %(number)03d quote types.', {"language": "Python", "number": 2})
    s = sprintf('%(language)s has %(number)03d quote types.', theDict)
    s = sprintf('%(language)s has %(number)03d quote types.', locals()) # locals() returns a dictionary
    s = sprintf('%(language)s has %(number)03d quote types.') # auto get dictionary from locals()
    # 
    # this usage is very useful for complex string mixing different styles and/or env/bash variables
    s = sprintf('family="springer"; echo $family $HOME %(language)s')
    


    # usage 3: if ${var} or $var exist, replace them with regex both to {var}
    # then send to formatString.format() for evaluation -- see usage 4 for details
    # skipdollar will skip usage 3&4 entirely, sprintf('$packt {family}',skipdollar=1)
    # 
    # note: the bash $ is not natively supported by python
    # here I hack it to support the bash style, so that cmd can be directly used by both python and bash
    # but won't support $number:03d (ie, skipped) for consistency with bash
    # $0 ${0} $() ${0} {} {0,1..3} {1..$(2)} $number:03d ${number:03d} {number:03d} etc
    # other than [a-zA-Z_]+\w*? will all be skipped
    s = sprintf('$language has $number quote types.', theDict)
    s = sprintf('$language has $number quote types.')
    s = sprintf('${language}_ has $number quote types.')
    s = sprintf('$language')
    s = sprintf('$PATH')    # <--existing env variables (eg, $PATH) will not be replaced but kept as is (for later bash)
    s = sprintf('${PATH}')  # <--existing env variables (eg, ${PATH}) will not be replaced but kept as is (for later bash)
                            # <--env vars checked via os.environ (which returns a dictionary)
    #
    # better do not mix different styles, ie, %s $var {var} when formating  <--except ${var}
    s = sprintf('${language} has {number:03d} quote types.')  # -> 'Python has {number:03d} quote types.'
    s = sprintf('${language} has {number} quote types.')      # -> 'Python has 2 quote types.'
    s = sprintf('${language} = {language}')                   # OK
    


    # usage 4: usage 3 converges on this method, calls formatString.format()
    # skipdollar will skip usage 3&4 entirely, sprintf('$packt {family}',skipdollar=1)
    s = sprintf('{language} has {number} quote types.', theDict) # <--auto unpack
    s = sprintf('{language} has {number} quote types.')          # <--auto search
    


    # usage 5: long string
    longString = '''
    Hello, %s
    
    Best,
    '''
    s = sprintf(longString, language)
    # -------------------------------------------------------------------------
    """  
    # args is a tuple even when only one arg is passed in
    import re, inspect
    
    if len(args) > 1:
        return formatString % args
    elif len(args) == 1:
        if type(args[0]) in [list, tuple]:
            return formatString % tuple(*args)
        elif type(args[0]) in [dict]:
            # syntax %()
            if re.search('%\(', formatString):
                return formatString % args[0]
            else:
                # kwargs is empty {} if not specified
                try:
                    if kwargs['skipdollar']!=1: kwargs.pop('skipdollar')
                except:
                    pass
                if 'skipdollar' not in kwargs.keys():
                    # \w is [a-zA-Z0-9_], but I do not want pure number
                    # so [a-zA-Z_]+\w*? for valid variable naming
                    # ${number}, ${language}_ to {number}, {language}_
                    # but skip ${number:03d}
                    # but not replace ${PATH}
                    rs = re.findall('\$\{([a-zA-Z_]+\w*?)\}', formatString)
                    for r in rs:    
                        if r not in os.environ:
                            formatString = re.sub('\$\{('+r+')\}', r'{\1}', formatString)
                        else:
                            # trick the later .format() function ${PATH}   ->   |___|PATH|__|
                            formatString = re.sub('\$\{('+r+')\}', r'|___|\1|__|', formatString)
                    
                    # now $var -> {var}
                    rs = re.findall('\$([a-zA-Z_]+\w*?)', formatString)    
                    for r in rs:
                        if r not in os.environ:
                            formatString = re.sub('\$('+r+')', r'{\1}', formatString)
                    
                    # anything other than {[a-zA-Z_]+\w*?}--will be skipped
                    # do not know how to construct regex for invalid names, so...
                    allrs = re.findall('\{(.*?)\}', formatString)
                    validrs = re.findall('\{([a-zA-Z_]+\w*?)\}', formatString)
                    for r in allrs:
                        if r not in validrs:
                            # r may contain irregular char (eg, dot .) in this case, therefore re.sub may not work well
                            # formatString = re.sub('\{('+r+')\}', r'@__@\1@___@', formatString)
                            formatString = formatString.replace('{'+r+'}','@__@'+r+'@___@')
                    formatString = formatString.format(**args[0])
                    # replace back {invalid ...}
                    formatString = re.sub('@__@(.*?)@___@', r'{\1}', formatString)
                    # replace back env variable |___|PATH|__|  -->  ${PATH}
                    formatString = re.sub('\|___\|([a-zA-Z_]+\w*?)\|__\|', r'${\1}', formatString)

                    return formatString
                elif kwargs['skipdollar']==1:
                    return formatString
        else:
            # a single string or int
            return formatString % args         
    # no args passed in
    else:
        caller = inspect.currentframe().f_back
        return sprintf(formatString,caller.f_locals,**kwargs)
        
def iff(expression, result1, result2):
    """iff(expression, result1, result2)"""
    return result1 if expression else result2
ifelse=iff

def clear(module, recursive=False):
    """clear(module, recursive=False)
    remove a module from sys.modules so it cannot be searched.
    when recursive=True, remove the module and its submodules"""
    if recursive:
        for mod in sys.modules.keys():
            if mod.startswith(module):
                del(sys.modules[mod])
    else:
        if module in sys.modules:
            del(sys.modules[module])

import os, sys
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
THE_PATH = os.path.join(MODULE_PATH, 'timezone')
sys.path.insert(1, THE_PATH)
try:
    import pytz
    import tzlocal
except:
    pass

import os, sys, platform, string, random, re
import datetime

from random import seed as Randomize
from random import seed as randomize
from random import shuffle as RandomizeArray
from random import shuffle as randomizearray
from random import randint as Random
from random import randint as random
from random import choice as RandomChoice
from random import choice as randomchoice
def Permute(iterable=[]):
  """Permute(iterable=[])
  Returns permutations in a list
  e.g., ([1,2,3]) --> [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
  """
  from itertools import permutations
  return list(permutations(iterable))
permute = Permute

from time import sleep

def num(s):
    """num(s)
    num(3),num(3.7)-->3
    num('3')-->3, num('3.7')-->3.7
    num('3,700')-->ValueError
    num('3a'),num('a3'),-->ValueError
    num('3e4') --> 30000.0
    num(' '),num('') -->ValueError
    """
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            raise ValueError('argument is not a string of number')

def isempty(s):
    """isempty(s), None, numpy.nan return True"""
    try:
        return len(s) == 0
    except TypeError:
        # None, numpy.nan
        return True

def unique(seq):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
    duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq))

def union(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
    duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) | OrderedSet(seq2))

def intersect(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
    duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) & OrderedSet(seq2))

def setdiff(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
    duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) - OrderedSet(seq2))

def duplicate(seq):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    seq could be a list
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
    duplicate(seq) # returns a list of duplicated elements in original order
    # e.g.
    # a = [1,5,2,3,2,1,5,6,5,5,5]
    # duplicate(a) # yields [2, 1, 5]
    """
    from orderedset import OrderedSet
    seen = OrderedSet()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = OrderedSet( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

from collections import OrderedDict
class JDict(OrderedDict):
    """Jerry's dictionary
    customized ordered dictionary class with convient attributes and methods

    Methods:
    sort([reverse=False])
        sort the dictionary by key in (reverse) order
        returns a new sorted JDict, does not modify the original/itself
    update({k:v})
        adds new keys/vals or updates existing keys/vals, cannot delete
        v could be interger, string, list, dictionary
            if interger, string, assign the same key, updates val
            if list, assign the same key, append val to the existing list
            if dictionary, assign the same key, recursive call
            once, a type of v (e.g. list) determined at the first time, cannot be changed
            v could be a dictionary of list, dictionary or whatever

        e.g.
        a = JDict(); b = JDict(); c = JDict(); d = JDict()
        a.update({'k1':'v1'}); print a
        a.update({'k1':'v'}); print a
        a.update({'k2':'v'}); print a
        a.update({'k1':'v1', 'k2':'v2'}); print a

        b.update({'k1': ['v1']}); print b   # <-- seems no necessary to use ['v1',], side note: for tuple (2,)
        b.update({'k1': ['v', 'v']}); print b
        b.update({'k2': ['v']}); print b
        b.update({'k1': ['v1'], 'k2': ['v2']}); print b

        c.update({'k1': {'k11': 'v11'}}); print c
        c.update({'k1': {'k11': 'v'}}); print c
        c.update({'k1': {'k11': 'v11', 'k12': 'v12'}}); print c
        c.update({'k2': {'k21': ['v']}}); print c
        c.update({'k1': {'k13':{'k131':'v131'}}, 'k2': {'k21': ['v']}}); print c
        c.update({'k1': {'k13':{'k131':'v'}}, 'k2': {'k21': ['v']}}); print c

        d.update({'k1': JDict({'k11': 'v'})}); print d
        d.update({'k1': JDict({'k11': 'v11', 'k12': 'v12'})}); print d
    """
    def __init__(self, theDict={}):
        OrderedDict.__init__(self, theDict)
        # self = OrderedDict(theDict)  # -->not necessary or wrong??

    def update(self, theDict, prev=None):
        # prev for recursive call
        if prev == None: prev = self

        for (newKey,newVal) in theDict.items():
            # if no newKey, this is easy, simply initialize
            if not prev.has_key(newKey):
                prev[newKey] = newVal
            else:
            # key exisiting
                key = newKey
                if type(newVal) in [list]:
                    # assuming the existing val is also a list
                    prev[key].extend(newVal)
                elif type(newVal) in [OrderedDict, dict, JDict]:
                    # assuming the existing val is a dictionary
                    # recursive call, starting from the key
                    self.update(newVal,prev[key])
                else:
                    # simply update key:newVal
                    prev[key] = newVal

    def sort(self, reverse=False):
        # self = JDict(sorted(self.items(),reverse=reverse)) will not work, see
        # http://stackoverflow.com/questions/1216356/
        return JDict(sorted(self.items(),reverse=reverse))

class Moment(object):
    """A datetime like class, but with convenient attributes and methods

    Has common datetime attributes as strings.
    Wraps timedelta for easy calling.
    Formats the datetime to a string.
    Transforms a datetime-like string to a Moment object.
    Converts to specified timezone

    Attributes:
        moment, returns the datetime instance

        (the following all return string, while ignoring tzinfo)
        datetime, returns the string of date and time
        date, returns the string of the date
        time
        timezone
        year
        month
        day
        weekday
        hour
        ampm
        minute
        second
        microsecond
    """
    def __init__(self, timezone=None, moment=None):
        """Generates the current datetime in specified timezone, or local naive datetime if omitted, (when moment omitted).

        Args:
            timezone is the specified timezone string
                UTC: Coordinated Universal Time (not a time zone, but a time standard)
                GMT: Greenwich Mean Time (a time zone)
                but Moment('UTC').datetime = Moment('GMT').datetime

                US timezone:
                US/Alaska, US/Aleutian, US/Arizona, US/Central, US/East-Indiana, US/Eastern, 
                US/Hawaii, US/Indiana-Starke, US/Michigan, US/Mountain, US/Pacific, US/Pacific-New, US/Samoa

                Use the codes to look up:
                from pytz import all_timezones
                print len(all_timezones)
                for zone in all_timezones:
                    if 'US' in zone:
                        print zone

            moment could be naive (without tzinfo) or aware (with tzinfo) datetime

        """
        if not timezone:
            if not moment:
                moment = datetime.datetime.now()
            else:
                moment = moment
        else:
            if not moment:
                moment = datetime.datetime.now(pytz.timezone(timezone))
            else:
                if not moment.tzinfo:
                    # simply attach timezone to it
                    moment = moment.replace(tzinfo=pytz.timezone(timezone))
                else:
                    # convert to desired timezone
                    moment = moment.astimezone(pytz.timezone(timezone))

        self.moment = moment
        self.timezone = str(moment.tzinfo) if moment.tzinfo else None

        self.datetime = moment.strftime("%Y-%m-%d_%H-%M-%S")
        # in the format of 1/2/2014 for single digits, and 10/14/2014 for two digits
        self.date = str(moment.month)+"/"+str(moment.day)+"/"+str(moment.year)
        self.time = moment.strftime("%H:%M:%S")
        self.year = moment.strftime("%Y")
        self.month = moment.strftime("%B")
        self.day = moment.strftime("%d")
        self.weekday = moment.strftime("%A")
        self.hour = moment.strftime("%I")
        self.ampm = moment.strftime("%p")
        self.minute = moment.strftime("%M")
        self.second = moment.strftime("%S")
        self.microsecond = moment.strftime("%f")

    def Shift(self, *args, **kwargs):
        """Shifts time to the past or future.

        Args:
            the same as timedelta: [days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]]
            Use negative values to shift to the past

        Returns:
            an instance of Moment

        Raises:
            None
        """
        future = self.moment + datetime.timedelta(*args, **kwargs)
        return Moment(timezone=self.timezone, moment=future)

    def Format(self, datetimeFormat):
        """Formats the datetime to a string.

        Args:
            the format of the desired string.

        Returns:
            a string

        Raises:
            None
        """
        datetimeString = self.moment.strftime(datetimeFormat)
        return datetimeString

    def Convert(self, timezone=None):
        """Convert to a specified timezone.
        timezone is a specified timezone string, see the class help
        returns an instance of Moment
        """
        # if naive
        if self.timezone is None:
            tz = tzlocal.get_localzone()
            # attach local tz
            dt = tz.localize(self.moment)
        else:
            dt = self.moment
        timezone = pytz.timezone(timezone)
        newdt = dt.astimezone(timezone)
        return Moment(timezone=None, moment=newdt)

    @classmethod
    def Transform(cls, datetimeString, datetimeFormat, timezone=None):
        """Transforms a datetime-like string to a Moment object.

        Args:
             a datetime-like string, e.g. "21/11/06 16:30"
             the format information of the string, e.g. "%d/%m/%y %H:%M"

                    %a      Sun, Mon, ..., Sat (en_US);
                    %A      Sunday, Monday, ..., Saturday (en_US);
                    %w      0 is Sunday and 6 is Saturday.   0, 1, ..., 6     
                    %d      01, 02, ..., 31      
                    %b      Jan, Feb, ..., Dec (en_US);
                    %B      January, February, ..., December (en_US);
                    %m      01, 02, ..., 12      
                    %y      Year    00, 01, ..., 99      
                    %Y      Year    1970, 1988, 2001, 2013   
                    %H      Hour (24-hour clock)    00, 01, ..., 23      
                    %I      Hour (12-hour clock)    01, 02, ..., 12      
                    %p      AM, PM (en_US);
                    %M      Minute 00, 01, ..., 59      
                    %S      Second 00, 01, ..., 59
                    %f      Microsecond     000000, 000001, ..., 999999
                    %z      UTC offset in the form +HHMM or -HHMM   (empty), +0000, -0400, +1030
                    %Z      Time zone name  (empty), UTC, EST, CST
                    %j      Day of the year     001, 002, ..., 366   
                    %U      Week number of the year (Sunday as the first day of the week)
                    %W      Week number of the year (Monday as the first day of the week)
                    %c      Locale's appropriate date and time representation.  Tue Aug 16 21:30:00 1988 (en_US);
                    %X      Locale's appropriate date representation.   08/16/88 (None); 08/16/1988 (en_US);
                    %X      Locale's appropriate time representation.   21:30:00 (en_US);
                    %%      A literal '%' character.    %
            
            timezone is the specified timezone string, see the class help

        Returns:
            a Moment object

        Raises:
           None
        """
        # strptime returns naive datetime
        # hack: python 2.7 does not recognize %z
        # input: 
        #       datetimeString = 'Thu, 18 Jun 2015 16:52:23 -0400'
        #       datetimeFormat = '%a, %d %b %Y %H:%M:%S %z'
        # output: 
        #       moment (datetime with tzinfo) which is like:
        #       datetime.datetime(2015, 6, 18, 16, 52, 23, tzinfo=-0400)
        if '%z' in datetimeFormat:
            from datetime import timedelta, tzinfo
            class FixedOffset(tzinfo):
                """Fixed offset in minutes: `time = utc_time + utc_offset`."""
                def __init__(self, offset):
                    self.__offset = timedelta(minutes=offset)
                    hours, minutes = divmod(offset, 60)
                    #NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
                    #  that have the opposite sign in the name;
                    #  the corresponding numeric value is not used e.g., no minutes
                    self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)
                def utcoffset(self, dt=None):
                    return self.__offset
                def tzname(self, dt=None):
                    return self.__name
                def dst(self, dt=None):
                    return timedelta(0)
                def __repr__(self):
                    # offset in minutes
                    offset = self.utcoffset().total_seconds()/60
                    sign = '-' if offset < 0 else '+'
                    # /60.  add .  to get decimal points
                    return "%s%02d%02d" % (sign, abs(offset) / 60., abs(offset) % 60)
            import re
            naive_datetimeString = re.sub('[-+]\d{4}','',datetimeString)
            naive_dt = datetime.datetime.strptime(naive_datetimeString, datetimeFormat.replace('%z',''))
            offset_str = re.findall('[-+]\d{4}',datetimeString)[0]
            offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
            if offset_str[0] == "-":
                offset = -offset
            moment = naive_dt.replace(tzinfo=FixedOffset(offset))
            # print moment
            # datetime.datetime(2015, 6, 18, 16, 52, 23, tzinfo=-0400)
        # hack end
        else:
            moment = datetime.datetime.strptime(datetimeString, datetimeFormat)
        return Moment(timezone=timezone, moment=moment)

def lines(path='.', pattern='\.py$|.ini$|\.c$|\.h$|\.m$', recursive=True):
    """Counts lines of codes, counting empty lines as well.
    lines(path='.', pattern='\.py$|.ini$|\.c$|\.h$|\.m$', recursive=True)
    """

    # modified from https://liangsun.org/posts/python-code-for-counting-loclines-of-code/
    # Created by Liang Sun <i@liangsun.org> in 2012
    # This code is for Python 2.x
    COUNT_EMPTY_LINE = True

    def read_line_count(fname):
        count = 0
        for line in open(fname).readlines():
            if COUNT_EMPTY_LINE or len(line.strip()) > 0:
                count += 1
        return count

    line_count = 0
    file_count = 0
    files = fls(path,pattern) if recursive else ls(path,pattern)
    for file in files:
        try:
            file_count += 1
            c = read_line_count(file)
            print "%s : %d" % (os.path.basename(file), c)
            line_count += c
        except:
            pass

    print '-----------------------------'
    print 'File counted: %d' % file_count
    print 'Line counted: %d' % line_count
    print 'Done!'

def keygen(length=8, complexity=3):
    """generate a random key
    keygen(length=8, complexity=3)

    length: how long is the generated key

    complexity:
    1 = digits only
    2 = digits + lowercase  i.e., 'abcdefghijklmnopqrstuvwxyz'
    3 = digits + uppercase (default)
    4 = digits + lowercase + uppercase
    5 = digits + lowercase + uppercase + punctuation
    6 = digits + lowercase + uppercase + punctuation + whitespace
    or alternatively, complexity could be a list of chars like, '0123456789abcdefABCDEF'
    in which case, the key will only be composed of chars from the list
    """
    import string
    import random
    if complexity == 1:
        chars = string.digits
    elif complexity == 2:
        chars = string.digits + string.ascii_lowercase
    elif complexity == 3:
        chars = string.digits + string.ascii_uppercase
    elif complexity == 4:
        chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    elif complexity == 5:
        chars = string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation
    elif complexity == 6:
        chars = string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.whitespace
    elif complexity not in [1, 2, 3, 4, 5, 6]:
        chars = str(complexity)
    return ''.join(random.choice(chars) for x in range(length))

def hashes(filename, reference=None):
    """Calculate/Print a file's md5 32; sha1 32; can handle big files in a memory efficient way"""
    import hashlib
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
            sha1.update(chunk)
    if reference:
        if reference.lower() == md5.hexdigest().lower():
            print 'md5 32: ' + md5.hexdigest() + ' (matched)!'
        else:
            print 'md5 32: ' + md5.hexdigest() + ' (NOT MATCHED)!'
        if reference.lower() == sha1.hexdigest().lower():
            print 'sha1 32: ' + sha1.hexdigest() + ' (matched)!'
        else:
            print 'sha1 32: ' + sha1.hexdigest() + ' (NOT MATCHED)!'
    else:
        print 'md5 32: ' + md5.hexdigest()
        print 'sha1 32: ' + sha1.hexdigest()

def readx(path, sheet=0, r=[1,], c=None, *args, **kwargs):
    """
    (path, sheet=0, r=[1,], c=None, *args, **kwargs)
    Read xlsx, xls file into a list (see returns for details), using xlrd library
    Args:
        path, a xlsx, xls file
        sheet, either sheet number (the first is 0) or sheet name (e.g., Sheet1)
        r, None=start-end; 3=4th row (zero based); [3,4,5]=listed rows; [1,]=from 2nd row to end (ie, skipping first row, or header)
        c, the same format as r
    Returns:
        if multiple rows/columns, returns a list of list [[row1],[row2]]. To further slice returned result, result[r][c]
        if a single row/column, returns a list
        if a single cell, returns that cell as string, number depending on that cell type
        Note: the cells/elements in a list/column/row could have different data types, exactly the same as the actual data type in the excel file
              eg, a number is formated as string in excel file, then the returned type is string, u'2017'
              empty cell returns u'', but cell with spaces returns u'  '
    Raises:
       None
    """
    import xlrd
    wbobj = xlrd.open_workbook(path)
    # convert sheet index to sheet name
    if type(sheet) in [int]:
        sheets = wbobj.sheet_names()
        sheet = sheets[sheet]
    else:
        sheet = sheet
    sheetobj = wbobj.sheet_by_name(sheet)

    if r == None:
        r = range(0,sheetobj.nrows)     # all rows
    elif type(r) in [int]:
        r = [r]     # a single row
    elif type(r) in [list]:
        if len(r) == 1:
            r = range(r[0],sheetobj.nrows)  # from r to end
        else:
            r = r   # multiple rows
    else:
        raise Exception('Invalid row number(s)')

    if c == None:
        c = range(0,sheetobj.ncols)     # all cols
    elif type(c) in [int]:
        c = [c]    # a single col
    elif type(c) in [list]:
        if len(c) == 1:
            c = range(c[0],sheetobj.ncols)  # from c to end
        else:
            c = c   # multiple cols
    else:
        raise Exception('Invalid col number(s)')

    if len(r)==1 and len(c)==1:
        result = sheetobj.cell_value(r[0],c[0])
    elif len(r)==1 and len(c)>1:
        result = sheetobj.row_values(r[0])
        result = [result[i] for i in c]
    elif len(r)>1 and len(c)==1:
        result = sheetobj.col_values(c[0])
        result = [result[i] for i in r]
    elif len(r)>1 and len(c)>1:
        result = []
        for rr in r:
            row = sheetobj.row_values(rr)
            row = [row[i] for i in c]
            result.append(row)

    return result

def savex(path, data, header=None, delimiter=",", sheet_name='Sheet1', *args, **kwargs):
    """
    (path, data, header=None, sheet_name='Sheet1', *args, **kwargs)
    Write a list of list to a xlsx (xlsxwriter), xls(xlwt), csv file
    Args:
        path
            the path to the excel file (xlsx/xls), or csv(.csv, comma separated); explicitly specify .xlsx/xls or .csv 
            xls (but not xlsx) may be more compatible with old-version software (spss v20)
            however, xls limited to 256 columns by 65536 rows
            in which case, consider csv as an alternative
            or xlsx which has limits of 16,384 columns by 1,048,576 rows
            csv writing is much faster than xlsx
        data
            a list of list (each sublist is a row)
        header
            a list with each column's name, eg ['company','brand','price']
        delimiter
            only for writing csv, ignored for excel
    Returns:
        File is overwritten!
        Each element of list could be of different type, resulting in different format for each cell in excel file
        None and empty strings '' are written blank
        Strings and string of number are written as string
        Numbers as Numbers
        Returns Nothing
        For csv file, everything a string
    Raises:
       None
    """
    if path.endswith('.xls'):
        import xlwt
        book = xlwt.Workbook()
        sheet = book.add_sheet(sheet_name)

        if header:
            for c, val in enumerate(header):
                sheet.write(0, c, val, *args, **kwargs)
            header = 1
        else:
            header = 0

        for r, row in enumerate(data,header):
            for c, val in enumerate(row):
                sheet.write(r, c, val, *args, **kwargs)
        book.save(path)
    elif path.endswith('.xlsx'):
        import xlsxwriter
        xbook = xlsxwriter.Workbook(path)
        xsheet = xbook.add_worksheet(sheet_name)

        if header:
            for c, val in enumerate(header):
                xsheet.write(0, c, val, *args, **kwargs)
            header = 1
        else:
            header = 0

        for r, row in enumerate(data,header):
            # https://xlsxwriter.readthedocs.io/worksheet.html#worksheet-write-row
            xsheet.write_row(r, 0, row, *args, **kwargs)
        xbook.close()
    else:
        import  csv
        with open(path,"w") as f:
            wr = csv.writer(f, delimiter=delimiter, *args, **kwargs)
            if header: wr.writerow(header)
            wr.writerows(data)
writex = savex

def hanzifreq(filename, size=10, outfile=None, encoding='utf8'):  
    """
    (filename, size, outfile, encoding)
    size: top # items; if None, print(save) all items
    outfile: path; if None, no save
    does not count punctuation (ie, ignore punctuation)
    print(save) freq table (top # items) and return a list [(char,times)]  (always all items)
    
    see also http://www.tagxedo.com/ (support Chinese characters)
    """
    # modified from http://blog.csdn.net/xm1331305/article/details/8090639

    import codecs  
    from time import time  
    from operator import itemgetter  
    import sys

    begin = time()

    count = {}  
    for line in codecs.open(filename, 'r', encoding):  
        for chr in line:  
            if u'\u4E00' <= chr <= u'\u9FA5' or  u'\uF900' <= chr <= u'\uFA2D':  
                count[chr] = 1 + count.get(chr, 0)

    hanzifreq = sorted(count.iteritems(), key=itemgetter(1), reverse=True)
    result = hanzifreq  # for return
    if size: hanzifreq = hanzifreq[:size]

    print '\n'.join([u'%s\t%s' % (chr, times) for chr, times in hanzifreq]) 
    if outfile:
        with codecs.open(outfile, mode='w', encoding='utf-8') as outFile:
            outFile.write('\n'.join([u'%s,%s' % (chr, times) for chr, times in hanzifreq]))
    
    print 'Done! Elapsed %s seconds.' % (time()-begin)
    return result

def chunk(xs, n):
    '''
    Split the list, xs, into n chunks. 
    gives exactly n chunks, but they may not be evenly sized, since the last chunk gets padded with any surplus.
    eg, 
    chunk('abcdefghij', 3) ->     ['abc', 'def', 'ghij']
    chunk([1,2,3,4],3)     ->     [[1], [2], [3, 4]]
    chunk([1,2,3,4,5,6],6) ->     [[1], [2], [3], [4], [5], [6]]
    chunk([1,2,3,4,5,6],1) ->     [[1, 2, 3, 4, 5, 6]]
    '''
    # http://wordaligned.org/articles/slicing-a-list-evenly-with-python
    L = len(xs)
    assert 0 < n <= L
    s, r = divmod(L, n)
    chunks = [xs[p:p+s] for p in range(0, L, s)]
    chunks[n-1:] = [xs[-r-s:]]
    return chunks

def chunk2(initialList, chunkSize):
    """
    This function chunks a list into sub lists 
    that have a length equals to chunkSize.

    Example:
    lst = [3, 4, 9, 7, 1, 1, 2, 3]
    print(chunk2(lst, 3)) 
    returns
    [[3, 4, 9], [7, 1, 1], [2, 3]]
    """
    # https://stackoverflow.com/a/28786255/2292993
    finalList = []
    for i in range(0, len(initialList), chunkSize):
        finalList.append(initialList[i:i+chunkSize])
    return finalList

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# debugging
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    pass