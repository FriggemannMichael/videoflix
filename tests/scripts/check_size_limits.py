from __future__ import annotations

import argparse
import ast
from pathlib import Path

MAX_FUNCTION_LOC = 14
MAX_FILE_LOC = 400
SKIP_DIRS = {
    '.git',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    '.venv',
    '__pycache__',
    'tests',
}


def code_loc(lines: list[str], start: int = 1, end: int | None = None) -> int:
    selected = lines[start - 1 : end]
    return sum(
        1 for line in selected if line.strip() and not line.lstrip().startswith('#')
    )


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
        if not any(part in SKIP_DIRS for part in file.parts)
    ]


def function_loc_errors(path: Path, lines: list[str], tree: ast.AST) -> list[str]:
    errors: list[str] = []
    nodes = (
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    )
    for node in nodes:
        function_loc = code_loc(lines, node.lineno, node.end_lineno)
        if function_loc > MAX_FUNCTION_LOC:
            errors.append(function_error(path, node.name, node.lineno, function_loc))
    return errors


def function_error(path: Path, name: str, line_number: int, loc: int) -> str:
    return (
        f"{path}:{line_number}: function '{name}' has "
        f'{loc} LOC, max is {MAX_FUNCTION_LOC}'
    )


def check_file(path: Path) -> list[str]:
    lines = path.read_text(encoding='utf-8').splitlines()
    tree = ast.parse('\n'.join(lines), filename=str(path))
    errors = function_loc_errors(path, lines, tree)
    if code_loc(lines) > MAX_FILE_LOC:
        errors.append(f'{path}: file has {code_loc(lines)} LOC, max is {MAX_FILE_LOC}')
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
