#!/usr/bin/env python
import subprocess
import sys
import os
import re
from argparse import ArgumentParser


def test_file_filter(filepath):
    basename = os.path.basename(filepath)
    return not basename.startswith('test_')

def other_filter(filepath):
    blacklist = ['./setup.py']
    for i in blacklist:
        if filepath == i:
            return False
    return True

def get_python_files(start='.'):
    files = []
    for dirpath, dirnames, filenames in os.walk(start):
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(os.path.join(dirpath,filename))
    return files

def get_coverage_report():
    report = subprocess.check_output(
        ['coverage','report'])
    return report

def build_coverage_dictionary(report):
    dictionary = {}
    for line in report.splitlines():
        try:
            key, garbage = line.split(' ', 1)
        except:
            continue
        dictionary[key] = line
    return dictionary

def match_exclude_regex(regex, path):
    return not re.match(regex, path) is None


def main():
    parser = ArgumentParser(
        description='Check code coverage in a Python source tree.')
    parser.add_argument('-m', '--minimum-code-coverage', dest='minimum_code_coverage', default=0, type=int,
        help='The per-file minimum code coverage')
    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=str, default=[],
        help='File path regular expression(s) to exclude.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
        help='Verbose output')

    args = parser.parse_args()

    coverage_report = get_coverage_report()
    coverage_dictionary = build_coverage_dictionary(coverage_report)

    file_list = get_python_files()
    for exclude_regex in args.exclude:
        # filter coverage_dictionary
        remove_list = [filepath for filepath in coverage_dictionary if match_exclude_regex(exclude_regex, filepath)]
        for entry in remove_list:
            del coverage_dictionary[entry]
        # filter file_list
        file_list = [filepath for filepath in file_list if not match_exclude_regex(exclude_regex, filepath)]

    if args.verbose:
        for line in coverage_report.splitlines():
            output = True
            for exclude_regex in args.exclude:
                if match_exclude_regex(exclude_regex, line.split()[0]):
                    output = False
                    break
            if output:
                print line
        print

    for filepath in file_list:
        # we gonna chop off the './' and the '.py' at the beginning and end
        key = filepath[2:-3]
        try:
            line = coverage_dictionary[key]
            tokens = line.split()
            coverage = tokens[-1]  # grab the code coverage
            coverage = int(coverage[:-1])  # remove the '%' character
            if coverage < args.minimum_code_coverage:
                print >> sys.stderr,\
                'Minimum code coverage not met (%d%% < %d%%) for "%s"!' %\
                    (coverage, args.minimum_code_coverage, filepath)
                return 1
        except KeyError:
            print >> sys.stderr, '"%s" not found in coverage report!' % filepath
            return 1
    return 0

if '__main__' == __name__:
    sys.exit(main())
