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

Almost all commands support the usage of '~', '..', '.', '?', '*' in path (ls,fls only support regular expression).
Symbolic link itself is the target of file operations; the actual file should be safe.

error(msg)

fullpath(path)
pwd() or cwd()  # Returns current working director.
csd(), csf()   # Returns current script directory, i.e. the directory where the running script is.
parentdir(path) # Returns the parent directory of a path.
joinpath(path1[, path2[, ...]])   # Returns the joined path. Supports vectorization.
join(sep,string1,string2) # Glues together strings with sep. Supports vectorization.
splitpath(path) # Returns a list of path elements: [path, file, ext]. Supports vectorization.
cd(path)    # Changes to a new working directory.

ls([path[, regex]], full=True)    # Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
lsd([path[, regex]], full=True)
fls([path[, regex]])   # Returns a list of files with their full paths in flattened path (i.e. walk each subdirectory).
# the filter only works for short file name not for full file name, i.e. the file name itself not its full path
# regular expression is case-sensitive
# usage: ls(); ls(cwd()); ls(cwd(), "\.py$")

mkdir("path/to/a/directory")    # Makes a directory (also any one of the "path", "to", "a" directories if not exits).
rn(old, new) # Renames old to new.
exists(path)    # Returns the existence of path (0 or 1).
rm(path)    # Deletes a file or folder. Supports wildcards, vectorization.
cp(source, destination)  # Copies source file(s) or folder to destination. Supports wildcards, vectorization.
mv(source, destination)  # Moves source file(s) or folder to destination. Supports wildcards, vectorization.

execute(cmd, output=True)    # Executes a bash command with or without capturing shell output

pprint() # Pretty prints.
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

log(file="log.txt", mode='a', status=True) # Prints output to both terminal and a file (log.txt) globally. mode: a=append; w=overwrite

tree([path[, Folder]) # Prints a directory tree structure. Folder=True prints files in addition to folders.

[starts, ends] = regexp(string, pattern); regexp(string, pattern, method='split/match'), regexpi
regexprep(string, pattern, replace, count=0), regexprepi

sprintf(formatString, *args)
sort()
iff(expression, result1, result2)
clear(module, recursive=False)

num(string)
isempty(s)
Randomize(x), randomize(x) # Sets a randomization seed.
RandomizeArray(list=[])   randomizearray(list=[])  # Shuffles a list in place.
Random(a,b) random(a,b) # Returns a random integer N such that a <= N <= b.
RandomChoice(seq), randomchoice(seq) # Returns a random element from sequence
Permute(iterable=[]) permute(iterable=[]) # Returns permutations in a list

unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
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

JDict() # Jerry's dictionary, customized ordered dictionary class with convient attributes and methods, see help(JDict)
Moment(timezone)    # Generates the current datetime in specified timezone, or local naive datetime if omitted.

SetClip(content), setclip(content)   # Copy/Write something to current clipboard
content = GetClip(), content = getclip()   # Read out content from current clipboard and assign to a variable

lines(path='.', pattern='\.py$|.ini$|\.c$|\.h$|\.m$', recursive=True) # Counts lines of codes, counting empty lines as well.
keygen(length=8, complexity=3)  # generate a random key
hashes(filename): # Calculate/Print a file's md5 32; sha1 32; can handle big files in a memory efficient way

isemailvalid(email) # True or False, isEmailValid, IsEmailValid
"""

# reference: abspath for ../ ./, expanduser for ~, glob to resolve wildcards, fnmatch.translate wildcards to re
import os, sys, platform, string, random, shutil, re, subprocess, glob, ConfigParser, fnmatch
from os.path import abspath, basename, dirname, splitext, isfile, isdir, realpath, expanduser

_DEBUG_MODE = 0
def ShellDebug(debugMode=1):
    global _DEBUG_MODE
    _DEBUG_MODE = debugMode

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
    """
    return os.path.normpath(os.path.abspath(os.path.expanduser(path)))

def csd():
    """(),Returns current script directory, i.e. the directory where the running script is."""
    path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    # hack when a script is packed into an app, which returns xxx.app/Contents/Resources
    return os.path.abspath(os.path.join(path,os.pardir,os.pardir,os.pardir)) if path.endswith('.app/Contents/Resources') else path

def csf():
    """(),Returns current script name, i.e. the name of the running script."""
    path = os.path.abspath(sys.argv[0])
    dir = os.path.dirname(path)
    ext = os.path.splitext(path)[1]
    file = os.path.basename(path)[0:-len(ext)] if len(ext) != 0 else os.path.basename(path)
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

def join(sep='',*args):
    """join(sep,string1,string2)
       Glues together strings with sep. Supports vectorization
       Returns the joined string, supports vectorization
    """
    assert len(args) >= 1, "Give me more inputs"
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

def splitpath(path):
    """splitpath(path), Split path into [dir, file, ext]. e.g., file=easyshell, ext=.py
    Supports vectorization."""
    # return os.path.split(path)

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

def cd(path):
    """cd(path), Changes to a new directory."""
    path = fullpath(path)
    os.chdir(path)
    print "Start working in " + os.getcwd()

def ls(path="./", regex=".*", full=True):
    """ls([path[, regex]], full=True)    # Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
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
    if full: files = [os.path.join(path,file) for file in files]
    return [file for file in files if os.path.isfile(file)]

def lsd(path="./", regex=".*", full=True):
    """lsd([path[, regex]], full=True), Returns a list of all (including hidden) folders with their full paths in path, filtered by regular expression."""
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
    if full: files = [os.path.join(path,file) for file in files]
    return [file for file in files if not os.path.isfile(file)]

def fls(path="./", regex=".*"):
    """fls([path[, regex]])   # Returns a list of files with their full paths in flattened path (i.e. walk each subdirectory).
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
        filteredFiles = _FilterList(files, pattern_regex)
        ## If there is matched
        if filteredFiles:
            for file in filteredFiles:
                fileFullName = os.path.join(root, file)
                flatFiles.append(fileFullName)
    return flatFiles

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
          if old and new both folders, error
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
            raise Exception('Cannot rename to exising folder name')
        else:
            os.rename(source,destination)
    else:
        if not os.path.isdir(os.path.dirname(destination)):
            raise Exception('Destination folder does not exist')
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

def cp(source, destination, ignores=None):
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
            if not _DEBUG_MODE:
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
                print "Simulation! Copied file: " + "->".join([source, destination])
        elif os.path.isdir(source):
            if not _DEBUG_MODE:
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
                print "Simulation! Copied folder: " + "->".join([source, destination])
        # else:
        #     print source + " not copied to " + destination

def mv(source, destination):
    """Moves a source file or folder to destination.
    support vectorization
    destination parent folder does not have to exist already
    mv('a.txt','folder'), mv('a.txt','folder/a.txt'), mv('a.txt','folder/b.txt')
    mv('a','b')-->get b/a, b now has a as subfolder, regardless of b exists or not
    """
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
        if not _DEBUG_MODE:
            shutil.move(source, destination)
            # print "Moved: " + "->".join([source, destination])
        elif _DEBUG_MODE:
            print "Simulation! Moved: " + "->".join([source, destination])
        # else:
        #     print source + " not moved to " + destination

def lns(source, destination):
    """Creates a soft link / symbolic link /shortcut."""
    source = fullpath(source)
    destination = fullpath(destination)

    os.symlink(source, destination)
    print "Symbolic link: " + "->".join([source, destination])

def execute(cmd, output=True):
    """Executes a bash command.
    (cmd, output=True)
    output: whether capture shell output
    """
    if not _DEBUG_MODE:
        print "Output of command " + cmd + " :"
        if os.name == 'nt' or platform.system() == 'Windows':
            if output:
                subprocess.call(cmd, shell=True)
            else:
                subprocess.call(cmd, shell=True, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        else:
            if output:
                subprocess.call(cmd, shell=True, executable="/bin/bash")    # Use bash; the default is sh
            else:
                subprocess.call(cmd, shell=True, executable="/bin/bash", stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        print ""
    else:
        print "Simulation! The command is " + cmd
        print ""

from pprint import pprint

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
        theNameSpace = {}
        exec('import ' + package_name, theNameSpace)
        print theNameSpace[package_name].__version__
version = ver

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

def SetLog(file="log.txt", mode='a', status=True):
    """
    log(file="log.txt", mode='a', status=True)
    Prints output to both terminal and a file (log.txt) globally.
    mode: a=append; w=overwrite
    """
    import sys, datetime

    class Logger(object):
        def __init__(self, file):
            self.file = file
            sys.stdout = sys.__stdout__
            print "log on with " + fullpath(self.file)
            self.terminal = sys.stdout
            self.log = open(file, mode)
            self.log.write("++++++++++\n")
            self.log.write("starts at " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "\n")
            self.log.flush()

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()

        def off(self):
            self.log.write("ends at " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "\n")
            self.log.write("++++++++++\n")
            self.log.write("\n")
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

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# print directory tree structure starts
# modified from http://code.activestate.com/recipes/577091/
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def tree(path='./', F=False):
    """
    tree([path[, Folder]) # Prints a directory tree structure. Folder=True prints files in addition to folders.
    """
    import sys, os
    global PRINT_FILES; PRINT_FILES = F
    path = os.path.normpath(os.path.abspath(os.path.expanduser(path)))

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
    """
    return re.sub(pattern, replace, string, count=count)

def regexprepi(string, pattern, replace, count=0):
    """case-sensitive
    (string, pattern, replace, count=0)
    ('Baked Beans And Spam', '\sAND\s', ' & ') --> 'Baked Beans & Spam'

    count: maximum number of pattern occurrences to be replaced; count must be a non-negative integer.
    If omitted or zero, all occurrences will be replaced
    """
    return re.sub(pattern, replace, string, count=count, flags=re.IGNORECASE)

def sprintf(formatString, *args):
    """
    (formatString, *args)
    Examples:
    language = 'Python'; number = 2
    theDict = {"language": "Matlab", "number": 1}
    
    # recommended usage (mixing old, new and alternative syntax):    
    s = sprintf('%02d\n is bigger than\n %02d',4,3)
    s = sprintf('%02d\n is bigger than\n %02d',[4,3])
    s = sprintf('%02d\n is bigger than\n %02d',(4,3))
    s = sprintf('%s has %03d quote types', language, number)
    s = sprintf('%s', lanuage)
    
    s = sprintf('{language} has {number:03d} quote types.', theDict) <--auto unpack
    s = sprintf('$language has $number:03d quote types.', theDict)

    s = sprintf('{language} has {number:03d} quote types.')          <--auto search
    s = sprintf('$language has $number:03d quote types.')
    s = sprintf('$language')
    
    longString = '''
    Hello, %s
    
    Best,
    '''
    s = sprintf(longString, language)
    
    # -------------------------------------------------------------------------
    # old syntax:
    s = sprintf('%02d\n is bigger than\n %02d',4,3)
    s = sprintf('%02d\n is bigger than\n %02d',[4,3])
    s = sprintf('%02d\n is bigger than\n %02d',(4,3))
    s = sprintf('%s has %03d quote types', language, number)
    
    s = sprintf('%(language)s has %(number)03d quote types.', {"language": "Python", "number": 2})
    s = sprintf('%(language)s has %(number)03d quote types.', theDict)
    s = sprintf('%(language)s has %(number)03d quote types.', locals()) # locals() returns a dictionary
    s = sprintf('%(language)s has %(number)03d quote types.') # auto get dictionary from locals()
    """  
    # args is a tuple even when only one arg is passed in
    import re, inspect
    
    if len(args) > 1:
        return formatString % args
    elif len(args) == 1:
        if type(args[0]) in [list, tuple]:
            return formatString % tuple(*args)
        elif type(args[0]) in [dict]:
            if re.search('%\(', formatString):
                return formatString % args[0]
            else:
                formatString = re.sub('\$(\S+)', r'{\1}', formatString)
                return formatString.format(**args[0])
        else:
            # a single string or int
            return formatString % args         
    else:
        caller = inspect.currentframe().f_back
        if re.search('%\(', formatString):
            return formatString % caller.f_locals
        else:
            formatString = re.sub('\$(\S+)', r'{\1}', formatString)
            return formatString.format(**caller.f_locals)

def sort(*args, **kwargs):
    """wrapper of sorted, passed in list does not change, returns a sorted list"""
    return sorted(*args, **kwargs)

def iff(expression, result1, result2):
    """iff(expression, result1, result2)"""
    return result1 if expression else result2

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
    """num(s)"""
    try:
        return int(s)
    except ValueError:
        return float(s)


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
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq))


def union(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
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
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) | OrderedSet(seq2))


def intersect(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
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
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) & OrderedSet(seq2))


def setdiff(seq1,seq2):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
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
    """
    from orderedset import OrderedSet
    return list(OrderedSet(seq1) - OrderedSet(seq2))


def duplicate(seq):
    """
    unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
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

        b.update({'k1': ['v1']}); print b
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


class Moment(object):
    """A datetime like class, but with convenient attributes and methods

    Has common datetime attributes as strings.
    Wraps timedelta for easy calling.
    Formats the datetime to a string.
    Converts a datetime-like string to a Moment object.

    Methods:
    Shift, Format, Transform

    Attributes:
        moment, returns the datetime instance

        (the following all return string)
        datetime, returns the string of date and time
        date, returns the string of the date
        time
        year
        month
        day
        weekday
        hour
        ampm
        minute
        second
        microsecond

    def __init__(self, timezone=None, moment=None):
        Generates the current datetime in specified timezone, or local naive datetime if omitted, (when moment omitted).
        Args:
            timezone is the specified timezone string
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
    def __init__(self, timezone=None, moment=None):
        """Generates the current datetime in specified timezone, or local naive datetime if omitted, (when moment omitted).

        Args:
            timezone is the specified timezone string
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

        Returns:
            a Moment object

        Raises:
           None
        """
        # strptime returns naive datetime
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

def hashes(filename):
    """Calculate/Print a file's md5 32; sha1 32; can handle big files in a memory efficient way"""
    import hashlib
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
            sha1.update(chunk)
    # print 'md5 16: ' + md5.digest()   
    print 'md5 32: ' + md5.hexdigest()
    # print 'sha1 16: ' + sha1.digest()
    print 'sha1 32: ' + sha1.hexdigest()

def isemailvalid(email, check_mx=False, verify=False):
    """Indicate whether the given string is a valid email address
    according to the 'addr-spec' portion of RFC 2822 (see section
    3.4.1).  Parts of the spec that are marked obsolete are *not*
    included in this test, and certain arcane constructions that
    depend on circular definitions in the spec may not pass, but in
    general this should correctly identify any email address likely
    to be in use as of 2011.

    For check the domain mx and verify email exits you must have the pyDNS package installed:
    pip install pyDNS

    Check if the host has SMTP Server: ('example@example.com',check_mx=True)
    Check if the host has SMTP Server and the email really exists: ('example@example.com',verify=True)  <--not working sometimes?
    """
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # modified from https://github.com/syrusakbary/validate_email
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # RFC 2822 - style email validation for Python
    # (c) 2012 Syrus Akbary <me@syrusakbary.com>
    # Extended from (c) 2011 Noel Bush <noel@aitools.org>
    # for support of mx and user check (i.e., whether the mail server actually exists, user actually exists)
    # This code is made available to you under the GNU LGPL v3.
    #
    # returns True or False to indicate whether a given address
    # is valid according to the 'addr-spec' part of the specification
    # given in RFC 2822.  Ideally, we would like to find this
    # in some other library, already thoroughly tested and well-
    # maintained.  The standard Python library email.utils
    # contains a parse_addr() function, but it is not sufficient
    # to detect many malformed addresses.
    #
    # This implementation aims to be faithful to the RFC, with the
    # exception of a circular definition (see comments below), and
    # with the omission of the pattern components marked as "obsolete".

    import re
    import smtplib
    import socket

    try:
        import DNS
        ServerError = DNS.ServerError
    except:
        DNS = None
        class ServerError(Exception): pass
    # All we are really doing is comparing the input string to one
    # gigantic regular expression.  But building that regexp, and
    # ensuring its correctness, is made much easier by assembling it
    # from the "tokens" defined by the RFC.  Each of these tokens is
    # tested in the accompanying unit test file.
    #
    # The section of RFC 2822 from which each pattern component is
    # derived is given in an accompanying comment.
    #
    # (To make things simple, every string below is given as 'raw',
    # even when it's not strictly necessary.  This way we don't forget
    # when it is necessary.)
    #
    WSP = r'[ \t]'                                       # see 2.2.2. Structured Header Field Bodies
    CRLF = r'(?:\r\n)'                                   # see 2.2.3. Long Header Fields
    NO_WS_CTL = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'        # see 3.2.1. Primitive Tokens
    QUOTED_PAIR = r'(?:\\.)'                             # see 3.2.2. Quoted characters
    FWS = r'(?:(?:' + WSP + r'*' + CRLF + r')?' + \
                WSP + r'+)'                                    # see 3.2.3. Folding white space and comments
    CTEXT = r'[' + NO_WS_CTL + \
                    r'\x21-\x27\x2a-\x5b\x5d-\x7e]'              # see 3.2.3
    CCONTENT = r'(?:' + CTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.2.3 (NB: The RFC includes COMMENT here
                                                                                                             # as well, but that would be circular.)
    COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + \
                        r')*' + FWS + r'?\)'                       # see 3.2.3
    CFWS = r'(?:' + FWS + r'?' + COMMENT + ')*(?:' + \
                 FWS + '?' + COMMENT + '|' + FWS + ')'         # see 3.2.3
    ATEXT = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'           # see 3.2.4. Atom
    ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'      # see 3.2.4
    DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'   # see 3.2.4
    DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?' # see 3.2.4
    QTEXT = r'[' + NO_WS_CTL + \
                    r'\x21\x23-\x5b\x5d-\x7e]'                   # see 3.2.5. Quoted strings
    QCONTENT = r'(?:' + QTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.2.5
    QUOTED_STRING = CFWS + r'?' + r'"(?:' + FWS + \
                                    r'?' + QCONTENT + r')*' + FWS + \
                                    r'?' + r'"' + CFWS + r'?'
    LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + \
                             QUOTED_STRING + r')'                    # see 3.4.1. Addr-spec specification
    DTEXT = r'[' + NO_WS_CTL + r'\x21-\x5a\x5e-\x7e]'    # see 3.4.1
    DCONTENT = r'(?:' + DTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.4.1
    DOMAIN_LITERAL = CFWS + r'?' + r'\[' + \
                                     r'(?:' + FWS + r'?' + DCONTENT + \
                                     r')*' + FWS + r'?\]' + CFWS + r'?'  # see 3.4.1
    DOMAIN = r'(?:' + DOT_ATOM + r'|' + \
                     DOMAIN_LITERAL + r')'                       # see 3.4.1
    ADDR_SPEC = LOCAL_PART + r'@' + DOMAIN               # see 3.4.1

    # A valid address will match exactly the 3.4.1 addr-spec.
    VALID_ADDRESS_REGEXP = '^' + ADDR_SPEC + '$'

    try:
        assert re.match(VALID_ADDRESS_REGEXP, email) is not None
        check_mx |= verify
        if check_mx:
            if not DNS: raise Exception('For check the mx records or check if the email exists you must have installed pyDNS python package')
            DNS.DiscoverNameServers()
            hostname = email[email.find('@')+1:]
            mx_hosts = DNS.mxlookup(hostname)
            for mx in mx_hosts:
                try:
                    smtp = smtplib.SMTP()
                    smtp.connect(mx[1])
                    if not verify: return True
                    status, _ = smtp.helo()
                    if status != 250: continue
                    smtp.mail('')
                    status, _ = smtp.rcpt(email)
                    if status != 250: return False
                    break
                except smtplib.SMTPServerDisconnected: #Server not permits verify user
                    break
                except smtplib.SMTPConnectError:
                    continue
    except (AssertionError, ServerError):
        return False
    return True
isEmailValid = isemailvalid
IsEmailValid = isemailvalid

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# debugging
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    pass