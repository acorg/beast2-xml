from unittest import TestCase
from six.moves import builtins
from six import assertRaisesRegex, PY3, StringIO
import xml.etree.ElementTree as ET
from dark.reads import Read
from beast2xml import BEAST2XML

try:
    from unittest.mock import mock_open, patch
except ImportError:
    from mock import mock_open, patch

open_ = ('builtins' if PY3 else '__builtin__') + '.open'


class TestTemplate(TestCase):
    """
    Test the BEAST2XML class when a template is passed.
    """
    @patch(open_, new_callable=mock_open,
           read_data="<?xml version='1.0' encoding='UTF-8'?>")
    def testNoElementXML(self, mock):
        """
        Passing a template that has an XML header but no elements to
        BEAST2XML must raise a syntax error.
        """
        error = '^no element found: line 1, column 38$'
        assertRaisesRegex(self, ET.ParseError, error, BEAST2XML,
                          template='filename')

    @patch(open_, new_callable=mock_open, read_data='not XML')
    def testNonXMLTemplate(self, mock):
        """
        Passing a template that is not XML to BEAST2XML must raise a
        ParseError.
        """
        error = '^syntax error: line 1, column 0$'
        assertRaisesRegex(self, ET.ParseError, error, BEAST2XML,
                          template='filename')

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' "
                      "encoding='UTF-8'?><beast></beast>"))
    def testTemplateWithNoData(self, mock):
        """
        Passing a template that has no <data> tag to BEAST2XML must raise a
        ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = "^Could not find 'data' tag in XML template$"
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' encoding='UTF-8'?>"
                      '<beast><data></data></beast>'))
    def testTemplateWithNoRun(self, mock):
        """
        Passing a template that has no <run> tag to BEAST2XML must raise a
        ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = "^Could not find 'run' tag in XML template$"
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' encoding='UTF-8'?>"
                      '<beast><data></data><run></run></beast>'))
    def testTemplateWithNoTrait(self, mock):
        """
        Passing a template that has no <trait> tag to BEAST2XML must raise
        a ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = ("^Could not find '\./run/state/tree/trait' tag in XML "
                 "template$")
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' encoding='UTF-8'?>"
                      '<beast><data></data><run><state><tree><trait>'
                      '</trait></tree></state></run></beast>'))
    def testTemplateWithNoTracelog(self, mock):
        """
        Passing a template that has no tracelog logger tag to BEAST2XML
        must raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = ('^Could not find "\./run/logger\[@id=\'tracelog\'\]" tag '
                 'in XML template$')
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' encoding='UTF-8'?>"
                      '<beast><data></data><run>'
                      '<state><tree><trait></trait></tree></state>'
                      '<logger id="tracelog"></logger>'
                      '</run></beast>'))
    def testTemplateWithNoTreelog(self, mock):
        """
        Passing a template that has no treelog logger tag to BEAST2XML must
        raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = (
            '^Could not find '
            '"\./run/logger\[@id=\'treelog\.t:alignment\'\]" '
            'tag in XML template$')
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open,
           read_data=("<?xml version='1.0' encoding='UTF-8'?>"
                      '<beast><data></data><run>'
                      '<state><tree><trait></trait></tree></state>'
                      '<logger id="tracelog"></logger>'
                      '<logger id="treelog.t:alignment"></logger>'
                      '</run></beast>'))
    def testTemplateWithNoScreenlog(self, mock):
        """
        Passing a template that has no screenlog logger tag to BEAST2XML
        must raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template='filename')
        error = (
            '^Could not find "\./run/logger\[@id=\'screenlog\'\]" '
            'tag in XML template$')
        assertRaisesRegex(self, ValueError, error, xml.toString)

    @patch(open_, new_callable=mock_open)
    def testNonExistentTemplateFile(self, mock):
        """
        Passing a template filename that does not exist must raise a
        FileNotFoundError (PY3) or IOError (PY2).
        """
        errorClass = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = errorClass('abc')
        error = '^abc$'
        assertRaisesRegex(self, errorClass, error, BEAST2XML,
                          template='filename')

    def testTemplateIsOpenFile(self):
        """
        BEAST2XML must run correctly when initialized from an open file
        pointer.
        """
        ET.fromstring(
            BEAST2XML(
                template=StringIO(BEAST2XML().toString())
            ).toString()
        )


class TestMisc(TestCase):
    """
    Miscellaneous tests.
    """
    def testNoArgsGivesValidXML(self):
        """
        Passing no template or clock model to BEAST2XML and no arguments to
        toString must produce valid XML.
        """
        ET.fromstring(BEAST2XML().toString())

    @patch(open_, new_callable=mock_open)
    def testNonExistentClockModelFile(self, mock):
        """
        Passing a clock model that does not correspond to an existing
        clock model template file must raise FileNotFoundError (PY3) or
        IOError (PY2).
        """
        errorClass = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = errorClass('abc')
        error = '^abc$'
        assertRaisesRegex(self, errorClass, error, BEAST2XML,
                          clockModel='filename')


class ClockModelMixin(object):
    """
    Tests that will be run with all clock models.
    """

    def testOneSequence(self):
        """
        Adding a sequence must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        xml.addSequence(Read('id1', 'ACTG'))
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        # The sequence must be the only child of the <data> tag.
        data = elements['data']
        self.assertEqual(1, len(data))
        child = data[0]
        self.assertEqual('sequence', child.tag)
        self.assertEqual('ACTG', child.get('value'))
        self.assertEqual('4', child.get('totalcount'))
        self.assertEqual('id1', child.get('taxon'))
        self.assertEqual('seq_id1', child.get('id'))
        self.assertIs(None, child.text)

        # The sequence id with the default age of 0.0 must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1=0.0') > -1)

    def testSequenceIdDateRegex(self):
        """
        Using a sequence id date regex must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL,
                        sequenceIdDateRegex='^.*_([0-9]+)')
        xml.addSequence(Read('id1_80_xxx', 'ACTG'))
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        # The sequence id with the default age of 0.0 must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1_80_xxx=80.0') > -1)

    def testSequenceIdDateRegexNonMatching(self):
        """
        Using a sequence id date regex with a sequence id that does not match
        must result in a ValueError.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL,
                        sequenceIdDateRegex='^.*_([0-9]+)')
        error = ("^No sequence date could be found in 'id1' using the "
                 "sequence id date regex$")
        assertRaisesRegex(self, ValueError, error, xml.addSequence,
                          Read('id1', 'ACTG'))

    def testSequenceIdDateRegexNonMatchingNotAnError(self):
        """
        Using a sequence id date regex that doesn't match is not an error if
        we pass sequenceIdDateRegexMayNotMatch=True, in which case the default
        age should be assigned.
        """
        xml = BEAST2XML(
            clockModel=self.CLOCK_MODEL,
            sequenceIdDateRegex='^.*_([0-9]+)',
            sequenceIdDateRegexMayNotMatch=True
        )
        xml.addSequence(Read('id1_xxx', 'ACTG'))
        tree = ET.ElementTree(ET.fromstring(xml.toString(defaultAge=50)))
        elements = BEAST2XML.findElements(tree)

        # The sequence id with the passed default age must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1_xxx=50.0') > -1)

    def testOneSequenceWithAge(self):
        """
        Adding a sequence with an age must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        xml.addSequence(Read('id1', 'ACTG'))
        xml.addAge('id1', 44)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        # The sequence id with the given age must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1=44.0') > -1)

    def testOneSequenceWithAgeAddedTogether(self):
        """
        Adding a sequence with an age (both passed to addSequence) must result
        in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        xml.addSequence(Read('id1', 'ACTG'), 44)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        # The sequence id with the given age must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1=44.0') > -1)

    def testAddSequences(self):
        """
        Adding several sequences must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        xml.addSequences([
            Read('id1', 'GG'), Read('id2', 'CC'), Read('id3', 'AA')])
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        # The sequences must be the children of the <data> tag.
        data = elements['data']
        self.assertEqual(3, len(data))

        child = data[0]
        self.assertEqual('sequence', child.tag)
        self.assertEqual('GG', child.get('value'))
        self.assertEqual('4', child.get('totalcount'))
        self.assertEqual('id1', child.get('taxon'))
        self.assertEqual('seq_id1', child.get('id'))
        self.assertIs(None, child.text)

        child = data[1]
        self.assertEqual('sequence', child.tag)
        self.assertEqual('CC', child.get('value'))
        self.assertEqual('4', child.get('totalcount'))
        self.assertEqual('id2', child.get('taxon'))
        self.assertEqual('seq_id2', child.get('id'))
        self.assertIs(None, child.text)

        child = data[2]
        self.assertEqual('sequence', child.tag)
        self.assertEqual('AA', child.get('value'))
        self.assertEqual('4', child.get('totalcount'))
        self.assertEqual('id3', child.get('taxon'))
        self.assertEqual('seq_id3', child.get('id'))
        self.assertIs(None, child.text)

        # The sequence ids with the default age of 0.0 must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1=0.0') > -1)
        self.assertTrue(trait.text.find('id2=0.0') > -1)
        self.assertTrue(trait.text.find('id3=0.0') > -1)

    def testChainLength(self):
        """
        Passing a chain length to toString must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(chainLength=100)))
        elements = BEAST2XML.findElements(tree)
        self.assertEqual('100', elements['run'].get('chainLength'))

    def testDefaultAge(self):
        """
        Passing a default age to toString must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        xml.addSequence(Read('id1', 'ACTG'))
        tree = ET.ElementTree(ET.fromstring(xml.toString(defaultAge=33.0)))
        elements = BEAST2XML.findElements(tree)

        # The sequence id with the default age of 0.0 must be in the traits.
        trait = elements['./run/state/tree/trait']
        self.assertTrue(trait.text.find('id1=33.0') > -1)

    def testLogFileBaseName(self):
        """
        Passing a log file base name to toString must result in the expected
        log file names in the XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(logFileBasename='xxx')))
        elements = BEAST2XML.findElements(tree)

        logger = elements["./run/logger[@id='tracelog']"]
        self.assertEqual('xxx' + BEAST2XML.TRACELOG_SUFFIX,
                         logger.get('fileName'))

        logger = elements["./run/logger[@id='treelog.t:alignment']"]
        self.assertEqual('xxx' + BEAST2XML.TREELOG_SUFFIX,
                         logger.get('fileName'))

    def testTraceLogEvery(self):
        """
        Passing a traceLogEvery value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(traceLogEvery=300)))
        elements = BEAST2XML.findElements(tree)

        logger = elements["./run/logger[@id='tracelog']"]
        self.assertEqual('300', logger.get('logEvery'))

    def testTreeLogEvery(self):
        """
        Passing a treeLogEvery value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(treeLogEvery=300)))
        elements = BEAST2XML.findElements(tree)

        logger = elements["./run/logger[@id='treelog.t:alignment']"]
        self.assertEqual('300', logger.get('logEvery'))

    def testScreenLogEvery(self):
        """
        Passing a screenLogEvery value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(screenLogEvery=300)))
        elements = BEAST2XML.findElements(tree)

        logger = elements["./run/logger[@id='screenlog']"]
        self.assertEqual('300', logger.get('logEvery'))

    def testTransformFunction(self):
        """
        Passing a transform function to toString must result in the expected
        XML.
        """
        def transform(tree):
            return ET.ElementTree(ET.fromstring(
                "<?xml version='1.0' encoding='UTF-8'?><hello/>"))

        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        expected = ("<?xml version='1.0' encoding='" +
                    ('UTF-8' if PY3 else 'utf-8') +
                    "'?>\n<hello />")
        self.assertEqual(expected, xml.toString(transformFunc=transform))

    def testDefaultDateDirection(self):
        """
        Passing no dateDirection toString must result in the expected date
        direction in the XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString()))
        elements = BEAST2XML.findElements(tree)

        trait = elements['./run/state/tree/trait']
        self.assertEqual('date-backward', trait.get('traitname'))

    def testDateDirection(self):
        """
        Passing a dateDirection value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(
            xml.toString(dateDirection='forward')))
        elements = BEAST2XML.findElements(tree)

        trait = elements['./run/state/tree/trait']
        self.assertEqual('date-forward', trait.get('traitname'))

    def testNoDateUnit(self):
        """
        Passing no dateUnit value to toString must result in the expected XML
        (with no 'units' attribute in the trait).
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        elements = BEAST2XML.findElements(tree)

        trait = elements['./run/state/tree/trait']
        self.assertEqual(None, trait.get('units'))

    def testDateUnit(self):
        """
        Passing a dateUnit value to toString must result in the expected XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString(dateUnit='day')))
        elements = BEAST2XML.findElements(tree)

        trait = elements['./run/state/tree/trait']
        self.assertEqual('day', trait.get('units'))

    def testDontMimicBEAUTi(self):
        """
        If mimicBEAUTi is not passed to toString the BEAUTi attributes must
        not appear in the <beast> tag in the XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        root = tree.getroot()
        self.assertEqual(None, root.get('beautitemplate'))
        self.assertEqual(None, root.get('beautistatus'))

    def testMimicBEAUTi(self):
        """
        Passing mimicBEAUTi=True to toString must result in the expected
        BEAUTi attributes in the <beast> tag in the XML.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString(mimicBEAUTi=True)))
        root = tree.getroot()
        self.assertEqual('Standard', root.get('beautitemplate'))
        self.assertEqual('', root.get('beautistatus'))


class TestRandomLocalClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'random-local' clock model is used.
    """
    CLOCK_MODEL = 'random-local'

    def testExpectedTemplate(self):
        """
        Passing a 'random-local' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldMean.c:alignment"]')
        self.assertTrue(logger is not None)
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldStdev.c:alignment"]')
        self.assertTrue(logger is not None)


class TestRelaxedExponentialClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'relaxed-exponential' clock model is used.
    """
    CLOCK_MODEL = 'relaxed-exponential'

    def testExpectedTemplate(self):
        """
        Passing a 'relaxed-exponential' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucedMean.c:alignment"]')
        self.assertTrue(logger is not None)


class TestRelaxedLognormalClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'relaxed-lognormal' clock model is used.
    """
    CLOCK_MODEL = 'relaxed-lognormal'

    def testExpectedTemplate(self):
        """
        Passing a 'relaxed-lognormal' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldMean.c:alignment"]')
        self.assertTrue(logger is not None)
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldStdev.c:alignment"]')
        self.assertTrue(logger is not None)


class TestStrictClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'strict' clock model is used.
    """
    CLOCK_MODEL = 'strict'

    def testExpectedTemplate(self):
        """
        Passing a 'strict' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clockModel=self.CLOCK_MODEL)
        tree = ET.ElementTree(ET.fromstring(xml.toString()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="clockRate.c:alignment"]')
        self.assertTrue(logger is not None)
