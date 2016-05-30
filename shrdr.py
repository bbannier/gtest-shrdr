#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import multiprocessing
import optparse
import os
import re
import signal
import subprocess
import sys


class bcolors:
    HEADER = '\033[95m' if sys.stdout.isatty() else ''
    OKBLUE = '\033[94m' if sys.stdout.isatty() else ''
    OKGREEN = '\033[92m' if sys.stdout.isatty() else ''
    WARNING = '\033[93m' if sys.stdout.isatty() else ''
    FAIL = '\033[91m'if sys.stdout.isatty() else ''
    ENDC = '\033[0m' if sys.stdout.isatty() else ''
    BOLD = '\033[1m' if sys.stdout.isatty() else ''
    UNDERLINE = '\033[4m' if sys.stdout.isatty() else ''


def work(opts):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    shard, nshards, binary = opts
    env = os.environ.copy()
    env['GTEST_TOTAL_SHARDS'] = str(nshards)
    env['GTEST_SHARD_INDEX'] = str(shard)

    try:
        output = subprocess.check_output(
                binary,
                stderr=subprocess.STDOUT,
                env=env,
                universal_newlines=True)
        print(bcolors.OKGREEN + '.' + bcolors.ENDC, end='', flush=True)
        return True, output
    except subprocess.CalledProcessError as ex:
        print(bcolors.FAIL + 'E' + bcolors.ENDC, end='', flush=True)
        return False, ex.output


def main_(options, binary):
    def options_gen(n, binary):
        opts = range(n)

        # If we run in a terminal enable colored test output. We still
        # allow users to disable this themself via extra args.
        if sys.stdout.isatty():
            binary = binary[0:1] + ['--gtest_color=yes'] + binary[1:]

        for opt in opts:
            yield opt, n, binary

    try:
        p = multiprocessing.Pool(processes=options.jobs)
        results = p.map(work, options_gen(options.jobs, binary))

        nfailed = len(list(itertools.filterfalse(lambda r: r[0], results)))

        for result in results:
            if not result[0]:
                if options.verbosity > 0:
                    print(result[1], file=sys.stderr)
            else:
                if options.verbosity > 1:
                    print(result[1], file=sys.stdout)

        if nfailed:
            print(
              '\n' +
              bcolors.FAIL + bcolors.BOLD + '[FAIL]' + bcolors.ENDC,
              file=sys.stderr)
        else:
            print(
              '\n' + bcolors.OKGREEN + bcolors.BOLD + '[PASS]' + bcolors.ENDC)

        sys.exit(nfailed)

    except KeyboardInterrupt:
        # Force a newline after intermediate test reports.
        print()

        print('Caught KeyboardInterrupt, terminating workers')

        p.terminate()
        p.join()

        sys.exit(1)
    except OSError as ex:
        p.terminate()
        p.join()

        print('\n' + bcolors.FAIL + 'ERROR: ' + str(ex) + bcolors.ENDC)

        sys.exit(1)

if __name__ == '__main__':
    parser = optparse.OptionParser(
            usage='Usage: %prog [options] <test> [-- <test_options>]')

    DEFAULT_NUM_JOBS = int(multiprocessing.cpu_count() * 1.5)
    parser.add_option('-j', '--jobs', type='int',
                      default=DEFAULT_NUM_JOBS,
                      help='number of parallel jobs to spawn. DEFAULT: {}'
                      .format(DEFAULT_NUM_JOBS))

    parser.add_option('-v', '--verbosity', type='int',
                      default=1,
                      help='output verbosity:'
                      ' 0 only shows summarized information,'
                      ' 1 also shows full logs of failed shards, and anything'
                      ' >1 shows all output. DEFAULT: 1')

    (options, binary) = parser.parse_args()

    if not binary:
        parser.print_usage()
        sys.exit(1)

    main_(options, binary)
