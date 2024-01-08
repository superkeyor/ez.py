To make it easy to interact with Linux, Mac OS, Windows shell.
===============================================================

.. code-block:: none

    jerryzhujian9_at_gmail.com
    Tested under python 3.11
    To see your python version
    in terminal: python -V
    or in python: import sys; print (sys.version)

Install
-------

also hosted at https://pypi.python.org/pypi/ez

.. code-block:: none

    pip install ez

General note
------------

- Almost all commands support the usage of '~', '..', '.', '?', '*' in path (ls, fls only support regular expression).
- Symbolic link itself is the target of file operations; the actual file should be safe.

Function list
-------------

- ``debug(1/0)``
    - 0 = everything will be actually executed
    - 1 = simulate operations of cp, mv, execute; other commands will be actually performed. Will print out simulated commands, useful for debugging and for counting files when necessary.

- ``error(msg)``

- ``readx(path, sheet=0, r=[1,], c=None)`` - Read xlsx, xls file into a list
- ``savex(path, data, header=None, delimiter=",", sheet_name='Sheet1')`` - Write a list of list to a xlsx (xlsxwriter), xls(xlwt), csv file

- ``fullpath(path)`` ``fp()``
- ``pwd()`` or ``cwd()``  - Returns current working directory.
- ``csd()`` - Returns full path of current script directory, i.e., the directory where the running script is. 
- ``csf()`` 0 Returns current script name without ext.
- ``parentdir(path)`` ``pr()`` - Returns the parent directory of a path.
- ``joinpath(path1[, path2[, ...]])``  ``jp()`` - Returns the joined path. Supports vectorization.
- ``splitpath(path)`` ``sp()`` - Returns a list of path elements: [path, file, ext]. Supports vectorization.
- ``cd(path)`` - Changes to a new working directory.
- ``stepfolder(-1)``

- ``trim(string,how[,chars])`` ``quote(string)``
- ``join(sep, string1, string2)``, ``join(sep, array)`` - Glues together strings with sep. Supports vectorization.
- ``sort(array)``
- ``replace(theList, theItem, replacement)``, ``remove(theList, theItem)``

- ``ls([path[, regex]], full=True, dotfile=False)`` - Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
- ``lsd([path[, regex]], full=False, dotfolder=False)``
- ``fls([path[, regex, dotf=False]])`` - Returns a list of files with their full paths in flattened path (i.e., walk each subdirectory). The filter only works for the short file name, not for the full file name, i.e., the file name itself not its full path. Regular expression is case-sensitive. Usage examples: ``ls(); ls(cwd()); ls(cwd(), "\.py$")``

- ``mkdir("path/to/a/directory")`` - Makes a directory (also any one of the "path", "to", "a" directories if not exists).
- ``rn(old, new)`` - Renames old to new.
- ``exists(path)`` - Returns the existence of path (0 or 1).
- ``rm(path)`` - Deletes a file or folder. Supports wildcards, vectorization.
- ``cp(source, destination)`` - Copies source file(s) or folder to destination. Supports wildcards, vectorization.
- ``mv(source, destination)`` - Moves source file(s) or folder to destination. Supports wildcards, vectorization.

- ``sprintf(formatString, *args, **kwargs)``
- ``evaluate(exp)`` - Executes a shell command. ``execute``, ``execute1``, ``execute2``: no capture output (`subprocess.call`), `execute1` discards (does not return) captured output, `execute2` captures output (`subprocess.Popen`).
- ``esp``, ``esp1``, ``esp2`` - Execute sprintf shell commands.
- ``espR``, ``espR1``, ``espR2`` - Execute sprintf R codes.
- ``with nooutput():`` - Used to suppress output in stdout. Example: `print 'this will not be printed in stdout'`.
- ``pprint(text, color='green')`` - Color print. `ppprint()` is used to "pretty-print" arbitrary Python data structures.
- ``beep()`` - Beeps to notify user.
- ``which(name)`` - Prints where a module is and in which module a function is. For example, `which('python')` returns which Python is being used.
- ``help(name)``/``doc(name)`` - Prints the documentation string of a module/class/function. For modules, use explicit docstring with `__doc__`. For functions/classes, use implicit docstring within the function/class definition.
- ``ver(package_name)``, ``version(package_name)`` - Checks a package's version. `package_name` could be 'python'.
- ``whos(name)``, ``whos()`` - Lists imported functions/packages.

- ``logon(file="log.txt", mode='a', status=True, timestamp=True)``, ``logoff()``
- ``tree([path[, sum=True, save=None, sort=True, case=True]])`` - Prints a directory tree structure. `sum=True` (default) prints only folders, showing the larger structure. `sum=False` prints files plus folders.

- ``[starts, ends] = regexp(string, pattern)``, ``regexp(string, pattern, method='split/match')``, ``regexpi``
- ``regexprep(string, pattern, replace, count=0)``, ``regexprepi``

- ``iff(expression, result1, result2)``, ``ifelse()``
- ``clear(module, recursive=False)``

- ``num(string)``
- ``isempty(s)``

- ``Randomize(x)``, ``randomize(x)`` - Sets a randomization seed.
- ``RandomizeArray(list=[])``, ``randomizearray(list=[])`` - Shuffles a list in place.
- ``Random(a, b) random(a, b)`` - Returns a random integer N such that a <= N <= b.
- ``RandomChoice(seq)``, ``randomchoice(seq)`` - Returns a random element from a sequence.
- ``Permute(iterable=[])``, ``permute(iterable=[])`` - Returns permutations in a list.
- ``unique(seq)``, ``union(seq1, seq2)``, ``intersect(seq1, seq2)``, ``setdiff(seq1, seq2)`` - Operates on sequences in their original order. Note: `setdiff(seq1, seq2)` may not be equal to `setdiff(seq2, seq1)`. Examples: 
  - ``unique('abracadaba')`` results in ``['a', 'b', 'r', 'c', 'd']``.
  - ``setdiff('abracadaba', 'simsalabim')`` results in ``['r', 'c', 'd']``.
- ``duplicate(seq)`` - Returns a list of duplicated elements in original order. Example: `duplicate([1,5,2,3,2,1,5,6,5,5,5])` yields `[2, 1, 5]`.

- ``JDict()`` - Jerry's dictionary, a customized ordered dictionary class with convenient attributes and methods. Use `help(JDict)` for more information.
- ``Moment(timezone)`` - Generates the current datetime in specified timezone, or local naive datetime if omitted.

- ``SetClip(content)``, ``setclip(content)`` - Copy/Write something to the current clipboard.
- ``GetClip()``, ``getclip()`` - Read out content from the current clipboard and assign it to a variable.

- ``lines(path='.', pattern='\\.py$|.ini$|\\.c$|\\.h$|\\.m$', recursive=True)`` - Counts lines of codes, including empty lines.
- ``keygen(length=8, complexity=3)`` - Generates a random key.
- ``hashes(filename)`` - Calculates/Prints a file's md5 and sha1 hashes; can handle big files in a memory-efficient way.
- ``pinyin()``, ``pinyinauthor()``
- ``encoding_detect()``, ``encoding_convert()``
- ``hanzifreq()``

- Pipe usage: 
  - Example: ``[1,2,3,0] > ez.pipe | len | str``.
  - Countdown example: ``ez.pipe|(range, -1)|reversed|ez.pipetools.foreach('{0}...')|' '.join|'{0} boom'``; ``countdown(5)``.

Email and Password Configuration
--------------------------------
To avoid typing email and password each time, place a file named `pygmailconfig.py` with the following contents in the `site-packages/ez` folder (check location with `ez.which('ez')`):
- EMAIL = 'someone@gmail.com'
- PASSWORD = 'abcdefghik'

Alternatively, use `pygmailconfig.pyc` for better security.

With this configuration, the functions will no longer require explicit email/password input:

- ``Mail(to, subject, body, attach=None)``
- ``AddEvent(event)``
- ``Sheet(fileName)``

Function Details
----------------
- ``Mail([EMAIL, PASSWORD, ] to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)``
  - to/bcc/cc: Can be a list like `['a@a.com','b@b.com']` or a single string `'a@a.com, b@b.com'`.
  - reply_to: For example, `'a@a.com'`.
  - attachment: Either a single file `'file_in_working_dir.txt'` or a list like `['a.txt','b.py','c.pdf']`.

- ``AddEvent([EMAIL, PASSWORD, ] event)``
  - Event details like date, time, duration, and place.

- ``Sheet([EMAIL, PASSWORD, ] fileName)``
  - Returns a sheet object representing "Sheet 1".
  - Your Google account does not need to be the owner of the sheet, as long as you have edit access.
  - Initialization/creation of the sheet and its header may need to be done manually.
  - Headers with spaces or special characters are normalized (e.g., 'Delayed Test_date?' becomes 'delayedtestdate').
  - Ensure `fileName` is unique and can contain spaces.

GetRows Function
----------------
- ``GetRows(query=None, order_by=None, reverse=None, filter_func=None)``
  - :param query: A structured query on the full text in the worksheet. Supported binary operators include `()`, `=`, `==`, `<>`, `!=`, `and`, `&&`, `or`, `||`.
  - :param order_by: Specifies the column for ordering entries. 'position' (default) or 'column:columnName'.
  - :param reverse: Sort order, 'true' for descending, 'false' (default) for ascending.
  - :param filter_func: A lambda function for filtering rows in memory.
  - :return: A list of row dictionaries.

UpdateRow Function
------------------
- ``UpdateRow(row_data)``
  - Updates a row by ID.
  - :param row_data: A dictionary containing row data, updated according to the ID_FIELD.
  - :return: The updated row.

UpdateRowByIndex Function
-------------------------
- ``UpdateRowByIndex(index, row_data)``
  - Updates a row by its index.
  - :param index: The index of the row to update (zero-based).
  - :param row_data: A dictionary containing row data.
  - :return: The updated row.

InsertRow Function
------------------
- ``InsertRow(row_data)``
  - Appends a row at the end.
  - :param row_data: A dictionary containing row data.
  - :return: A dictionary for the inserted row.

DeleteRow Function
------------------
- ``DeleteRow(row)``
  - Deletes a row by ID.
  - :param row: A row dictionary to delete.

DeleteRowByIndex Function
-------------------------
- ``DeleteRowByIndex(index)``
  - Deletes a row by index.
  - :param index: A row index, relative to the returned result set.

DeleteAllRows Function
----------------------
- ``DeleteAllRows()``
  - Deletes all rows in the spreadsheet.
