from __future__ import print_function, division

import re
import six
import pkg_resources
import xml.etree.ElementTree as ET
from dark.reads import Reads


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

    TRACELOG_SUFFIX = '.log'
    TREELOG_SUFFIX = '.trees'

    def __init__(self, template=None, clockModel='strict',
                 sequenceIdDateRegex=None,
                 sequenceIdDateRegexMayNotMatch=False):
        if template is None:
            self._tree = ET.parse(
                pkg_resources.resource_filename(
                    'beast2xml', 'templates/%s.xml' % clockModel))
        else:
            self._tree = ET.parse(template)
        if sequenceIdDateRegex is None:
            self._sequenceIdDateRegex = None
        else:
            self._sequenceIdDateRegex = re.compile(sequenceIdDateRegex)

        self._sequenceIdDateRegexMayNotMatch = sequenceIdDateRegexMayNotMatch
        self._sequences = Reads()
        self._ageByFullId = {}
        self._ageByShortId = {}

    @staticmethod
    def findElements(tree):
        """
        Check that an XML tree has the required structure and return the found
        elements.

        @param tree: An C{ET.ElementTree} instance.
        @raise ValueError: If any required element cannot be found.
        @return: A C{dict} keyed by C{str} element paths with C{ET.Element}
            instances as values.
        """
        result = {}
        root = tree.getroot()

        for tag in ("data",
                    "run",
                    "./run/state/tree/trait",
                    "./run/logger[@id='tracelog']",
                    "./run/logger[@id='treelog.t:alignment']",
                    "./run/logger[@id='screenlog']"):
            element = root.find(tag)
            if element is None:
                raise ValueError('Could not find %r tag in XML template' % tag)
            result[tag] = element

        return result

    def addAge(self, sequenceId, age):
        """
        Specify the age of a sequence.

        @param sequenceId: The C{str} name of a sequence id. An age will be
            recorded for both the full id and for the part of it up to its
            first space. This makes it convenient for giving sequence ids from
            the command line (e.g., using ../bin/beast2-xml.py) without having
            to specify the full id. On id lookup (when creating XML), full ids
            always have precedence so there is no danger of short id
            duplication error if full ids are always used.
        @param age: The C{float} age of the sequence.
        """
        self._ageByShortId[sequenceId.split()[0]] = age
        self._ageByFullId[sequenceId] = age

    def addSequence(self, sequence, age=None):
        """
        Add a sequence (optionally with an age) to the run.

        @param sequence: A C{dark.read} instance.
        @param age: If not C{None}, the C{float} age of the sequence.
        """
        self._sequences.add(sequence)
        if age is not None:
            self.addAge(sequence.id, age)
        elif self._sequenceIdDateRegex:
            match = self._sequenceIdDateRegex.match(sequence.id)
            if match:
                try:
                    age = match.group(1)
                except IndexError:
                    match = None
                else:
                    self.addAge(sequence.id, float(age))

            if not self._sequenceIdDateRegexMayNotMatch and not match:
                raise ValueError(
                    'No sequence date could be found in %r '
                    'using the sequence id date regex' % sequence.id)

    def addSequences(self, sequences):
        """
        Add a set of sequences to the run.

        @param sequences: An iterable of C{dark.read} instances.
        """
        for sequence in sequences:
            self._sequences.add(sequence)

    def toString(self, chainLength=None, defaultAge=0.0, dateUnit='year',
                 dateDirection='backward', logFileBasename=None,
                 traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
                 transformFunc=None, mimicBEAUTi=False):
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
        @param mimicBEAUTi: If C{True}, add attributes to the <beast> tag
            in the way that BEAUTi does, to allow BEAUTi to load the XML we
            produce.
        @raise ValueError: If any required tree elements cannot be found
            (raised by our call to self.findElements).
        @return: C{str} XML.
        """
        if mimicBEAUTi:
            root = self._tree.getroot()
            root.set('beautitemplate', 'Standard')
            root.set('beautistatus', '')

        elements = self.findElements(self._tree)

        # Delete any existing children of the data node.
        data = elements['data']
        for child in data:
            data.remove(child)

        # Add in all sequences.
        trait = elements['./run/state/tree/trait']
        traitText = []
        for sequence in self._sequences:
            id_ = sequence.id
            shortId = id_.split()[0]
            traitText.append(
                '%s=%f' % (shortId, (self._ageByFullId.get(id_) or
                                     self._ageByShortId.get(shortId) or
                                     defaultAge)))
            ET.SubElement(data, 'sequence', id='seq_' + shortId, taxon=shortId,
                          totalcount='4', value=sequence.sequence)

        trait.text = ',\n'.join(traitText) + '\n'

        # Set the date direction.
        trait.set('traitname', 'date-' + dateDirection)

        # Set the date unit (if not 'year').
        if dateUnit != 'year':
            trait.set('units', dateUnit)

        if chainLength is not None:
            elements['run'].set('chainLength', str(chainLength))

        if logFileBasename is not None:
            # Trace log.
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set('fileName', logFileBasename + self.TRACELOG_SUFFIX)
            # Tree log.
            logger = elements["./run/logger[@id='treelog.t:alignment']"]
            logger.set('fileName', logFileBasename + self.TREELOG_SUFFIX)

        if traceLogEvery is not None:
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set('logEvery', str(traceLogEvery))

        if treeLogEvery is not None:
            logger = elements["./run/logger[@id='treelog.t:alignment']"]
            logger.set('logEvery', str(treeLogEvery))

        if screenLogEvery is not None:
            logger = elements["./run/logger[@id='screenlog']"]
            logger.set('logEvery', str(screenLogEvery))

        tree = (self._tree if transformFunc is None
                else transformFunc(self._tree))

        stream = six.StringIO()
        tree.write(stream, 'unicode' if six.PY3 else 'utf-8',
                   xml_declaration=True)
        return stream.getvalue()
