from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from .datapacks import Datapack

def get_datapacks(dir: Path, lantern_load=True) -> list[Datapack]:
    return [Datapack(f) for f in dir.iterdir() if Datapack.is_datapack(f)]

@dataclass
class Statistic:
    name: str
    total: int
    count: int
    note: str = ''
    data: list = field(default_factory=list)
    

    def get_percent_str(self) -> str:
        percent = '-'
        if self.total > 0:
            percent = f'{round(self.count / self.total * 100)}%'
        return percent
    
def get_test_coverage_stat(datapack: Datapack):
    all_function_paths = set(datapack.get_functions())
    test_function_paths = set(datapack.get_functions('test'))
    non_test_functions_paths = all_function_paths.difference(test_function_paths)
    testable_function_paths = set()  # non test functions not called in other non test functions

    for non_test_path in non_test_functions_paths:
        call = datapacks.path_to_function_call(non_test_path)
        # look through all non-test functions to eliminate from testable pool
        for p in non_test_functions_paths:
            # skip own file
            if call != datapacks.path_to_function_call(p):
                continue
            # check if mcfunction file has this call
            if called_in_file(call, p):
                testable_function_paths.add(non_test_path)
                break
    called_from_tests = set()
    for testable_path in testable_function_paths:
        call = datapacks.path_to_function_call(testable_path)
        for test_path in test_function_paths:
            if called_in_file(call, test_path):
                called_from_tests.add(testable_path)
                break
    
    uncalled_testables = test_function_paths.difference(called_from_tests)
    
    testable_count = len(test_function_paths)
    covered_count = len(called_from_tests)
    return Statistic('Test Coverage', testable_count,covered_count, data=uncalled_testables)
    
    
def called_in_file(call: str, file: Path):
    # check if mcfunction file has this call
    with open(file, 'r') as f:
        for line in f.readlines():
            if call in line.strip() and not line.strip().startswith('#'):
                return True