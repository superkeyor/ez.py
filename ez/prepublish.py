"""Generate function catalogs and packaging CLI metadata without changing the version."""

import argparse
import ast
import io
import json
from pathlib import Path
import re
import sys
import tokenize
import tomllib


HERE = Path(__file__).resolve().parent
README_START = "<!-- BEGIN GENERATED FUNCTION CATALOG -->"
README_END = "<!-- END GENERATED FUNCTION CATALOG -->"
SCRIPTS_START = "# BEGIN GENERATED CLI SCRIPTS"
SCRIPTS_END = "# END GENERATED CLI SCRIPTS"
INTRODUCTION = (
    "Cross-platform utilities for shell interaction, paths, files, data, and automation.\n"
    "See each function's docstring for parameters and examples."
)


def _regions(source):
    """Return validated region intervals and their nested labels."""
    regions = []
    stack = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT or token.start[1] != 0:
            continue
        match = re.fullmatch(r"#(region|endregion)(?:\s+(.*))?", token.string)
        if match is None:
            continue
        kind, label = match.groups()
        label = (label or "").strip()
        if kind == "region":
            if not label:
                raise ValueError(f"Unnamed region on line {token.start[0]}.")
            stack.append((token.start[0], label))
        else:
            if not stack:
                raise ValueError(f"Unmatched endregion on line {token.start[0]}.")
            start, expected = stack[-1]
            if label and label != expected:
                raise ValueError(
                    f"Endregion {label!r} on line {token.start[0]} "
                    f"does not match {expected!r}."
                )
            regions.append((start, token.start[0], tuple(name for _, name in stack)))
            stack.pop()
    if stack:
        raise ValueError(f"Unclosed region {stack[-1][1]!r} on line {stack[-1][0]}.")
    return regions


def _region_at(regions, line):
    """Return the innermost region labels containing a source line."""
    matches = [labels for start, end, labels in regions if start < line < end]
    return max(matches, key=len, default=())


def _literal_assignment(tree, name):
    """Find a single module assignment without executing its source."""
    values = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    ]
    if len(values) != 1:
        raise ValueError(f"Expected one literal {name} assignment.")
    return values[0]


def _source_offset(lines, line, column):
    """Convert an AST UTF-8 byte column into a string offset."""
    return sum(len(value) for value in lines[:line - 1]) + len(
        lines[line - 1].encode("utf-8")[:column].decode("utf-8")
    )


def _catalog(source):
    """Collect grouped names, aliases, and summaries from the module's source."""
    tree = ast.parse(source)
    regions = _regions(source)
    groups = {}
    bindings = {}
    imported = {}

    for node in tree.body:
        labels = _region_at(regions, node.lineno)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if len(labels) != 2 or labels[-1] != node.name:
                raise ValueError(f"Function {node.name} needs a topic and its own region.")
            start = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
            if _region_at(regions, start) != labels or _region_at(regions, node.end_lineno) != labels:
                raise ValueError(f"Region does not enclose all of function {node.name}.")
            doc = ast.get_docstring(node)
            if not doc or not doc.strip():
                raise ValueError(f"Function {node.name} has no nonempty docstring.")
            summary = " ".join(doc.strip().splitlines()[0].split())
            entry = [node.name, [], summary]
            groups.setdefault(labels[0], []).append(entry)
            bindings[node.name] = (labels[0], entry)
        elif isinstance(node, ast.ImportFrom) and len(labels) == 1:
            for alias in node.names:
                if alias.name == "*":
                    raise ValueError("Wildcard imports cannot be indexed inside topic regions.")
                name = alias.asname or alias.name
                target = "." * node.level + (node.module or "") + "." + alias.name
                key = (labels[0], target)
                if key not in imported:
                    entry = [name, [], f"Imported from {target}."]
                    imported[key] = entry
                    groups.setdefault(labels[0], []).append(entry)
                else:
                    entry = imported[key]
                    entry[1].append(name)
                bindings[name] = (labels[0], entry)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Name):
            binding = bindings.get(node.value.id)
            if binding is not None:
                group, entry = binding
                if not labels or labels[0] != group:
                    raise ValueError(f"Alias for {node.value.id} is outside its topic region.")
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        entry[1].append(target.id)
                        bindings[target.id] = binding

    if not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in tree.body):
        raise ValueError("No module-level functions found.")
    return groups


def generate_doc(source):
    """Replace only __doc__ with a catalog derived from the module's source."""
    tree = ast.parse(source)
    catalog = [INTRODUCTION, "\n\nFunction catalog (generated by ez/prepublish.py):\n"]
    for group, entries in _catalog(source).items():
        catalog.append(f"\n{group}:\n")
        for name, aliases, summary in entries:
            alias_text = f" (aliases: {', '.join(aliases)})" if aliases else ""
            catalog.append(f"    {name}{alias_text} - {summary}\n")
    value = _literal_assignment(tree, "__doc__")
    if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
        raise ValueError("Expected __doc__ to be a literal string.")
    lines = source.splitlines(keepends=True)
    start = _source_offset(lines, value.lineno, value.col_offset)
    end = _source_offset(lines, value.end_lineno, value.end_col_offset)
    escaped = "".join(
        "\n" if character == "\n" else json.dumps(character, ensure_ascii=False)[1:-1]
        for character in "".join(catalog)
    )
    updated = source[:start] + '"""' + escaped + '"""' + source[end:]
    ast.parse(updated)
    return updated


def generate_readme(source, readme):
    """Replace the marked README catalog, preserving all surrounding content."""
    if readme.count(README_START) != 1 or readme.count(README_END) != 1:
        raise ValueError("Expected one pair of README function catalog markers.")
    start = readme.index(README_START) + len(README_START)
    end = readme.index(README_END)
    if end < start:
        raise ValueError("README function catalog markers are out of order.")
    catalog = ["\n\nGenerated by `ez/prepublish.py` from the same source as `ez.__doc__`.\n"]
    for group, entries in _catalog(source).items():
        catalog.append(f"\n### {group}\n\n| Function | Aliases | Description |\n|---|---|---|\n")
        for name, aliases, summary in entries:
            alias_text = ", ".join(f"<code>{alias}</code>" for alias in aliases)
            summary = (summary.replace("&", "&amp;").replace("<", "&lt;")
                       .replace(">", "&gt;").replace("|", "&#124;"))
            catalog.append(f"| <code>{name}</code> | {alias_text} | {summary} |\n")
    return readme[:start] + "".join(catalog) + "\n" + readme[end:]


def generate_scripts(source, project):
    """Synchronize the marked TOML scripts table from the literal CLI registry."""
    commands = ast.literal_eval(_literal_assignment(ast.parse(source), "_CLI_COMMANDS"))
    if not isinstance(commands, dict) or not commands or any(
        not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name)
        for name in commands
    ):
        raise ValueError("Expected a nonempty CLI registry with valid command names.")
    tomllib.loads(project)
    if project.count(SCRIPTS_START) != 1 or project.count(SCRIPTS_END) != 1:
        raise ValueError("Expected one pair of generated CLI scripts markers.")
    start = project.index(SCRIPTS_START) + len(SCRIPTS_START)
    end = project.index(SCRIPTS_END)
    if end < start:
        raise ValueError("CLI scripts markers are out of order.")
    section = project[start:end].strip().splitlines()
    if not section or section[0] != "[project.scripts]" or any(
        line.lstrip().startswith("[") for line in section[1:]
    ):
        raise ValueError("CLI scripts markers must contain only the [project.scripts] table.")
    lines = ["\n[project.scripts]\n"]
    lines.extend(f'{name} = "ez.ez:_cli"\n' for name in commands)
    updated = project[:start] + "".join(lines) + project[end:]
    parsed = tomllib.loads(updated)
    if parsed["project"]["scripts"] != {name: "ez.ez:_cli" for name in commands}:
        raise ValueError("CLI scripts must be contained in the generated section.")
    return updated


def update_catalogs(path, readme_path, check=False, project_path=None):
    """Validate both catalogs before writing, or check both without changing files."""
    source = path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")
    updated_source = generate_doc(source)
    updated_readme = generate_readme(source, readme)
    outputs = [(path, source, updated_source), (readme_path, readme, updated_readme)]
    if project_path is not None:
        project = project_path.read_text(encoding="utf-8")
        outputs.append((project_path, project, generate_scripts(source, project)))
    if check:
        return all(updated == original for _, original, updated in outputs)
    for target, original, updated in outputs:
        if updated != original:
            target.write_text(updated, encoding="utf-8")
    return True


def update_doc(path, check=False):
    """Update a module's catalog, or report whether it is already current."""
    source = path.read_text(encoding="utf-8")
    updated = generate_doc(source)
    if check:
        return updated == source
    if updated != source:
        path.write_text(updated, encoding="utf-8")
    return True


def main(argv=None):
    """Generate documentation and CLI metadata, or check them without writing."""
    parser = argparse.ArgumentParser(
        description="Generate function catalogs and pyproject.toml CLI metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Notes:\n"
            "    1. No flags or --docs-only: update catalogs and CLI metadata.\n"
            "    2. No mode increments the version or publishes; publish.sh handles releases.\n\n"
            "Example:\n"
            "    python ez/prepublish.py --docs-only\n"
            "    python ez/prepublish.py --check-docs"
        ),
        add_help=False,
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--docs-only", action="store_true", help="Update catalogs and CLI metadata without changing the version.")
    modes.add_argument("--check-docs", action="store_true", help="Check catalogs and CLI metadata without changing any files.")
    parser.add_argument("-h", "--help", action="help", help="Show this help and exit.")
    args = parser.parse_args(argv)
    try:
        if not update_catalogs(
            HERE / "ez.py", HERE.parent / "README.md", check=args.check_docs,
            project_path=HERE.parent / "pyproject.toml",
        ):
            print("Function catalogs or CLI metadata are stale; run ez/prepublish.py --docs-only.", file=sys.stderr)
            return 1
        print("Catalogs and CLI metadata are current." if args.check_docs
              else "Catalogs and CLI metadata updated; version unchanged.")
    except (OSError, ValueError, SyntaxError, tokenize.TokenError) as exc:
        print(f"Prepublish failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
