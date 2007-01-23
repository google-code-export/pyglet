#!/usr/bin/env python

'''Test framework for pyglet.  Reads details of components and capabilities
from a requirements document, runs the appropriate unit tests.

Collects results in a file named testrun.xml

TODO
----

* Implement the --full-help option


* Make modules non-interative by default (change flag to __interactive)

Differences
-----------

* Skips tests requiring interaction if --non-interactive flag is set

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import logging
import optparse
import os
from os.path import curdir, dirname, join, normpath, pardir
import re
import sys
import time

import reqparser
from ut_utils import TestComponent

LOG = logging.getLogger()
SCRIPT_ROOT = normpath(dirname(sys.argv[0] or curdir))


################################################################################

def fatal_error(msg):
    """ A fatal error has been encountered. Stop the application.
    """
    LOG.fatal(msg)
    print >> sys.stderr, "Fatal error: %s" % msg
    exit(-1)

def calc_default_capabilities():
    platform_cap = {
        'linux2': 'X11',
        'win32':  'WIN',
        'cygwin': 'WIN',
        'darwin': 'OSX' }.get(sys.platform, None)
    if platform_cap:
        return 'GENERIC,' + platform_cap
    else:
        return 'GENERIC'

def configure_logging(filename, level):
    """ Configures standard Python logging mechanism. """
    if filename == "stderr":
        filename = None
    logging.basicConfig(filename=filename, level=level)
    

def make_option_parser():
    usage = "Usage: %prog [options] [test_names]"
    description = '''Runs Pyglet tests. If you specify test_names, only those tests will be run, otherwise all tests will be run. test_names may be a regular expression (e.g. "image" to just run image tests).'''

    result = optparse.OptionParser(usage=usage, description=description, version="%prog " + __version__)

    result.add_option("--requirements", 
            default=normpath(join(SCRIPT_ROOT, pardir, 'doc', 
                'requirements.txt')),
            metavar="FILE",
            help="read requirements from FILE (defaults to %default)")

    result.add_option("--test-root",
            default=SCRIPT_ROOT,
            metavar="DIR",
            help="look for unit-tests in top-level directory DIR " 
                "(defaults to %default)")

    result.add_option("--capabilities",
            default=calc_default_capabilities(),
            metavar="CAPS",
            help="capabilities to test, as a comma separated list. "
                "By default includes only your operating system capability "
                "(X11, WIN or OSX). If you specify an empty set of "
                "capabilities, the capabilities check will be ignored and "
                "all the tests are run. (defaults to %default)")

    result.add_option("--log-level",
            default=10,
            type="int",
            metavar="LEVEL",
            help="sets minimum logging level to LEVEL - 10=debug, 30=warning, "
                "50=critical. (defaults to %default)")

    result.add_option("--log-file",
            default="stderr",
            metavar="FILE",
            help="send logging output to FILE. (defaults to %default)") 

    result.add_option("--no-regression-capture",
            dest="regression_capture",
            default=True,
            action="store_false",
            help="don't save regression images to disk")

    result.add_option("--no-regression-check",
            dest="regression_check",
            default=True,
            action="store_false",
            help="don't look for regression images on disk; assume none exist. "
                "Good for rebuilding out-of-date regression images.")

    result.add_option("--regression-tolerance",
            default=2,
            type="int",
            metavar="UNITS",
            help="allow UNITS tolerance when comparing a regression image. A "
                "tolerance of 0 means images must be identical. A tolerance "
                "of 256 means images will always match, if correct dimensions. "
                "(defaults to %default)")

    result.add_option("--regression-path",
            default=normpath(join(SCRIPT_ROOT, 'regression', 'images')),
            metavar="DIR",
            help="look for and store regression test images in DIR " 
                "(defaults to %default)")

    result.add_option("--developer",
            default=False,
            action="store_true",
            help="run tests with capability progress marked 'D' "
                "(developer-only). Enable this only if you are the developer "
                "of the feature; otherwise expect it to fail. "
                "(defaults to %default)")

    result.add_option("--no-interactive",
            dest="interactive",
            default=True,
            action="store_false",
            help="don't write descriptions or prompt for confirmation; just "
                "run each test in succession.")

    return result

def handle_args():
    """ Handles command line, ensuring arguments are of correct type and
        does some initialisation. """
    opts, args = make_option_parser().parse_args()
    opts.capabilities = opts.capabilities.split(',')

    if opts.regression_capture:
        try:
            os.makedirs(opts.regression_path)
        except OSError:
            pass

    configure_logging(opts.log_file, opts.log_level)

    sys.path[1:1] = [opts.test_root]

    return opts, args


def fetch_req_components(file_name, test_names):
    """ Fetch named components from the named requirements document file. """
    try:
        text = open(file_name).read()
    except:
        fatal_error("Could not open requirements document %s." % file_name)

    req_doc = reqparser.parse(text)
    if test_names:
        result = []
        for name in test_names:
            matches = req_doc.search(name)
            if not matches:
                fatal_error('No components or sections match "%s"', name)
            result += matches
        return result
    else:
        return req_doc.get_all_components()

def component_selected(req_comp, capabilities, developer):
    """ Determines if the requirements component should be selected. """
    level = reqparser.RequirementsComponent.FULL
    if developer:
        level = reqparser.RequirementsComponent.DEVELOPER
    return req_comp.is_implemented(capabilities, level)

def run_remote(opts, test_comp):
    """ Run the given test component in another process. """
    # Write out params
    # Create test result dir
    remote_script = join(SCRIPT_ROOT, 'run_test.py')
    os.spawnv(os.P_WAIT, sys.executable, [sys.executable, remote_script,
        test_comp.name, opts.test_root, 'tmp'])
    # Run remote test
    # Interpret results

            
def main():
    """ Main program.  Gets options, determines which tests to run, and runs 
    them."""

    opts, args = handle_args()

    LOG.info('Beginning test at %s', time.ctime())
    LOG.info('Capabilities are: %s', ', '.join(opts.capabilities))
    LOG.info('sys.platform = %s', sys.platform)
    LOG.info('Reading requirements from %s', opts.requirements)

    req_comps = fetch_req_components(opts.requirements, args)
    LOG.debug('Fetching matching test components')
    test_comps = [TestComponent(rc.get_absname(), opts.regression_path) 
            for rc in req_comps 
                if component_selected(rc, opts.capabilities, opts.developer)]
    LOG.info('%s tests to run', len(test_comps))

    # TODO: create a tmp dir

    for tc in test_comps:
        run_remote(opts, tc)

    # TODO: write summary file
    # TODO: Collect all together in a zip file. Delete tmp dir
    

if __name__ == '__main__':
    main()
