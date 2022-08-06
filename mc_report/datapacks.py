from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import json

LOAD_TAG_PATH = Path('data/load/tags/functions/load.json')
TEST_FUNCTIONS_PATH = Path('functions/test')
API_FUNCTIONS_PATH = Path('functions/api')
INTERNAL_FUNCTIONS_PATH = Path('functions/internal')


class DatapackTest(ABC):

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        pass

    @abstractmethod
    def run(datapack_directories: list[Path]) -> tuple[list, bool, list]:
        pass

class DatapackException(Exception):
    pass

@dataclass
class Datapack:
    
    path: Path
    main_namespace: str = None
    dependencies: list = field(default_factory=list)

    def __init__(self, path, main_namespace=None, dependencies=None, lantern_load=True):
        if not path.is_dir():
            raise DatapackException(f'Path to datapack does not exist: {path}')
        self.name = path.name.title()
        mc_meta_file = path / 'pack.mcmeta'
        if not mc_meta_file.is_file():
            raise DatapackException(f'Datapack does not have a pack.mcmeta file: {mc_meta_file}')
        
        if lantern_load:
            lantern_load_tag = path / LOAD_TAG_PATH
            if not lantern_load_tag.is_file():
                raise DatapackException(f'Datapack does not have Lantern Load tag: {lantern_load_tag}')
            
            if not main_namespace:
                # print(f'{lantern_load_tag=}')
                with open(lantern_load_tag, 'r') as f:
                    ll_json = json.load(f)
                    last_value = ll_json['values'][-1]
                    function_call = last_value if isinstance(last_value, str) else last_value['id']

                    path_to_call = function_call_to_path(path, function_call)
                    if not path_to_call.is_file():
                        raise DatapackException(f'Lantern load call to {function_call} at {path_to_call} does not exist! Ignore this by explicitly passing in a main namespace')
                    # print(f'{path_to_call=}')
                    self.main_namespace = function_call[1 if function_call.startswith('#') else 0:function_call.find(':')]
            else:
                self.main_namespace = main_namespace

        if not self.main_namespace:
            raise DatapackException('Main namespace must be given if not a Lantern Load datapack')
        
        # valid path
        self.path = path

        if not self.get_namespace_dir().is_dir():
            raise DatapackException(f'Main namespace dir must exist: {self.main_namespace}')

        
        if dependencies:
            self.dependencies = dependencies

    def get_namespace_dir(self) -> Path:
        return self.path / 'data' / self.main_namespace

    def get_functions(self, subpath=None):
        api_dir = self.get_namespace_dir() / 'functions'
        if subpath:
            api_dir = api_dir / subpath
        return api_dir.glob('**/*.mcfunction')

    def __str__(self):
        return Datapack.__recursive_str(self)

    @staticmethod
    def __recursive_str(pack, output='', indent=0):
        indent_str = '  ' * indent
        pack_str = f'Path: {pack.path}'
        if pack.dependencies:
            pack_str += '\nDependencies:'
            for dep in pack.dependencies:
                pack_str = Datapack.__recursive_str(dep, pack_str + '\n', indent + 2)
        indented = '\n'.join(indent_str + line for line in pack_str.split('\n'))
        output += indented
        return output

    @staticmethod
    def is_datapack(path: Path) -> bool:
        try:
            Datapack(path)
            return True
        except DatapackException as e:
            return False


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