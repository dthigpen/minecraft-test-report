from pathlib import Path
from .datapacks import Datapack, DatapackTest, path_to_function_call, path_to_function_call


class CoverageTest(DatapackTest):
    @staticmethod
    def get_name() -> str:
        return 'Test Coverage'

    def run(self, datapack_dirs: list) -> list:
        header = ['Datapack', 'Tested', 'Total', 'Percent']
        table = []
        for datapack_dir in datapack_dirs:
            datapack = Datapack(datapack_dir)
            all_function_paths = set(datapack.get_functions())
            test_function_paths = set(datapack.get_functions('test'))
            non_test_functions_paths = all_function_paths.difference(test_function_paths)
            testable_function_paths = set()  # non test functions not called in other non test functions

            for non_test_path in non_test_functions_paths:
                call = path_to_function_call(non_test_path)
                # look through all non-test functions to eliminate from testable pool
                for p in non_test_functions_paths:
                    # skip own file
                    if call != path_to_function_call(p):
                        continue
                    # check if mcfunction file has this call
                    if called_in_file(call, p):
                        testable_function_paths.add(non_test_path)
                        break
            called_from_tests = set()
            for testable_path in testable_function_paths:
                call = path_to_function_call(testable_path)
                for test_path in test_function_paths:
                    if called_in_file(call, test_path):
                        called_from_tests.add(testable_path)
                        break
            uncalled_testables = test_function_paths.difference(called_from_tests)
            
            testable_count = len(test_function_paths)
            covered_count = len(called_from_tests)
            percent = round(covered_count / testable_count * 100) if testable_count > 0 else None
            table.append([datapack.name, covered_count, testable_count, percent])
        
        table.sort(key=lambda row: row[-1] if row[-1] != None else -1, reverse=True)
        # TODO add an "All" row
        # Add percent signs
        for row in table:
            row[-1] = f'{row[-1]}%' if row[-1] != None else '-'
        table.insert(0,header)
        return table, True

def called_in_file(call: str, file: Path):
    # check if mcfunction file has this call
    with open(file, 'r') as f:
        for line in f.readlines():
            if call in line.strip() and not line.strip().startswith('#'):
                return True