
from contextlib import contextmanager
import os
from pathlib import Path
import re
from .test_util import DatapackTest, get_functions, list_to_table_cell, path_to_function_call, sort_table

from mctools import RCONClient

DEFAULT_PORT = 25575
@contextmanager
def rcon_client(host, port=DEFAULT_PORT, pwd=None):
    # Code to acquire resource, e.g.:
    rcon = RCONClient(host, port=port)
    if pwd:
        rcon.login(pwd)
    try:
        yield rcon
    finally:
        pass




class UnittestRunner(DatapackTest):
    def __init__(self, host='localhost', port=DEFAULT_PORT, test_includes=None, test_excludes=None):
        self.host=host
        self.port=port
        self.test_includes=test_includes
        self.test_excludes=test_excludes

    @staticmethod
    def get_name() -> str:
        return 'Unit Tests'

    def run(self, datapack_dirs: list) -> list:
        summary_table = [['Datapack', 'Failed', 'Passed', 'Skipped']]
        details_table = [['Datapack','Failed','Skipped']]
        passed = True
        for datapack_dir in datapack_dirs:
            fail_paths = []
            pass_paths = []
            skip_paths = []
            mcfunction_paths = get_functions(datapack_dir, self.test_includes, self.test_excludes)
            mcfunctions = [path_to_function_call(p) for p in mcfunction_paths]
            pwd=os.getenv('RCON_PWD')
            with rcon_client(self.host,pwd=pwd,port=self.port) as rcon:
                rcon.command('reload')
                for test_function in mcfunctions:
                    test_cmd = f'function {test_function}'
                    rcon.command(test_cmd)
                    verify_cmd = 'scoreboard players get $passed unittest'
                    output = rcon.command(verify_cmd)
                    if '$passed has 1' in output:
                        pass_paths.append(test_function)
                    else:
                        fail_paths.append(test_function)
                        passed = False
            fail_count = len(fail_paths)
            pass_count = len(pass_paths)
            skip_count = len(skip_paths)
            datapack_name = str(datapack_dir.name).title()
            # only add detail entry for failed or skipped tests
            if fail_count + skip_count > 0:
                failed_str = list_to_table_cell([f'`{f}`' for f in fail_paths])
                skip_str = list_to_table_cell([f'`{f}`' for f in skip_paths])
                details_table.append([datapack_name, failed_str, skip_str])
            # only add entry if there was at least one test
            if True or fail_count + pass_count + skip_count > 0:
                summary_table.append([datapack_name,fail_count, pass_count, 0])
            sort_table(summary_table, lambda row: row[1])
        return (summary_table, passed, details_table)