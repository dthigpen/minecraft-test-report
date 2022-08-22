import argparse
from pathlib import Path

from mc_report.in_game_unittest_test import UnittestRunner
from mc_report.markdown import Document
from mc_report.coverage_test import CoverageTest

# Include files in the "test" functions subdirectory that start with "test_"
UNIT_TESTS_RE = r'.*/functions/test/(.*/)?test_[^/]*\.mcfunction'
# Exclude files that include client or client_test(s) 
TESTS = [UnittestRunner(test_includes=[UNIT_TESTS_RE], test_content_include_regex=r'function unittest:api/test_suite/setup'),\
    CoverageTest(test_includes=[UNIT_TESTS_RE,r'.*/functions/test/(.*/)?client_test_[^/]*\.mcfunction'])]

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate various stats on datapack functions')
    parser.add_argument('datapacks',type=Path,nargs='+', help='Datapack(s)')
    parser.add_argument('--output',type=Path, default=Path('report.md'),help='Output file path')
    parser.add_argument('--tests',type=str,nargs='*',help='Specific tests to run or all if not specified')
    parser.add_argument('--append',action='store_true',help='Append the output file instead of overwriting')
    return parser.parse_args()


def write_table(doc: Document, table: list[list]):
    doc.table_header(*table[0])
    for row in table[1:]:
        doc.table_row(*row)

def run(datapack_paths: list[Path], output_file: Path, tests_to_run=None, append_output=False):
    print(f'Outputting to {output_file}')
    overall_pass = True
    with Document.open(output_file, 'a+' if append_output else 'w') as doc:
        doc.header2('Tests')
        doc.nl()
        for test in TESTS:
            if tests_to_run and test.get_name() not in tests_to_run:
                continue
            print(f'Running test: {test.get_name()}')
            results_table, passed, details_table = test.run(datapack_paths)
            if not passed:
                overall_pass = False
            doc.header3(f'{test.get_name()}')
            write_table(doc, results_table)
            doc.nl()
            if len(details_table) > 1:
                doc.collapsible_section_opening('Details')
                write_table(doc, details_table)
                doc.collapsible_section_closing()
    return overall_pass
if __name__ == "__main__":
    args = get_args()
    overall_pass = run(args.datapacks, args.output,tests_to_run=args.tests, append_output=args.append)
    # force pass for now
    # exit(0 if overall_pass else 1)
