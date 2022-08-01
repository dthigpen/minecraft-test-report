import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

class Document:
    def __init__(self, file):
        self.file = file

    def write(self, *lines):
        text = '\n'.join(lines)
        self.file.write(text + '\n')
    
    def nl(self, count=1):
        self.file.write('\n'*count)
    

    def header(self, title, size=1):
        self.write('#' * size + ' ' + title)
        self.nl()
    
    def header1(self, title):
        self.header(title, size=1)

    def header2(self, title):
        self.header(title, size=2)

    def header3(self, title):
        self.header(title, size=3)

    def table_header(self, *cols):
        col_strs = list(map(str, cols))
        col_breaks = ['-'*len(c) for c in col_strs]
        self.write('| ' + ' | '.join(col_strs) + ' |')
        self.write('| ' + ' | '.join(col_breaks) + ' |')
    
    def table_row(self, *cols):
        col_strs = list(map(str, cols))
        self.write('| ' + '|'.join(col_strs) + ' |')

    def collapsible_section_opening(self, summary):
        self.write('<details>')
        self.write(f'  <summary>{summary}</summary>\n')
    
    def collapsible_section_closing(self):
        self.write('</details>')
        self.nl()

    @staticmethod
    @contextmanager
    def open(output_file, mode='w'):
        # Code to acquire resource, e.g.:
        doc_file = open(output_file, mode)
        document = Document(doc_file)
        try:
            yield document
        finally:
            if doc_file and not doc_file.closed:
                doc_file.close()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=Path, help='Output markdown file')
    return parser.parse_args()

def main(out_path: Path):
    print(out_path)

if __name__ == '__main__':
    args = get_args()
    main(args.file)