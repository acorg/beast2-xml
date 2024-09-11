from __future__ import print_function, division

import re
import six
from datetime import date
import xml.etree.ElementTree as ET
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from dark.reads import Reads
import pandas as pd


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
        See the explanation in ../bin/beast2-xml.py
    @param sequenceIdAgeRegex: If not C{None}, gives a C{str} regular
        expression that will be used to capture sequence ages from their ids.
        See the explanation in ../bin/beast2-xml.py
    @param sequenceIdRegexMustMatch: If C{True} it will be considered an error
        if a sequence id does not match the regular expression given by
        C{sequenceIdDateRegex} or C{sequenceIdAgeRegex}.
    @param dateUnit: A C{str}, either 'day', 'month', or 'year' indicating the
        date time unit.
    """

    TRACELOG_SUFFIX = ".log"
    TREELOG_SUFFIX = ".trees"

    def __init__(
        self,
        template=None,
        clockModel="strict",
        sequenceIdDateRegex=None,
        sequenceIdAgeRegex=None,
        sequenceIdRegexMustMatch=True,
        dateUnit="year",
    ):
        if template is None:
            self._tree = ET.parse(
                files("beast2xml").joinpath(f"templates/{clockModel}.xml")
            )
        else:
            self._tree = ET.parse(template)
        if sequenceIdDateRegex is None:
            self._sequenceIdDateRegex = None
        else:
            self._sequenceIdDateRegex = re.compile(sequenceIdDateRegex)

        if sequenceIdAgeRegex is None:
            self._sequenceIdAgeRegex = None
        else:
            self._sequenceIdAgeRegex = re.compile(sequenceIdAgeRegex)

        self._sequenceIdRegexMustMatch = sequenceIdRegexMustMatch
        self._sequences = Reads()
        self._ageByFullId = {}
        self._ageByShortId = {}
        self._dateUnit = dateUnit

    @staticmethod
    def find_elements(tree):
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
                    "./run/logger[@id='treelog.t:",
                    "./run/logger[@id='screenlog']"):
            if tag == "./run/logger[@id='treelog.t:":
                tag = tag + data_id + "']"
            element = root.find(tag)
            if element is None:
                raise ValueError('Could not find %r tag in XML template' % tag)
            if tag == 'data':
                data_id = element.get('id')
            result[tag] = element

        return result

    def add_ages(self, age_data, seperator='\t'):
        if isinstance(age_data, str):
            age_data = pd.read_csv(age_data, sep=seperator)
        if isinstance(age_data, pd.DataFrame):
            if len(age_data.columns) != 2:
                raise ValueError("age_data columns must have two columns")
            if 'id' in age_data.columns:
                age_data = age_data.set_index('id')
            elif 'strain' in age_data.columns:
                age_data = age_data.set_index('strain')
            else:
                raise ValueError("An age_data column must be id or strain")
            age_data = age_data.iloc[:, 0]
        if isinstance(age_data, pd.Series):
            age_data = age_data.to_dict()
        if not isinstance(age_data, dict):
            raise ValueError('age_data must be a C{dict} a C{pd.DataFrame}, a C{pd.Series} or a path to tsv/csv.')
        self._ageByFullId.update(age_data)
        age_data = {key.split()[0]: value for key, value in age_data.items()}
        self._ageByShortId.update(age_data)


    def add_age(self, sequenceId, age):
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

    def add_sequence(self, sequence, age=None):
        """
        Add a sequence (optionally with an age) to the run.

        @param sequence: A C{dark.read} instance.
        @param age: If not C{None}, the C{float} age of the sequence.
        """
        self._sequences.add(sequence)

        if age is not None:
            self.add_age(sequence.id, age)
            return

        age = None

        if self._sequenceIdDateRegex:
            match = self._sequenceIdDateRegex.match(sequence.id)
            if match:
                try:
                    sequenceDate = date(
                        *map(
                            int,
                            (
                                match.group("year"),
                                match.group("month"),
                                match.group("day"),
                            ),
                        )
                    )
                except IndexError:
                    pass
                else:
                    days = (date.today() - sequenceDate).days
                    if self._dateUnit == "year":
                        age = days / 365.25
                    elif self._dateUnit == "month":
                        age = days / (365.25 / 12)
                    else:
                        assert self._dateUnit == "day"
                        age = days

        if age is None and self._sequenceIdAgeRegex:
            match = self._sequenceIdAgeRegex.match(sequence.id)
            if match:
                try:
                    age = match.group(1)
                except IndexError:
                    pass

        if age is None:
            if self._sequenceIdRegexMustMatch and (
                self._sequenceIdDateRegex or self._sequenceIdAgeRegex
            ):
                raise ValueError(
                    "No sequence date or age could be found in %r "
                    "using the sequence id date/age regular expressions." % sequence.id
                )
        else:
            self.add_age(sequence.id, float(age))

    def add_sequences(self, sequences):
        """
        Add a set of sequences to the run.

        @param sequences: An iterable of C{dark.read} instances.
        """
        for sequence in sequences:
            self.add_sequence(sequence)

    def _to_xml_tree(self, chainLength=None, defaultAge=0.0,
                 dateDirection='backward', logFileBasename=None,
                 traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
                 transformFunc=None, mimicBEAUti=False):
        """
        @param chainLength: The C{int} length of the MCMC chain. If C{None},
            the value in the template will be retained.
        @param defaultAge: The C{float} age to use for sequences that are not
            explicitly given an age via C{addAge}.
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
        @return: C{str} Element tree.
        """
        if mimicBEAUti:
            root = self._tree.getroot()
            root.set("beautitemplate", "Standard")
            root.set("beautistatus", "")

        elements = self.find_elements(self._tree)


        # Get data element
        data = elements['data']
        data_id = data.get('id')
        tree_logger_key = "./run/logger[@id='treelog.t:" + data_id + "']"
        # Delete any existing children of the data node.
        for child in list(data):
            data.remove(child)

        trait = elements['./run/state/tree/trait']

        # Add in all sequences.
        trait_text = []
        for sequence in sorted(self._sequences): # Sorting adds the sequences alphabetically like in BEAUti.
            id = sequence.id
            short_id = id.split()[0]
            trait_text.append(
                short_id + '=' + str(
                    self._ageByFullId.get(id) or self._ageByShortId.get(short_id) or defaultAge
                ))
            ET.SubElement(data, 'sequence', id='seq_' + short_id, spec="Sequence", taxon=short_id,
                          totalcount='4', value=sequence.sequence)


        trait.set('value', '') # Removes old age info
        trait.text = ',\n'.join(trait_text) + '\n' # Adds new age info
        ##### Conisder line below to add new age info to template. Maybe removing the 2 lines above.
        #trait.set('value', ','.join(trait_text))


        # Set the date direction.
        trait.set("traitname", "date-" + dateDirection)

        # Set the date unit (if not 'year').
        if self._dateUnit != "year":
            trait.set("units", self._dateUnit)

        if chainLength is not None:
            elements["run"].set("chainLength", str(chainLength))

        if logFileBasename is not None:
            # Trace log.
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set("fileName", logFileBasename + self.TRACELOG_SUFFIX)
            # Tree log.
            logger = elements[tree_logger_key]
            logger.set('fileName', logFileBasename + self.TREELOG_SUFFIX)


        if traceLogEvery is not None:
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set("logEvery", str(traceLogEvery))

        if treeLogEvery is not None:
            logger = elements[tree_logger_key]
            logger.set('logEvery', str(treeLogEvery))


        if screenLogEvery is not None:
            logger = elements["./run/logger[@id='screenlog']"]
            logger.set("logEvery", str(screenLogEvery))

        tree = self._tree if transformFunc is None else transformFunc(self._tree)

        return tree

    def to_string(self, chainLength=None, defaultAge=0.0,
                  dateDirection='backward', logFileBasename=None,
                  traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
                  transformFunc=None, mimicBEAUti=False):
        """
        @param chainLength: The C{int} length of the MCMC chain. If C{None},
            the value in the template will be retained.
        @param defaultAge: The C{float} age to use for sequences that are not
            explicitly given an age via C{addAge}.
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
        @return: C{str} representation of XML.
        """
        tree = self._to_xml_tree(chainLength=chainLength, defaultAge=defaultAge,
                                 dateDirection=dateDirection, logFileBasename=logFileBasename,
                                 traceLogEvery=traceLogEvery, treeLogEvery=treeLogEvery, screenLogEvery=screenLogEvery,
                                 transformFunc=transformFunc, mimicBEAUti=mimicBEAUti)

        stream = six.StringIO()
        tree.write(stream, "unicode" if six.PY3 else "utf-8", xml_declaration=True)
        return stream.getvalue()

    def to_xml(self, path, chainLength=None, defaultAge=0.0,
               dateDirection='backward', logFileBasename=None,
               traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
               transformFunc=None, mimicBEAUti=False):
        """
        @param path: The C{str} filename to write the XML to.
        @param chainLength: The C{int} length of the MCMC chain. If C{None},
            the value in the template will be retained.
        @param defaultAge: The C{float} age to use for sequences that are not
            explicitly given an age via C{addAge}.
        @param dateDirection: A C{str}, either 'backward' or
        'forward'
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
        @return: None.
        """
        if not isinstance(path, str):
            raise TypeError('filename must be a string.')
        tree = self._to_xml_tree(chainLength=chainLength, defaultAge=defaultAge,
                                 dateDirection=dateDirection, logFileBasename=logFileBasename,
                                 traceLogEvery=traceLogEvery, treeLogEvery=treeLogEvery, screenLogEvery=screenLogEvery,
                                 transformFunc=transformFunc, mimicBEAUti=mimicBEAUti)
        tree.write(path, 'unicode' if six.PY3 else 'utf-8', xml_declaration=True)