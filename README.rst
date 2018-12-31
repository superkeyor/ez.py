This module is for easy interaction with linux, Mac OS X, Windows shell.
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

trim(string,how[,chars]) quote(string)
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

tree([path[, sum=True, save=None, sort=True, case=True]) # Prints a directory tree structure. 
    sum=True (default) prints only folders, i.e., print less to show the big structure
    sum=False prints files plus folders

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
pinyin() pinyinauthor()
encoding_detect(), encoding_convert()
hanzifreq()
pipe usage: # http://0101.github.io/pipetools/doc/
    # result = [1,2,3,0] > ez.pipe | len | str
    # countdown = ez.pipe|(range, -1)|reversed|ez.pipetools.foreach('{0}...')|' '.join|'{0} boom'; countdown(5)





To avoid typing email password each time, place a file named pygmailconfig.py with
EMAIL = 'someone@gmail.com'
PASSWORD = 'abcdefghik'
or better pygmailconfig.pyc
in the site-packages/ez folder, check with ez.which('ez')
The functions will no longer need email/password and become like this
Mail(to, subject, body, attach=None), AddEvent(event), Sheet(fileName)

Mail([EMAIL, PASSWORD, ] to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
        to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
        reply_to: 'a@a.com'
        attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
AddEvent([EMAIL, PASSWORD, ] event)     on DATE at TIME for DURATION in PLACE

Sheet([EMAIL, PASSWORD, ] fileName)
    returns a sheet object representing "Sheet 1"

    your google account doesn't have to the owner of this sheet, as long as you can edit it.
    but you need to initialize/create this sheet and maybe the header by hand to begin with
    the header could have spaces, ? etc, and when they are used as the keywords of dictionary, they are all converted to lowercase and all illegal characters are removed e.g. Delayed Test_date?  --> delayedtestdate

    fileName should be unique, can have spaces


GetRows(query=None, order_by=None,
        reverse=None, filter_func=None)
    :param query:
        A string structured query on the full text in the worksheet.
          [columnName][binaryOperator][value]
          Supported binaryOperators are:
          - (), for overriding order of operations
          - = or ==, for strict equality
          - <> or !=, for strict inequality
          - and or &&, for boolean and
          - or or ||, for boolean or.
    :param order_by:
        A string which specifies what column to use in ordering the
        entries in the feed. By position (the default): 'position' returns
        rows in the order in which they appear in the GUI. Row 1, then
        row 2, then row 3, and so on. By column:
        'column:columnName' sorts rows in ascending order based on the
        values in the column with the given columnName, where
        columnName is the value in the header row for that column.
    :param reverse:
        A string which specifies whether to sort in descending or ascending
        order.Reverses default sort order: 'true' results in a descending
        sort; 'false' (the default) results in an ascending sort.
    :param filter_func:
        A lambda function which applied to each row, Gets a row dict as
        argument and returns True or False. Used for filtering rows in
        memory (as opposed to query which filters on the service side).
    :return:
        A list of row dictionaries.


UpdateRow(row_data):
    Update Row (By ID).

    Only the fields supplied will be updated.
    :param row_data:
        A dictionary containing row data. The row will be updated according
        to the value in the ID_FIELD.
    :return:
        The updated row.


UpdateRowByIndex(index, row_data):
    Update Row By Index

    :param index:
        An integer designating the index of a row to update (zero based).
        Index is relative to the returned result set, not to the original
        spreadseet.
    :param row_data:
        A dictionary containing row data.
    :return:
        The updated row.


InsertRow(row_data):
    Append Row at the end

    :param row_data:
        A dictionary containing row data.
    :return:
        A row dictionary for the inserted row.


DeleteRow(row):
    Delete Row (By ID).

    Requires that the given row dictionary contains an ID_FIELD.
    :param row:
        A row dictionary to delete.


DeleteRowByIndex(index):
    Delete Row By Index

    :param index:
        A row index. Index is relative to the returned result set, not to
        the original spreadsheet.


DeleteAllRows():
    Delete All Rows
