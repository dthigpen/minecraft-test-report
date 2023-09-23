from pathlib import Path
from .test_util import DatapackTest, get_functions, list_to_table_cell, path_to_function_call, path_to_function_call, sort_table


class CoverageTest(DatapackTest):

    def __init__(self, all_includes=None, all_excludes=None, test_includes=None, test_excludes=None) -> None:
        super().__init__()
        self.all_includes = all_includes
        self.all_excludes = all_excludes
        self.test_includes = test_includes
        self.test_excludes = test_excludes

    @staticmethod
    def get_name() -> str:
        return 'Coverage Test'
    
    def run(self, datapack_dirs: list) -> list:
        summary_table = [['Datapack', 'Tested', 'Total', 'Percent']]
        details_table = [['Datapack', 'Uncalled']]
        for datapack_dir in datapack_dirs:

            all_function_paths = set([p for p in get_functions(datapack_dir,includes=self.all_includes,excludes=self.all_excludes)])
            test_function_paths = set([p for p in get_functions(datapack_dir,includes=self.test_includes,excludes=self.test_excludes)])
            non_test_functions_paths = all_function_paths.difference(test_function_paths)
            paths_called_in_another_function = set()  # non test functions not called in other non test functions
            for non_test_path in non_test_functions_paths:
                call = path_to_function_call(non_test_path)
                # look through all non-test functions to eliminate from testable pool
                for p in non_test_functions_paths:
                    # skip own file
                    if call == path_to_function_call(p):
                        continue
                    if called_in_file(call, p):
                        paths_called_in_another_function.add(non_test_path)
                        break
            paths_not_called_in_another_function = non_test_functions_paths.difference(paths_called_in_another_function)
            called_from_tests = set()
            for testable_path in paths_not_called_in_another_function:
                call = path_to_function_call(testable_path)
                for test_path in test_function_paths:
                    if called_in_file(call, test_path):
                        called_from_tests.add(testable_path)
                        break
            uncalled_testables = paths_not_called_in_another_function.difference(called_from_tests)
            datapack_name = str(datapack_dir.name).title()
            uncalled_str = list_to_table_cell([f'`{path_to_function_call(f)}`' for f in uncalled_testables])
            details_table.append([datapack_name, uncalled_str])
            testable_count = len(test_function_paths)
            covered_count = len(called_from_tests)
            percent = round(covered_count / testable_count * 100) if testable_count > 0 else None
            summary_table.append([datapack_name, covered_count, testable_count, percent])
        sort_table(summary_table, lambda row: row[-1] if row[-1] != None else -1, reverse=True)
        # TODO add an "All" row
        return (summary_table, True, details_table)

def called_in_file(call: str, file: Path):
    # check if mcfunction file has this call
    with open(file, 'r') as f:
        for line in f.readlines():
            if call in line.strip() and not line.strip().startswith('#'):
                return True