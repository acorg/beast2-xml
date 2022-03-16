#!/usr/bin/env python

from __future__ import print_function, division

import argparse
from itertools import chain
from dark.reads import addFASTACommandLineOptions, parseFASTACommandLineOptions
from beast2xml import BEAST2XML

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=('Given FASTA on stdin (or in a file via the --fastaFile '
                 'option), write an XML BEAST2 input file on stdout.'))

# A mutually exclusive group for either --clockModel or --templateFile.
group = parser.add_mutually_exclusive_group()

group.add_argument(
    '--clockModel', metavar='MODEL', default='strict',
    choices=('random-local', 'relaxed-exponential', 'relaxed-lognormal',
             'strict'),
    help=('Specify the clock model. Possible values are '
          "'random-local', 'relaxed-exponential', 'relaxed-lognormal', "
          "or 'strict'"))

group.add_argument(
    '--templateFile', metavar='FILENAME',
    help='The XML template file to use.')

parser.add_argument(
    '--chainLength', type=int, metavar='LENGTH',
    help='The MCMC chain length.')

parser.add_argument(
    '--age', metavar='ID=N', nargs='+', action='append',
    help=('The age of a sequence. The format is a sequence id, an equals '
          'sign, then the age. For convenience, just the first part '
          'of a full sequence id (i.e., up to the first space) may be given. '
          'May be specified multiple times.'))

parser.add_argument(
    '--defaultAge', type=float, default=0.0, metavar='N',
    help=('The age to use for sequences that are not explicitly given an '
          'age via --age.'))

parser.add_argument(
    '--dateUnit', metavar='UNIT', choices=('day', 'month', 'year'),
    default='year',
    help=('Specify the date unit. Possible values are '
          "'day', 'month', or 'year'."))

parser.add_argument(
    '--dateDirection', metavar='DIRECTION', choices=('backward', 'forward'),
    default='backward',
    help=('Specify whether dates are back in time from the present or '
          'forward in time from some point in the past. Possible values are '
          "'forward' or 'backward'."))

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

parser.add_argument(
    '--mimicBEAUti', action='store_true',
    help=('If specified, add attributes to the <beast> tag that mimic what '
          'BEAUti uses so that BEAUti will be able to load the XML.'))

parser.add_argument(
    '--sequenceIdDateRegex', metavar='REGEX',
    help=('A regular expression that will be used to capture sequence dates '
          'from their ids. The regular expression must have three named '
          'capture regions ("year", "month", and "day"). Regular expression '
          'matching is anchored to the start of the id string (i.e., '
          "Python's re.match function is used, not the re.search function), "
          'so you must explicitly match the id from its beginning. For '
          'example, you might use --sequenceIdDateRegex '
          r"'^.*_(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)'."))

parser.add_argument(
    '--sequenceIdAgeRegex', metavar='REGEX',
    help=('A regular expression that will be used to capture sequence ages '
          'from their ids. The regular expression must have a single '
          'capture region. Regular expression matching is anchored to the '
          "start of the id string (i.e., Python's re.match function is used, "
          'not the re.search function), so you must explicitly match the id '
          'from its beginning. For example, you might use '
          r"--sequenceIdAgeRegex '^.*_(\d+)$' to capture an age preceded by "
          'an underscore at the very end of the sequence id. If '
          '--sequenceIdDateRegex is also given, it takes precedence when '
          'matching sequence ids.'))

parser.add_argument(
    # Note that --sequenceIdDateRegexMayNotMatch is maintained here for
    # backwards compatibility.
    '--sequenceIdRegexMayNotMatch', '--sequenceIdDateRegexMayNotMatch',
    action='store_false',
    dest='sequenceIdRegexMustMatch',
    help=('If specified (and --sequenceIdDateRegex or --sequenceIdAgeRegex is '
          'given) it will not be considered an error if a sequence id does '
          'not match the given regular expression. In that case, sequences '
          'will be assigned an age of zero unless one is given via --age.'))

addFASTACommandLineOptions(parser)
args = parser.parse_args()
reads = parseFASTACommandLineOptions(args)

xml = BEAST2XML(
    template=args.templateFile, clockModel=args.clockModel,
    sequenceIdDateRegex=args.sequenceIdDateRegex,
    sequenceIdAgeRegex=args.sequenceIdAgeRegex,
    sequenceIdRegexMustMatch=args.sequenceIdRegexMustMatch,
    dateUnit=args.dateUnit)

xml.addSequences(reads)

if args.age:
    # Flatten lists of lists that we get from using both nargs='+' and
    # action='append'. We use both because it allows people to use --age on the
    # command line either via "--age id1=33 --age id2=21" or "--age id1=33
    # id2=21", or a combination of these. That way it's not necessary to
    # remember which way you're supposed to use it and you also can't be hit by
    # the subtle problem encountered in
    # https://github.com/acorg/dark-matter/issues/453
    ages = list(chain.from_iterable(args.age))

    for ageInfo in ages:
        id_, age = ageInfo.rsplit(sep='=', maxsplit=1)
        xml.addAge(id_.strip(), float(age.strip()))

print(xml.toString(
    chainLength=args.chainLength, defaultAge=args.defaultAge,
    dateDirection=args.dateDirection, logFileBasename=args.logFileBasename,
    traceLogEvery=args.traceLogEvery, treeLogEvery=args.treeLogEvery,
    screenLogEvery=args.screenLogEvery,
    mimicBEAUti=args.mimicBEAUti).replace('" /><sequence',
                                          '" />\n    <sequence'))
