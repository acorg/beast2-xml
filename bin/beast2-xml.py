#!/usr/bin/env python

from __future__ import print_function, division

import argparse
from beast2xml.beast2 import BEAST2XML
from dark.reads import addFASTACommandLineOptions, parseFASTACommandLineOptions

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=('Given FASTA on stdin (or in a file via the --fastaFile '
                 'option), write an XML BEAST2 input file on stdout.'))

parser.add_argument(
    '--chainLength', type=int, metavar='LENGTH',
    help='The MCMC chain length.')

parser.add_argument(
    '--templateFile', metavar='FILENAME',
    help='The XML template file to use.')

parser.add_argument(
    '--logFileBasename', default='beast-output', metavar='BASE-FILENAME',
    help=('The base filename to write logs to. A ".log" or ".trees" suffix '
          'will be appended to this to make complete log file names.'))

parser.add_argument(
    '--traceLogEvery', type=int, default=2000, metavar='N',
    help='How often to write to the trace log file.')

parser.add_argument(
    '--treeLogEvery', type=int, default=2000, metavar='N',
    help='How often to write to the tree log file.')

parser.add_argument(
    '--screenLogEvery', type=int, default=2000, metavar='N',
    help='How often to write logging to the screen (i.e., terminal).')

addFASTACommandLineOptions(parser)
args = parser.parse_args()
reads = parseFASTACommandLineOptions(args)

xml = BEAST2XML(template=args.templateFile)
xml.addSequences(reads)

print(xml.toStr(
    chainLength=args.chainLength,
    logFileBasename=args.logFileBasename,
    traceLogEvery=args.traceLogEvery,
    treeLogEvery=args.treeLogEvery,
    screenLogEvery=args.screenLogEvery).replace(
        '" /><sequence', '" />\n    <sequence'))
