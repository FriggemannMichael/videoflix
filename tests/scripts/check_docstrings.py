from __future__ import annotations

import argparse
import ast
from pathlib import Path

SKIP_DIRS = {
    '.git',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    '.venv',
    '__pycache__',
    'migrations',
    'tests',
}
SKIP_FILES = {'__init__.py', 'manage.py'}
DOCUMENTED = ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


def iter_python_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == '.py':
            files.append(path)
        elif path.is_dir():
            files.extend(valid_python_files(path))
    return sorted(files)


def valid_python_files(path: Path) -> list[Path]:
    return [
        file
        for file in path.rglob('*.py')
        if file.name not in SKIP_FILES
        and not any(part in SKIP_DIRS for part in file.parts)
    ]


def definition_errors(path: Path, tree: ast.AST) -> list[str]:
    return [
        f"{path}:{node.lineno}: '{node.name}' has no docstring"
        for node in ast.walk(tree)
        if isinstance(node, DOCUMENTED) and not ast.get_docstring(node)
    ]


def check_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    errors = definition_errors(path, tree)
    if not ast.get_docstring(tree):
        errors.insert(0, f'{path}:1: module has no docstring')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*', type=Path, default=[Path('.')])
    errors = [
        error
        for path in iter_python_files(parser.parse_args().paths)
        for error in check_file(path)
    ]
    print('\n'.join(errors)) if errors else None
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
