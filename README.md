# ez

[![PyPI Version](https://img.shields.io/pypi/v/ez.svg)](https://pypi.org/project/ez/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ez.svg)](https://pypi.org/project/ez/)
[![License: GPLv3+](https://img.shields.io/pypi/l/ez.svg)](https://www.gnu.org/licenses/gpl-3.0.html)

A cross-platform Python utility library for easy shell interaction and common programming tasks on Linux, macOS, and Windows.

---

## Installation

```bash
pip install ez
```

Requires Python 3.11+.

---

## Quick Start

```python
from ez import *

# File operations
files = ls('~/Documents', r'\.py$')
cp('source.txt', '~/backup/')
mv('old_name.txt', 'new_name.txt')
rm('temp/')

# Path utilities
print(cwd())                            # current working directory
print(jp('~', 'Documents', 'file'))     # join path components
print(sp('/path/to/file.txt'))          # => ['/path/to', 'file', '.txt']

# Execute shell commands
execute('ls -la')
output = execute2('echo hello')
esp('echo %s', 'world')

# Read/write spreadsheets
data = readx('data.xlsx')
savex('output.xlsx', data, header=['Name', 'Age'])
```

---

## Features

### File & Directory Operations

| Function | Description |
|---|---|
| `ls([path[, regex]], full=True, dotfile=False)` | List files in a directory, filtered by regex. |
| `lsd([path[, regex]], full=False, dotfolder=False)` | List subdirectories. |
| `fls([path[, regex]])` | Recursively list all files (walks subdirectories). Regex matches filename only, case-sensitive. |
| `mkdir(path)` | Create a directory and any missing parents (like `mkdir -p`). |
| `cp(src, dst)` | Copy file(s) or a folder; supports wildcards and vectorization. |
| `mv(src, dst)` | Move file(s) or a folder; supports wildcards and vectorization. |
| `rm(path)` | Delete a file or folder; supports wildcards and vectorization. |
| `rn(old, new)` | Rename a file or directory. |
| `exists(path)` | Check whether a path exists (returns `0` or `1`). |
| `tree([path, sum=True, save=None, sort=True, case=True])` | Print a directory tree. `sum=True` shows only folders; `sum=False` includes files. |

### Path Utilities

| Function | Description |
|---|---|
| `fullpath(path)` / `fp(path)` | Resolve the full absolute path (expands `~`, `..`). |
| `pwd()` / `cwd()` | Return the current working directory. |
| `csd()` | Return the directory of the currently running script. |
| `csf()` | Return the current script filename without its extension. |
| `parentdir(path)` / `pr(path)` | Return the parent directory of a path. |
| `joinpath(*parts)` / `jp(*parts)` | Join path components; supports vectorization. |
| `splitpath(path)` / `sp(path)` | Split a path into `[directory, filename, extension]`; supports vectorization. |
| `cd(path)` | Change the current working directory. |
| `stepfolder(n)` | Navigate up or down the directory hierarchy by *n* levels. |

### String Utilities

| Function | Description |
|---|---|
| `trim(string, how[, chars])` | Strip whitespace or specific characters. |
| `quote(string)` | Wrap a string in quotes. |
| `join(sep, *strings)` / `join(sep, array)` | Concatenate strings with a separator; supports vectorization. |
| `sort(array)` | Sort a list. |
| `replace(lst, item, replacement)` | Replace an element in a list. |
| `remove(lst, item)` | Remove an element from a list. |

### Shell Execution

| Function | Description |
|---|---|
| `execute(cmd)` | Run a shell command without capturing output (`subprocess.call`). |
| `execute1(cmd)` | Run a shell command and discard its output. |
| `execute2(cmd)` | Run a shell command and return the captured output (`subprocess.Popen`). |
| `sprintf(fmt, *args, **kwargs)` | Format a string (like C's `sprintf`). |
| `esp(fmt, ...)` / `esp1(...)` / `esp2(...)` | Execute a `sprintf`-formatted shell command. |
| `espR(fmt, ...)` / `espR1(...)` / `espR2(...)` | Execute `sprintf`-formatted R code. |
| `evaluate(exp)` | Evaluate and execute a shell expression. |

### Spreadsheet & Data I/O

| Function | Description |
|---|---|
| `readx(path, sheet=0, r=[1,], c=None)` | Read a `.xlsx`, `.xls`, or `.csv` file into a list. |
| `savex(path, data, header=None, delimiter=",", sheet_name='Sheet1')` | Write a list of lists to a `.xlsx`, `.xls`, or `.csv` file. |

### Regular Expressions

| Function | Description |
|---|---|
| `regexp(string, pattern)` | Return `[starts, ends]` match positions; also accepts `method='split'` or `method='match'`. |
| `regexpi(string, pattern)` | Case-insensitive variant of `regexp`. |
| `regexprep(string, pattern, replace, count=0)` | Replace pattern matches in a string. |
| `regexprepi(string, pattern, replace, count=0)` | Case-insensitive variant of `regexprep`. |

### Utility & Debugging

| Function | Description |
|---|---|
| `debug(1/0)` | Toggle simulation mode. `1` simulates `cp`, `mv`, and `execute` (prints without running); `0` executes for real. |
| `error(msg)` | Raise an error with a message. |
| `pprint(text, color='green')` | Color-coded console print. |
| `ppprint(obj)` | Pretty-print arbitrary Python data structures. |
| `beep()` | Emit a system beep. |
| `which(name)` | Locate a module, or show which Python interpreter is active (e.g., `which('python')`). |
| `help(name)` / `doc(name)` | Print a module, class, or function docstring. |
| `ver(pkg)` / `version(pkg)` | Check a package's installed version (`pkg` can be `'python'`). |
| `whos([name])` | List imported functions and packages. |
| `with nooutput():` | Context manager that suppresses stdout within the block. |

### Logging

| Function | Description |
|---|---|
| `logon(file="log.txt", mode='a', status=True, timestamp=True)` | Begin logging stdout to a file. |
| `logoff()` | Stop logging. |

### Randomization

| Function | Description |
|---|---|
| `Randomize(x)` / `randomize(x)` | Seed the random number generator. |
| `RandomizeArray(lst)` / `randomizearray(lst)` | Shuffle a list in place. |
| `Random(a, b)` / `random(a, b)` | Return a random integer `N` such that `a ≤ N ≤ b`. |
| `RandomChoice(seq)` / `randomchoice(seq)` | Return a random element from a sequence. |
| `Permute(iterable)` / `permute(iterable)` | Return all permutations as a list. |

### Set Operations

All set operations preserve the original order of elements.

| Function | Description |
|---|---|
| `unique(seq)` | Remove duplicates. `unique('abracadaba')` → `['a', 'b', 'r', 'c', 'd']` |
| `union(seq1, seq2)` | Set union. |
| `intersect(seq1, seq2)` | Set intersection. |
| `setdiff(seq1, seq2)` | Elements in `seq1` not in `seq2`. Note: `setdiff(a, b) ≠ setdiff(b, a)` in general. |
| `duplicate(seq)` | Return only elements that appear more than once. `duplicate([1,5,2,3,2,1,5,6,5])` → `[2, 1, 5]` |

### Clipboard

| Function | Description |
|---|---|
| `SetClip(content)` / `setclip(content)` | Write content to the system clipboard. |
| `GetClip()` / `getclip()` | Read content from the system clipboard. |

### Miscellaneous

| Function | Description |
|---|---|
| `num(string)` | Convert a string to a number. |
| `isempty(s)` | Check if a value is empty. |
| `iff(expr, result1, result2)` / `ifelse(...)` | Inline conditional (ternary) expression. |
| `clear(module, recursive=False)` | Reload a module. |
| `lines(path='.', pattern='\.py$', recursive=True)` | Count lines of code (including empty lines) matching a file pattern. |
| `keygen(length=8, complexity=3)` | Generate a random key string. |
| `hashes(filename)` | Calculate and print a file's MD5 and SHA1 hashes; memory-efficient for large files. |
| `encoding_detect(path)` | Detect the character encoding of a file. |
| `encoding_convert(path)` | Convert a file's encoding. |
| `JDict()` | A custom ordered dictionary with convenient attribute access and helper methods. Use `help(JDict)` for details. |
| `Moment(timezone)` | Return the current datetime in a specified timezone, or a local naive datetime if omitted. |

### Pipe

Chain operations using a pipe-style syntax:

```python
# Basic pipe
[1, 2, 3, 0] > ez.pipe | len | str

# Countdown example
ez.pipe | (range, -1) | reversed | ez.pipetools.foreach('{0}...') | ' '.join | '{0} boom'
```

---

## General Notes

- Almost all path-related commands support `~`, `..`, `.`, `?`, and `*`. The exceptions are `ls` and `fls`, which use regular expressions for filtering.
- File operations target symbolic links themselves, not the underlying files they point to.

---

## License

[GNU General Public License v3 or later (GPLv3+)](https://www.gnu.org/licenses/gpl-3.0.html)
