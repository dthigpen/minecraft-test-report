from abc import ABC, abstractmethod
from pathlib import Path
import re

class DatapackTest(ABC):

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        pass

    @abstractmethod
    def run(datapack_directories: list[Path]) -> tuple[list, bool, list]:
        pass

def get_functions(datapack_path: Path, includes=None, excludes=None):
    ALL_MCFUNCTIONS = '**/data/*/functions/**/*.mcfunction'
    if not includes:
        includes = []
    if not excludes:
        excludes = []
    for p in datapack_path.glob(ALL_MCFUNCTIONS):
        # default to pass if no includes
        passes_includes = len(includes) == 0
        for inc in includes:
            if re.match(inc, str(p)) is not None:
                passes_includes = True
                # don't check additional includes
                break
        passes_excludes = True
        if passes_includes:
            for exc in excludes:
                if re.match(exc, str(p)) is not None:
                    passes_excludes = False
                    # don't check additional excludes
                    break
            if passes_excludes:
                yield p
            
def path_to_function_call(function_path: Path) -> str:
    path_parts = list(function_path.parts[function_path.parts.index('data') + 1:])
    namespace = path_parts.pop(0) # namespace
    path_parts.pop(0) # functions
    path_parts.pop() # actual function file
    path_parts.append(function_path.stem)
    return f'{namespace}:{"/".join(path_parts)}'

def function_call_to_path(datapack_path: Path, function_call: str) -> Path:
    is_tag = function_call.startswith('#')
    namespace = function_call[1 if is_tag else 0:function_call.find(':')]
    function_or_tag_dir = 'tags/functions' if is_tag else 'functions'
    file_ext = '.json' if is_tag else '.mcfunction'
    load_file = function_call[function_call.find(':') + 1:] + file_ext
    return datapack_path / 'data' / namespace / function_or_tag_dir / load_file

def sort_table(table, sort_funct, reverse=True):
    header = table.pop(0)
    table.sort(key=sort_funct, reverse=reverse)
    table.insert(0, header)

def list_to_table_cell(items):
    return f'<br/>'.join(items)