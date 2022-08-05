
from contextlib import contextmanager
import os
from pathlib import Path
from .datapacks import Datapack, DatapackTest, path_to_function_call

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
    def __init__(self, host='localhost', port=DEFAULT_PORT):
        self.host=host
        self.port=port

    @staticmethod
    def get_name() -> str:
        return 'Unit Tests'

    def run(self, datapack_dirs: list) -> list:
        summary_header = ['Datapack', 'Failed', 'Passed', 'Skipped']
        summary_table = []
        details_header = ['Datapack','Failed','Skipped']
        details_table = []
        passed = True
        for datapack_dir in datapack_dirs:
            fail_paths = []
            pass_paths = []
            skip_paths = []
            mcfunctions = [path_to_function_call(p) for p in datapack_dir.glob('**/functions/test/**/test_*') if 'client' not in str(p) and 'unittest' not in p.parts and not p.name.startswith('_')]
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
            pass_count = len(pass_count)
            skip_count = len(skip_count)
            datapack_name = Datapack(datapack_dir).name
            # only add detail entry for failed or skipped tests
            if fail_count + skip_count > 0:
                failed_str = ''
                for f in fail_paths:
                    failed_str += f'`{f}`<br/>'
                skip_str = ''
                for f in skip_paths:
                    skip_str += f'`{f}`<br/>'
                details_table.append([datapack_name, failed_str, skip_str])
            # only add entry if there was at least one test
            if fail_count + pass_count + skip_count > 0:
                summary_table.append([datapack_name,fail_count, pass_count, 0])
        
        if details_table:
            details_table.insert(0,details_header)
        else:
            details_header = None
        summary_table.insert(0, summary_header)
        return (summary_table, passed, details_table)