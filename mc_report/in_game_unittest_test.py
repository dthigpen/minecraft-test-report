
from contextlib import contextmanager
import os
from pathlib import Path
import re
from time import sleep
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
    def __init__(self, host='localhost', port=DEFAULT_PORT, test_includes=None, test_excludes=None, test_content_include_regex=None, test_content_exclude_regex=None):
        self.host=host
        self.port=port
        self.test_includes=test_includes
        self.test_excludes=test_excludes
        self.test_content_include_regex=test_content_include_regex
        self.test_content_exclude_regex=test_content_exclude_regex

    @staticmethod
    def get_name() -> str:
        return 'Unit Tests'

    @staticmethod
    def _passes_content_filter(content: str, include_re: str, exclude_re: str) -> bool:
        # check include
        passes = include_re is None or re.search(include_re, content)
        # check exclude
        passes = passes and (exclude_re is None or not re.search(exclude_re, content))
        return passes


    def run(self, datapack_dirs: list) -> list:
        summary_table = [['Datapack', 'Failed', 'Passed', 'Skipped']]
        details_table = [['Datapack','Failed','Skipped']]
        passed = True
        for datapack_dir in datapack_dirs:
            fail_paths = []
            pass_paths = []
            skip_paths = []
            mcfunction_paths = get_functions(datapack_dir, self.test_includes, self.test_excludes)

            mcfunctions = [path_to_function_call(p) for p in mcfunction_paths if UnittestRunner._passes_content_filter(p.read_text(), self.test_content_include_regex, self.test_content_exclude_regex)]
            pwd=os.getenv('RCON_PWD')
            with rcon_client(self.host,pwd=pwd,port=self.port) as rcon:
                rcon.command('reload')
                rcom.command('player Steve spawn')
                for test_function in mcfunctions:
                    print(f'Running {test_function}')
                    test_cmd = f'execute as Steve at @s run function {test_function}'
                    rcon.command(test_cmd)
                    verify_cmd = 'scoreboard players get $status unittest'
                    output = rcon.command(verify_cmd)
                    if '$status has 1' in output:
                        pass_paths.append(test_function)
                    else:
                        passes_test = False
                        timeout_count = 3
                        print(f'test: {test_function} output: {output}')
                        while '$status has 2' in output or '$status has 3' in output:
                            # TODO make this a parameter
                            sleep(5)
                            output = rcon.command(verify_cmd)
                            timeout_count -= 1
                            if '$status has 1' in output:
                                passes_test = True
                                break
                            elif timeout_count <= 0:
                                break
                        if passes_test:
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
            if fail_count + pass_count + skip_count > 0:
                summary_table.append([datapack_name,fail_count, pass_count, 0])
            sort_table(summary_table, lambda row: row[1])
        return (summary_table, passed, details_table)
