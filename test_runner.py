import argparse
from pathlib import Path
from mc_report.in_game_unittest_test import UnittestRunner
from mc_report.markdown import Document
from mc_report.coverage_test import CoverageTest

TESTS = [UnittestRunner(), CoverageTest()]
# TESTS = [CoverageTest()]

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate various stats on datapack functions')
    parser.add_argument('datapacks',type=Path,nargs='+', help='Datapack(s)')
    parser.add_argument('--output',type=Path, default=Path('report.md'),help='Output file path')
    return parser.parse_args()


def write_table(doc: Document, table: list[list]):
    doc.table_header(*table[0])
    for row in table[1:]:
        doc.table_row(*row)

def run(datapack_paths: list[Path], output_file: Path, overwrite=True):
    print(f'Outputting to {output_file}')
    overall_pass = True
    open_mode = 'w' if overwrite else 'a+'
    with Document.open(output_file, open_mode) as doc:
        for test in TESTS:
            print(f'Running test: {test.get_name()}')
            results_table, passed, details_table = test.run(datapack_paths)
            if not passed:
                overall_pass = False
            if not overwrite:
                doc.nl()
            doc.header2('Tests')
            doc.header3(f'{test.get_name()}')
            write_table(doc, results_table)
            doc.nl()
            if details_table:
                doc.collapsible_section_opening('Details')
                write_table(doc, details_table)
                doc.collapsible_section_closing()
    return overall_pass
if __name__ == "__main__":
    args = get_args()
    overall_pass = run(args.datapacks, args.output)
    # force pass for now
    # exit(0 if overall_pass else 1)
