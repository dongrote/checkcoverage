#!/usr/bin/env python
import subprocess
import sys
import os
from optparse import OptionParser


def test_file_filter(filepath):
    basename = os.path.basename(filepath)
    return not basename.startswith('test_')

def legacy_scraper_filter(filepath):
    return not filepath.startswith('./centrifuge/legacy/')

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
        ['coverage','report','--omit="/usr*","centrifuge/legacy/*"'])
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


def main():
    parser = OptionParser()
    parser.set_usage('Usage: %prog [options]')
    parser.add_option('-m', '--minimum-code-coverage',
        dest='minimum_code_coverage', default=0, type='int',
        help='The per-file minimum code coverage')

    (options, args) = parser.parse_args()

    coverage_report = get_coverage_report()
    coverage_dictionary = build_coverage_dictionary(coverage_report)

    file_list = get_python_files()
    file_list = filter(test_file_filter, file_list)
    file_list = filter(legacy_scraper_filter, file_list)
    file_list = filter(other_filter, file_list)

    for filepath in file_list:
        # we gonna chop off the './' and the '.py' at the beginning and end
        key = filepath[2:-3]
        try:
            line = coverage_dictionary[key]
            tokens = line.split()
            coverage = tokens[-1]
            coverage = int(coverage[:-1])
            if coverage < options.minimum_code_coverage:
                print >> sys.stderr,\
                'Minimum code coverage not met (%d%% < %d%%) for "%s"!' %\
                    (coverage, options.minimum_code_coverage, filepath)
                return 1
        except KeyError:
            print >> sys.stderr, '"%s" not found in coverage report!' % filepath
            return 1
    return 0

if '__main__' == __name__:
    sys.exit(main())
