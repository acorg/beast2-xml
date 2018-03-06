## BEAST2 XML

This is a first, and *very* simplistic, cut at generating BEAST2 XML from
Python.  BEAST2 is a complex program and so is its input XML.  People
normally generate the input XML using a GUI tool, BEAUTi. BEAUTi is also a
complex tool, and the XML it generates can vary widely. Because BEAUTi is a
GUI tool it's not possible to use it to programmatically generate XML.

I wrote `beast2-xml` because I wanted a way to quickly and easily generate
BEAST2 XML files, from the command line and also from my
[Python](https://www.python.org/) code.

There are a lot of things that could be added to this code! Contributions
welcome.

## This package provides

* a command line script ([bin/beast2-xml.py](bin/beast2-xml.py)) to generate
  [BEAST2](http://beast2.org/) XML files.
* a simplistic Python class (in [beast2xml/beast2.py](beast2xml/beast2.py)
  that may be helpful if you are writing Python that needs to generate
  BEAST2 XML files.  (This Python class is of course used by the command
  line script.)

## Generate XML from the command line

You can use `bin/beast2-xml.py` to quickly generate BEAST2 XML.

Run `bin/beast2-xml.py --help` to see the currently supported options:

```sh
$ bin/beast2-xml.py --help
usage: beast2-xml.py [-h] [--chainLength LENGTH] [--templateFile FILENAME]
                     [--logFileBasename BASE-FILENAME] [--traceLogEvery N]
                     [--treeLogEvery N] [--screenLogEvery N]
                     [--fastaFile FILENAME] [--readClass CLASSNAME]
                     [--fasta | --fastq | --fasta-ss]

Given FASTA on stdin (or in a file via the --fastaFile option), write an XML
BEAST2 input file on stdout.

optional arguments:
  -h, --help            show this help message and exit
  --chainLength LENGTH  The MCMC chain length. (default: None)
  --templateFile FILENAME
                        The XML template file to use. (default: None)
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
  --fastaFile FILENAME  The name of the FASTA input file. Standard input will
                        be read if no file name is given. (default:
                        <_io.TextIOWrapper name='<stdin>' mode='r'
                        encoding='UTF-8'>)
  --readClass CLASSNAME
                        If specified, give the type of the reads in the input.
                        Possible choices: AAReadORF, SSAAReadWithX,
                        AAReadWithX, TranslatedRead, Read, RNARead, DNARead,
                        AARead, SSAARead. (default: DNARead)
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
template will need to have a high-level structure that's similar to the
default one found at the start of [bin/beast2-xml.py](bin/beast2-xml.py) or
the various command-line options for manipulating the template wont find
what they need (you'll see an error message in this case).

## Generate BEAST2 XML in Python

If you want to create BEAST2 XML from your own Python, you can use the
`BEAST2XML` class defined in [beast2xml/beast2.py](beast2xml/beast2.py).

One example of using this class can be found in the
[bin/beast2-xml.py](bin/beast2-xml.py) script.  Further examples can be
found in the tests in [beast2xml/test](beast2xml/test).
