from argparse import ArgumentParser
from subprocess import check_call
import glob
import os
import io
import tokenize


def main():
    parser = ArgumentParser(description='Github scraper')
    parser.add_argument('source', action='store',
                        help='Source folder for the scraped GitHub repositories')
    parser.add_argument('destination', action='store',
                        help='Destination file')
    parser.add_argument('-p', type=int, default=0, action='store', dest='padding',
                        help='Number of padding characters to add before each file')
    parser.add_argument('-e', type=int, default=0, action='store', dest='end_padding',
                        help='Number of end of file chaacters to add after each file')
    parser.add_argument('--twotothree', action='store_true')
    parser.add_argument('--removecomments', action='store_true')
    parser.add_argument('--autopep8', action='store_true')
    parser.add_argument('--yapf', action='store_true')

    settings = parser.parse_args()

    print(settings)

    glob_search_path = os.path.join(settings.source, '**', '*.py')

    filelist = [f for f in glob.iglob(
        glob_search_path, recursive=True) if os.path.isfile(f)]

    if settings.twotothree:
        check_call(['2to3', '-n', '-w', settings.source])

    if settings.removecomments:
        for filename in filelist:
            with io.open(filename, 'r+', encoding='latin-1', errors='ignore') as f:
                print(filename)
                text = f.read()
                clean_text = remove_comments_and_docstrings(text)
                f.seek(0)
                f.write(clean_text)

    if settings.autopep8:
        check_call(['autopep8', '--in-place', '--recursive', settings.source])

    if settings.yapf:
        check_call(['autopep8', '--in-place', '--recursive', settings.source])
    
    with io.open(settings.destination, 'w') as outfile:
        for f in filelist[:10]:
            with io.open(f, 'r', encoding='latin-1') as infile:
                pad(settings.padding, '\x0b')
                outfile.write(pad(settings.padding, '\x0b') +
                              infile.read() +
                              pad(settings.padding, '\x0c'))

def pad(n, padding):
    return padding * n


def n_pad(text, n, padding='\x0b'):
    return padding * n + text

def remove_comments_and_docstrings(source):
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
        # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out


def remove_last_n_lines(file, number=2):
    count = 0
    with open(file, 'r+b', buffering=0) as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            print(f.tell())
            char = f.read(1)
            if char != b'\n' and f.tell() == end:
                print("No change: file does not end with a newline")
            if char == b'\n':
                count += 1
            if count == number + 1:
                f.truncate()
                print("Removed " + str(number) + " lines from end of file")
 
            f.seek(-1, os.SEEK_CUR)

    if count < number + 1:
        print("No change: requested removal would leave empty file")



if __name__ == '__main__':
    main()
