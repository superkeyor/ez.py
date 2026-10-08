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

### Documents to Markdown

```python
import ez

markdown = ez.pptx2md('talk.pptx')  # prints to stdout and returns the Markdown
markdown = ez.pptx2md(
    'talk.pptx', note=True, slides='1-3,5', markers=False,
    images=True, output='talk.md', overwrite=True,
)
```

All four converters return the Markdown string and print it when `output=None`.
With `output='file.md'`, they write UTF-8 instead of printing. Existing output files
raise `FileExistsError` unless `overwrite=True`; replacing the input document is
always rejected, including symlink/hard-link aliases.

#### PowerPoint

| Argument (default) | CLI flag | Effect |
|---|---|---|
| `note=False` | `-n`, `--note` | Include speaker notes. |
| `slides=None` | `-s`, `--slides` | Select 1-based slides, e.g. `1-3,5`; default is all slides. |
| `markers=True` | `--no-markers` | Remove `<!-- Slide number: N -->` comments and separate slides with `---`. |
| `images=False` | `--images` | Embed images as base64 data URIs instead of filename references. |
| `output=None` | `-o`, `--output` | Write UTF-8 Markdown to a file instead of stdout. |
| `overwrite=False` | `-f`, `--force` | Allow replacing an existing output file. |

Selections retain presentation order, ignore duplicates, and preserve original
slide numbers. Invalid or out-of-range selections raise `ValueError`. Existing
output files raise `FileExistsError` unless overwriting is enabled. The input
presentation is never overwritten. Filename image references do **not** extract
image files; use `images=True` for self-contained Markdown.

```bash
pptx2md talk.pptx -n -s 1-3,5 --images -o talk.md
pptx2md --help
```

#### Word

```python
markdown = ez.docx2md('report.docx', images=True, output='report.md')
```

`images=False` is the default. Use `--images` to preserve complete base64 image
URIs; otherwise MarkItDown abbreviates them into unusable image references.
Supported headings, lists, tables, and links are converted, not exact page layout.

```bash
docx2md report.docx --images -o report.md
```

#### Excel

```python
markdown = ez.xlsx2md(
    'data.xlsx', sheets=['Annual Sales', 'Summary'], formulas=False,
    headers=True, output='data.md',
)
```

| Argument (default) | CLI flag | Effect |
|---|---|---|
| `sheets=None` | `-s`, `--sheets NAME [NAME ...]` | Select exact worksheet names; default is all worksheets, including hidden ones. |
| `formulas=False` | `--formulas` | Emit formula strings instead of cached values. |
| `headers=True` | `--no-headers` | Generate column-letter headers and include the first row as data. |

Selections retain workbook order and ignore duplicates; unknown names raise
`ValueError`. Each worksheet has a heading and a Markdown table; empty worksheets
have only a heading. Trailing empty rows/columns are omitted. Images, charts,
styles, and macros are not extracted; merged cells are not expanded.

Formulas are **not evaluated**. Missing cached formula values produce a warning
and empty cells. Calculate and save the workbook in Excel/LibreOffice first, or
use `formulas=True` to emit the formulas themselves.

```bash
xlsx2md data.xlsx --sheets "Annual Sales" Summary -o data.md
xlsx2md data.xlsx --formulas --no-headers
```

#### PDF

```python
markdown = ez.pdf2md('paper.pdf', pages='1-3,5', markers=False, output='paper.md')
```

| Argument (default) | CLI flag | Effect |
|---|---|---|
| `pages=None` | `-p`, `--pages` | Select 1-based page ranges; default is all pages. |
| `markers=True` | `--no-markers` | Remove `<!-- Page number: N -->` comments and separate pages with `---`. |

Selections retain document order and original page numbers. This is text-based
extraction, **not OCR**: scanned/blank pages can have no text. Images are not
extracted; exact layout/table reconstruction is not guaranteed. Decrypt PDFs
requiring a password before conversion.

```bash
pdf2md paper.pdf -p 1-3,5 -o paper.md
```

#### Batch conversion

The installed commands accept multiple files, folders, and wildcard patterns.
Each Python converter still processes one file per call.

```bash
pptx2md *.pptx --output-dir markdown --images
docx2md first.docx second.docx --output-dir markdown
pdf2md reports --recursive --output-dir markdown
pdf2md "reports/**/*.pdf" --recursive --output-dir markdown
xlsx2md workbooks --output-dir markdown --sheets Summary
```

- More than one distinct input requires `--output-dir DIR`; `-o FILE` is only
  for one input and cannot be combined with `--output-dir`.
- A single input without `--output-dir` retains the original stdout/`-o` behavior.
- Folders are scanned for the command's file extension, case-insensitively.
  Use `--recursive` for nested folders or quoted `**` patterns. Recursive
  discovery does not follow directory symlinks.
- Output folders are created as needed. Structure is preserved relative to the
  common ancestor of input roots: a folder's root is itself, an explicit file's
  root is its parent, and a wildcard's root is its non-wildcard directory prefix.
  For example, `pdf2md reports --recursive --output-dir markdown` maps
  `reports/a/report.pdf` to `markdown/a/report.md`. Explicit inputs
  `a/report.pdf b/report.pdf` map to `markdown/a/report.md` and
  `markdown/b/report.md`, rather than overwriting one another.
- Repeated files and file aliases are converted once. Outputs colliding with
  another destination or any source document are rejected, even with `--force`.
- All conversion options apply to every input. Discovery/conversion/output
  failures are reported to stderr while other files continue. A final summary
  reports succeeded/failed counts; any failure produces a nonzero exit status.
  Unmatched patterns and folders with no matching files are errors, not silent
  successes. Unexpected programming errors remain visible.
- `--force` allows replacing existing output files; otherwise they are reported
  as failures. Batch Markdown goes to files, not stdout.

#### Installed commands and future CLI tools

Install this version of the package to generate all four commands:

```bash
python -m pip install .
# Or, for local development:
python -m pip install -e .
```

Activate the Python environment containing `ez`, or put its executable directory
on `PATH`. All commands support `-o`/`--output`, `-f`/`--force`, and `-h`/`--help`.
Running any converter command without arguments shows help and exits successfully.
Importing or directly running `ez/ez.py` does not launch a converter CLI.

`_CLI_COMMANDS` in `ez/ez.py` is the single registry of exported tools. To expose
another tool, add its function and a registry entry with `function`, `description`,
`arguments`, `notes`, and `examples`; optional `groups` reuse argument groups.
Each argument is a pair of flag/name strings and an argparse-options dictionary.
Use the strings `"str"`, `"int"`, or `"float"` for typed arguments. Unspecified
options are omitted from the function call, preserving the function's defaults.
Command names may differ from function names; registered targets must accept the
parsed arguments as keywords. The dispatcher ignores normal return values and
exits successfully after a successful call.

Batch support is opt-in: the converter entries also specify `batch` metadata
(`input` parameter, supported `extension`, and expected document `errors`) and
use the shared `batch` argument group. Tools without this metadata retain normal
single-call dispatch.

`setup.py` reads the literal registry without importing runtime dependencies and
generates console entry points targeting the general `_cli` dispatcher. Reinstall
the package after adding a command. No new wrapper files or shell functions are
needed. Converter dependencies (MarkItDown, openpyxl, PyMuPDF, and python-pptx)
are already declared in the package.

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
