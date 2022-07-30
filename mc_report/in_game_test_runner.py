import argparse
import os
from pathlib import Path
import re

from mctools import RCONClient

from contextlib import contextmanager

DEFAULT_PORT = 25575  # Port number of the RCON server

def path_to_function_call(path: Path) -> str:
    relevant_parts = list(path.parts[path.parts.index('data') + 1:])
    namespace = relevant_parts.pop(0)
    relevant_parts.pop(0) # functions
    relevant_parts.pop() # last
    relevant_parts.append(path.stem)
    return f'{namespace}:{"/".join(relevant_parts)}'

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

def existing_dir(potential_dir: str) -> Path:
    path = Path(potential_dir)
    if not path.is_dir():
        raise argparse.ArgumentTypeError('Path does not exist or is not a directory')
    return path

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=existing_dir, help='Path to directory where unit tests reside somewhere inside')
    parser.add_argument('--host',default='localhost', help='Server host url')
    parser.add_argument('--port',type=int, default=25575, help='Server port')
    return parser.parse_args()



def test_command_output(rcon, command: str, output_re_str: str) -> bool:
    output = rcon.command(command)
    return re.match(output_re_str, output)


def run(dir: Path, host: str, port: int):
    mcfunctions = [path_to_function_call(p) for p in dir.glob('**/functions/test/**/test_*') if 'client' not in str(p) and 'unittest' not in p.parts and not p.name.startswith('_')]

    pwd=os.getenv('RCON_PWD')
    with rcon_client(host,pwd=pwd,port=port) as rcon:
        rcon.command('reload')
        for test_function in mcfunctions:
            test_cmd = f'function {test_function}'
            rcon.command(test_cmd)
            verify_cmd = 'scoreboard players get $passed unittest'
            output = rcon.command(verify_cmd)
            if '$passed has 1' in output:
                print(f'PASS: {test_function}')
            else:
                print(f'FAIL: {test_function}')
                print(f'output: {output}')



if __name__ == "__main__":
    args = get_args()
    run(args.dir, args.host, args.port)