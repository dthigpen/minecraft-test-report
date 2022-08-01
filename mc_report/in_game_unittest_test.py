
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
        table = [['Datapack', '# Failed', '# Passed', '% Passed']]
        fail_count = 0
        pass_count = 0
        passed = True
        for datapack_dir in datapack_dirs:
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
                        pass_count += 1
                    else:
                        fail_count += 1
                        passed = False
                        # print(f'output: {output}')
            datapack = Datapack(datapack_dir)
            percent = f'{round(pass_count / (pass_count+fail_count) * 100)}%' if pass_count + fail_count > 0 else '-'
            table.append([datapack.name,fail_count, pass_count, percent])
        return (table, passed)