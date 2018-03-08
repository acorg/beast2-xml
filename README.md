## BEAST2 XML

This is a first, and *very* simplistic, cut at generating BEAST2 XML from
Python (2.7, 3.5, 3.6 are all known to work).

BEAST2 is a complex program and so is its input XML.  People normally
generate the input XML using a GUI tool,
[BEAUti](https://www.beast2.org/beauti/). BEAUti is also a complex tool,
and the XML it generates can vary widely. Because BEAUti is a GUI tool it's
not possible to use it to programmatically generate XML.

I wrote `beast2-xml` because I wanted a way to quickly and easily generate
BEAST2 XML files, from the command line and also from my
[Python](https://www.python.org/) code.

There are a *lot* of things that could be added to this code! Contributions
welcome.

## The package provides

* A command-line script ([bin/beast2-xml.py](bin/beast2-xml.py)) to
  generate [BEAST2](http://beast2.org/) XML files.
* A simplistic Python class (in [beast2xml/beast2.py](beast2xml/beast2.py))
  that may be helpful if you are writing Python that needs to generate
  BEAST2 XML files.  (This Python class is of course used by the command
  line script.)

## Installation

```sh
$ pip install beast2-xml
```

You can also get the source
[from PyPI](https://pypi.org/project/beast2-xml/) or
[on Github](https://github.com/acorg/beast2-xml).

## Generate XML from the command line

You can use `bin/beast2-xml.py` to quickly generate BEAST2 XML.  You must
provide the sequences for the analysis (as FASTA or FASTQ), either on
standard input or using the `--fastaFile` option.

Run `beast2-xml.py --help` to see currently supported options:

```sh
$ beast2-xml.py --help
usage: beast2-xml.py [-h] [--clockModel MODEL | --templateFile FILENAME]
                     [--chainLength LENGTH] [--age ID=N [ID=N ...]]
                     [--defaultAge N] [--dateUnit UNIT]
                     [--dateDirection DIRECTION]
                     [--logFileBasename BASE-FILENAME] [--traceLogEvery N]
                     [--treeLogEvery N] [--screenLogEvery N] [--mimicBEAUti]
                     [--sequenceIdDateRegex REGEX]
                     [--sequenceIdDateRegexMayNotMatch] [--fastaFile FILENAME]
                     [--readClass CLASSNAME] [--fasta | --fastq | --fasta-ss]

Given FASTA on stdin (or in a file via the --fastaFile option), write an XML
BEAST2 input file on stdout.

optional arguments:
  -h, --help            show this help message and exit
  --clockModel MODEL    Specify the clock model. Possible values are 'random-
                        local', 'relaxed-exponential', 'relaxed-lognormal', or
                        'strict' (default: strict)
  --templateFile FILENAME
                        The XML template file to use. (default: None)
  --chainLength LENGTH  The MCMC chain length. (default: None)
  --age ID=N [ID=N ...]
                        The age of a sequence. The format is a sequence id, an
                        equals sign, then the age. For convenience, just the
                        first part of a full sequence id (i.e., up to the
                        first space) may be given. May be specified multiple
                        times. (default: None)
  --defaultAge N        The age to use for sequences that are not explicitly
                        given an age via --age. (default: 0.0)
  --dateUnit UNIT       Specify the date unit. Possible values are 'day',
                        'month', or 'year'. (default: year)
  --dateDirection DIRECTION
                        Specify whether dates are back in time from the
                        present or forward in time from some point in the
                        past. Possible values are 'forward' or 'backward'.
                        (default: backward)
  --logFileBasename BASE-FILENAME
                        The base filename to write logs to. A ".log" or
                        ".trees" suffix will be appended to this to make
                        complete log file names. (default: beast-output)
  --traceLogEvery N     How often to write to the trace log file. (default:
                        2000)
  --treeLogEvery N      How often to write to the tree log file. (default:
                        2000)
  --screenLogEvery N    How often to write logging to the screen (i.e.,
                        terminal). (default: 2000)
  --mimicBEAUti         If specified, add attributes to the <beast> tag that
                        mimic what BEAUti uses so that BEAUti will be able to
                        load the XML. (default: False)
  --sequenceIdDateRegex REGEX
                        A regular expression that will be used to capture
                        sequence dates from their ids. The regular expression
                        must have a single (...) capture region. (default:
                        None)
  --sequenceIdDateRegexMayNotMatch
                        If specified (and --sequenceIdDateRegex is given) it
                        will not be considered an error if a sequence id does
                        not match the given regular expression. In that case,
                        sequences will be assigned the default date unless one
                        is given via --age. (default: False)
  --fastaFile FILENAME  The name of the FASTA input file. Standard input will
                        be read if no file name is given.
  --readClass CLASSNAME
                        If specified, give the type of the reads in the input.
                        Possible choices: SSAARead, DNARead, TranslatedRead,
                        RNARead, SSAAReadWithX, AAReadORF, Read, AARead,
                        AAReadWithX. (default: DNARead)
  --fasta               If specified, input will be treated as FASTA. This is
                        the default. (default: False)
  --fastq               If specified, input will be treated as FASTQ.
                        (default: False)
  --fasta-ss            If specified, input will be treated as PDB FASTA
                        (i.e., regular FASTA with each sequence followed by
                        its structure). (default: False)
```

As mentioned, this is extremely simplistic. If you need to generate more
complex XML, you can pass in a template file using `--templateFile`. Your
template will need to have a high-level structure that's similar to those
produced by BEAUti, otherwise the various command-line options for
manipulating the template wont find what they need (you'll see an error
message in this case).

If you don't pass a template file name, a default will be chosen based on
the clock model (`strict` by default).  The [default templates](templates)
all come from BEAUti, so if you generate a template yourself using BEAUti,
you can almost certainly pass it to `beast2-xml.py` to use as a basis to
create variants from.

Note that the generated XML contains just the first part of sequence ids in
the given FASTA input. I'm not sure if this is a requirement, but it's what
BEAUti does and so I have done the same.

## Generate BEAST2 XML in Python

If you want to create BEAST2 XML from your own Python, you can use the
`BEAST2XML` class defined in [beast2xml/beast2.py](beast2xml/beast2.py).

The simplest possible usage is

```python
from beast2xml import BEAST2XML

print(BEAST2XML().toString())
```

There are several options you can pass to the `BEAST2XML` constructor:

```python
class BEAST2XML(object):
    """
    Create BEAST2 XML.

    @param template: A C{str} filename or an open file pointer to read the
        XML template from. If C{None}, a template based on C{clockModel}
        will be used.
    @param clockModel: A C{str} specifying the clock model. Possible values
        are 'random-local', 'relaxed-exponential', 'relaxed-lognormal',
        and 'strict.
    @param sequenceIdDateRegex: If not C{None}, gives a C{str} regular
        expression that will be used to capture sequence dates from their ids.
        The regular expression must have a single (...) capture region.
    @param sequenceIdDateRegexMayNotMatch: If C{True} it should not be
        considered an error if a sequence id does not match the regular
        expression given by C{sequenceIdDateRegex}.
    """
```

and options you can pass to its `toString` method:

```python
def toString(self, chainLength=None, defaultAge=0.0, dateUnit='year',
             dateDirection='backward', logFileBasename=None,
             traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
             transformFunc=None, mimicBEAUti=False):
    """
    @param chainLength: The C{int} length of the MCMC chain. If C{None},
        the value in the template will be retained.
    @param defaultAge: The C{float} age to use for sequences that are not
        explicitly given an age via C{addAge}.
    @param dateUnit: A C{str}, either 'day', 'month', or 'year'
        indicating the date time unit.
    @param dateDirection: A C{str}, either 'backward' or 'forward'
        indicating whether dates are back in time from the present or
        forward in time from some point in the past.
    @param logFileBasename: The C{str} The base filename to write logs to.
        A .log or .trees suffix will be appended to this to make the
        actual log file names.  If C{None}, the log file names in the
        template will be retained.
    @param traceLogEvery: An C{int} specifying how often to write to the
        trace log file. If C{None}, the value in the template will be
        retained.
    @param treeLogEvery: An C{int} specifying how often to write to the
        tree log file. If C{None}, the value in the template will be
        retained.
    @param screenLogEvery: An C{int} specifying how often to write to the
        terminal (screen) log. If C{None}, the value in the template will
        be retained.
    @param transformFunc: If not C{None} A callable that will be passed
        the C{ElementTree} instance and which must return an C{ElementTree}
        instance.
    @param mimicBEAUti: If C{True}, add attributes to the <beast> tag
        in the way that BEAUti does, to allow BEAUti to load the XML we
        produce.
    @raise ValueError: If any required tree elements cannot be found
        (raised by our call to self.findElements).
    @return: C{str} XML.
    """
```

An example of using the Python class can be found in the
[beast2-xml.py](bin/beast2-xml.py) script.  Small examples showing all
functionality can be found in the tests in
[test/testBeast2.py](test/testBeast2.py).

## Development

To run the tests:

```sh
$ make check
```

or if you have [Twisted](https://twistedmatrix.com/trac/) installed, you
can use its `trial` test runner, via

```sh
$ make tcheck
```

You can also use

```sh
$ tox
```

to run tests for various versions of Python.
