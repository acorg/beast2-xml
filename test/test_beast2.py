from unittest import TestCase
from six.moves import builtins
from six import assertRaisesRegex, PY3, StringIO
import xml.etree.ElementTree as ET
from dark.reads import Read
from beast2xml import BEAST2XML
from datetime import date, timedelta

try:
    from unittest.mock import mock_open, patch
except ImportError:
    from mock import mock_open, patch

open_ = ("builtins" if PY3 else "__builtin__") + ".open"


class TestTemplate(TestCase):
    """
    Test the BEAST2XML class when a template is passed.
    """

    @patch(
        open_,
        new_callable=mock_open,
        read_data="<?xml version='1.0' encoding='UTF-8'?>",
    )
    def test_no_element_xml(self, mock):
        """
        Passing a temp
        late that has an XML header but no elements to
        BEAST2XML must raise a syntax error.
        """
        error = "^no element found: line 1, column 38$"
        assertRaisesRegex(self, ET.ParseError, error, BEAST2XML, template="filename")

    @patch(open_, new_callable=mock_open, read_data="not XML")
    def test_non_xml_template(self, mock):
        """
        Passing a template that is not XML to BEAST2XML must raise a
        ParseError.
        """
        error = "^syntax error: line 1, column 0$"
        assertRaisesRegex(self, ET.ParseError, error, BEAST2XML, template="filename")

    @patch(
        open_,
        new_callable=mock_open,
        read_data="<?xml version='1.0' " "encoding='UTF-8'?><beast></beast>",
    )
    def test_template_with_no_data(self, mock):
        """
        Passing a template that has no <data> tag to BEAST2XML must raise a
        ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = "^Could not find 'data' tag in XML template$"
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(
        open_,
        new_callable=mock_open,
        read_data=(
            "<?xml version='1.0' encoding='UTF-8'?>" "<beast><data></data></beast>"
        ),
    )
    def test_template_with_no_run(self, mock):
        """
        Passing a template that has no <run> tag to BEAST2XML must raise a
        ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = "^Could not find 'run' tag in XML template$"
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(
        open_,
        new_callable=mock_open,
        read_data=(
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<beast><data id='alignment'></data><run></run></beast>"
        ),
    )
    def test_template_with_no_trait(self, mock):
        """
        Passing a template that has no <trait> tag to BEAST2XML must raise
        a ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = r"^Could not find '\./run/state/tree/trait' tag in XML " r"template$"
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(
        open_,
        new_callable=mock_open,
        read_data=(
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<beast><data id='alignment'></data><run><state><tree><trait>"
            "</trait></tree></state></run></beast>"
        ),
    )
    def test_template_with_no_tracelog(self, mock):
        """
        Passing a template that has no tracelog logger tag to BEAST2XML
        must raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = (
            r'^Could not find "\./run/logger\[@id=\'tracelog\'\]" tag '
            r"in XML template$"
        )
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(
        open_,
        new_callable=mock_open,
        read_data=(
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<beast><data id='alignment'></data><run>"
            "<state><tree><trait></trait></tree></state>"
            '<logger id="tracelog"></logger>'
            "</run></beast>"
        ),
    )
    def test_template_with_no_treelog(self, mock):
        """
        Passing a template that has no treelog logger tag to BEAST2XML must
        raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = (
            r"^Could not find "
            r'"\./run/logger\[@id=\'treelog\.t:alignment\'\]" '
            r"tag in XML template$"
        )
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(
        open_,
        new_callable=mock_open,
        read_data=(
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<beast><data id='alignment'></data><run>"
            "<state><tree><trait></trait></tree></state>"
            '<logger id="tracelog"></logger>'
            '<logger id="treelog.t:alignment"></logger>'
            "</run></beast>"
        ),
    )
    def test_template_with_no_screenlog(self, mock):
        """
        Passing a template that has no screenlog logger tag to BEAST2XML
        must raise a ValueError when toString is called.
        """
        xml = BEAST2XML(template="filename")
        error = (
            r'^Could not find "\./run/logger\[@id=\'screenlog\'\]" '
            r"tag in XML template$"
        )
        assertRaisesRegex(self, ValueError, error, xml.to_string)

    @patch(open_, new_callable=mock_open)
    def test_non_existent_template_file(self, mock):
        """
        Passing a template filename that does not exist must raise a
        FileNotFoundError (PY3) or IOError (PY2).
        """
        error_class = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = error_class("abc")
        error = "^abc$"
        assertRaisesRegex(self, error_class, error, BEAST2XML, template="filename")

    def test_template_is_open_file(self):
        """
        BEAST2XML must run correctly when initialized from an open file
        pointer.
        """
        ET.fromstring(BEAST2XML(template=StringIO(BEAST2XML().to_string())).to_string())


class TestMisc(TestCase):
    """
    Miscellaneous tests.
    """

    def test_no_args_gives_valid_xml(self):
        """
        Passing no template or clock model to BEAST2XML and no arguments to
        toString must produce valid XML.
        """
        ET.fromstring(BEAST2XML().to_string())

    @patch(open_, new_callable=mock_open)
    def test_non_existent_clock_model_file(self, mock):
        """
        Passing a clock model that does not correspond to an existing
        clock model template file must raise FileNotFoundError (PY3) or
        IOError (PY2).
        """
        error_class = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = error_class("abc")
        error = "^abc$"
        assertRaisesRegex(self, error_class, error, BEAST2XML, clock_model="filename")


class ClockModelMixin(object):
    """
    Tests that will be run with all clock models.
    """

    def test_one_sequence(self):
        """
        Adding a sequence must result in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        xml.add_sequence(Read("id1", "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence must be the only child of the <data> tag.
        data = elements["data"]
        self.assertEqual(1, len(data))
        child = data[0]
        self.assertEqual("sequence", child.tag)
        self.assertEqual("ACTG", child.get("value"))
        self.assertEqual("4", child.get("totalcount"))
        self.assertEqual("id1", child.get("taxon"))
        self.assertEqual("seq_id1", child.get("id"))
        self.assertIs(None, child.text)

        # The sequence id with the default age of 0.0 must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1=0.0")

    def test_sequence_id_age_regex(self):
        """
        Using a sequence id age regex must result in the expected XML.
        """
        xml = BEAST2XML(
            clock_model=self.clock_model, sequence_id_age_regex="^.*_([0-9]+)"
        )
        xml.add_sequence(Read("id1_80_xxx", "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with the default age of 0.0 must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1_80_xxx=80.0")

    def test_sequence_id_age_regex_non_matching(self):
        """
        Using a sequence id age regex with a sequence id that does not match
        must result in a ValueError.
        """
        xml = BEAST2XML(
            clock_model=self.clock_model, sequence_id_age_regex="^.*_([0-9]+)"
        )
        error = (
            r"^No sequence date or age could be found in 'id1' using the "
            r"sequence id date/age regular expressions\.$"
        )
        assertRaisesRegex(
            self, ValueError, error, xml.add_sequence, Read("id1", "ACTG")
        )

    def test_sequence_id_regex_non_matching_not_an_error(self):
        """
        Using a sequence id age regex that doesn't match is not an error if
        we pass sequence_id_regex_must_match=False, in which case the default
        age should be assigned.
        """
        xml = BEAST2XML(
            clock_model=self.clock_model,
            sequence_id_age_regex="^.*_([0-9]+)",
            sequence_id_regex_must_match=False,
        )
        xml.add_sequence(Read("id1_xxx", "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string(default_age=50)))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with the passed default age must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1_xxx=50")

    def test_one_sequence_with_date_regex_and_date_unit_in_years(self):
        """
        Adding a sequence with a date regex and date units in years must
        result in the expected XML.
        """
        sequence_date = (date.today() - timedelta(days=2 * 365)).strftime("%Y-%m-%d")
        r = r"^.*_(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)"
        id_ = "id1_" + sequence_date

        xml = BEAST2XML(clock_model=self.clock_model, sequence_id_date_regex=r)
        xml.add_sequence(Read(id_, "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with an age of ~2 years must be in the traits.
        trait = elements["./run/state/tree/trait"]
        # Note that the following is not exact!
        trait_value = float(trait.attrib["value"].split("=")[1])
        self.assertAlmostEqual(trait_value, 1.97, places=1)
        self.assertIs(None, trait.get("units"))

    def test_one_sequence_with_date_regex_and_date_unit_in_months(self):
        """
        Adding a sequence with a date regex and date units in months must
        result in the expected XML.
        """
        sequence_date = (date.today() - timedelta(days=2 * (365.25 / 12))).strftime(
            "%Y-%m-%d"
        )
        r = r"^.*_(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)"
        id_ = "id1_" + sequence_date

        xml = BEAST2XML(
            clock_model=self.clock_model, sequence_id_date_regex=r, date_unit="month"
        )
        xml.add_sequence(Read(id_, "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with an age of ~2 months must be in the traits.
        trait = elements["./run/state/tree/trait"]
        # Note that the following is not exact!
        trait_value = float(trait.attrib["value"].split("=")[1])
        self.assertAlmostEqual(trait_value, 1.9712, places=2)
        self.assertEqual("month", trait.get("units"))

    def test_one_sequence_with_date_regex_and_date_unit_in_days(self):
        """
        Adding a sequence with a date regex and date units in days must
        result in the expected XML.
        """
        sequence_date = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
        r = r"^.*_(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)"
        id_ = "id1_" + sequence_date

        xml = BEAST2XML(
            clock_model=self.clock_model, sequence_id_date_regex=r, date_unit="day"
        )
        xml.add_sequence(Read(id_, "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with an age of 10 days must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], id_ + "=10.0")
        self.assertEqual("day", trait.get("units"))

    def test_one_sequence_with_age(self):
        """
        Adding a sequence with an age must result in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        xml.add_sequence(Read("id1", "ACTG"))
        xml.add_age("id1", 44)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with the given age must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1=44")

    def test_one_sequence_with_age_added_together(self):
        """
        Adding a sequence with an age (both passed to addSequence) must result
        in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        xml.add_sequence(Read("id1", "ACTG"), 44)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with the given age must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1=44")

    def test_add_sequences(self):
        """
        Adding several sequences must result in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        xml.add_sequences([Read("id1", "GG"), Read("id2", "CC"), Read("id3", "AA")])
        xml_tree_string = xml.to_string()
        tree = ET.ElementTree(ET.fromstring(xml_tree_string))
        elements = BEAST2XML.find_elements(tree)

        # The sequences must be the children of the <data> tag.
        data = elements["data"]
        self.assertEqual(3, len(data))

        child = data[0]
        self.assertEqual("sequence", child.tag)
        self.assertEqual("GG", child.get("value"))
        self.assertEqual("4", child.get("totalcount"))
        self.assertEqual("id1", child.get("taxon"))
        self.assertEqual("seq_id1", child.get("id"))
        self.assertIs(None, child.text)

        child = data[1]
        self.assertEqual("sequence", child.tag)
        self.assertEqual("CC", child.get("value"))
        self.assertEqual("4", child.get("totalcount"))
        self.assertEqual("id2", child.get("taxon"))
        self.assertEqual("seq_id2", child.get("id"))
        self.assertIs(None, child.text)

        child = data[2]
        self.assertEqual("sequence", child.tag)
        self.assertEqual("AA", child.get("value"))
        self.assertEqual("4", child.get("totalcount"))
        self.assertEqual("id3", child.get("taxon"))
        self.assertEqual("seq_id3", child.get("id"))
        self.assertIs(None, child.text)

        # The sequence ids with the default age of 0.0 must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1=0.0,id2=0.0,id3=0.0")

    def test_chain_length(self):
        """
        Passing a chain length to toString must result in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(chain_length=100)))
        elements = BEAST2XML.find_elements(tree)
        self.assertEqual("100", elements["run"].get("chainLength"))

    def test_default_age(self):
        """
        Passing a default age to toString must result in the expected XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        xml.add_sequence(Read("id1", "ACTG"))
        tree = ET.ElementTree(ET.fromstring(xml.to_string(default_age=33.0)))
        elements = BEAST2XML.find_elements(tree)

        # The sequence id with the default age of 33.0 must be in the traits.
        trait = elements["./run/state/tree/trait"]
        self.assertEqual(trait.attrib["value"], "id1=33.0")

    def test_log_file_base_name(self):
        """
        Passing a log file base name to toString must result in the expected
        log file names in the XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(log_file_basename="xxx")))
        elements = BEAST2XML.find_elements(tree)

        logger = elements["./run/logger[@id='tracelog']"]
        self.assertEqual("xxx" + BEAST2XML.TRACELOG_SUFFIX, logger.get("fileName"))

        logger = elements["./run/logger[@id='treelog.t:alignment']"]
        self.assertEqual("xxx" + BEAST2XML.TREELOG_SUFFIX, logger.get("fileName"))

    def test_trace_log_every(self):
        """
        Passing a trace_log_every value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(trace_log_every=300)))
        elements = BEAST2XML.find_elements(tree)

        logger = elements["./run/logger[@id='tracelog']"]
        self.assertEqual("300", logger.get("logEvery"))

    def test_tree_log_every(self):
        """
        Passing a tree_log_every value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(tree_log_every=300)))
        elements = BEAST2XML.find_elements(tree)

        logger = elements["./run/logger[@id='treelog.t:alignment']"]
        self.assertEqual("300", logger.get("logEvery"))

    def test_screen_log_every(self):
        """
        Passing a screen_log_every value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(screen_log_every=300)))
        elements = BEAST2XML.find_elements(tree)

        logger = elements["./run/logger[@id='screenlog']"]
        self.assertEqual("300", logger.get("logEvery"))

    def test_transform_function(self):
        """
        Passing a transform function to toString must result in the expected
        XML.
        """

        def transform(tree):
            return ET.ElementTree(
                ET.fromstring("<?xml version='1.0' encoding='UTF-8'?><hello/>")
            )

        xml = BEAST2XML(clock_model=self.clock_model)
        expected = "<?xml version='1.0' encoding='utf-8'?>\n<hello />"
        self.assertEqual(expected, xml.to_string(transform_func=transform))

    def test_default_date_direction(self):
        """
        Passing no date_direction toString must result in the expected date
        direction in the XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        trait = elements["./run/state/tree/trait"]
        self.assertEqual("date-backward", trait.get("traitname"))

    def test_date_direction(self):
        """
        Passing a date_direction value to toString must result in the expected
        XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(date_direction="forward")))
        elements = BEAST2XML.find_elements(tree)

        trait = elements["./run/state/tree/trait"]
        self.assertEqual("date-forward", trait.get("traitname"))

    def test_no_date_unit(self):
        """
        Passing no date_unit value to the constructor must result in the
        expected XML (with no 'units' attribute in the trait).
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        trait = elements["./run/state/tree/trait"]
        self.assertEqual(None, trait.get("units"))

    def test_date_unit(self):
        """
        Passing a date_unit value to the constructor must result in the expected
        XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model, date_unit="day")
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        elements = BEAST2XML.find_elements(tree)

        trait = elements["./run/state/tree/trait"]
        self.assertEqual("day", trait.get("units"))

    def test_dont_mimic_beauti(self):
        """
        If mimic_beauti is not passed to toString the BEAUti attributes must
        not appear in the <beast> tag in the XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        root = tree.getroot()
        self.assertEqual(None, root.get("beautitemplate"))
        self.assertEqual(None, root.get("beautistatus"))

    def test_mimic_beauti(self):
        """
        Passing mimic_beauti=True to toString must result in the expected
        BEAUti attributes in the <beast> tag in the XML.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string(mimic_beauti=True)))
        root = tree.getroot()
        self.assertEqual("Standard", root.get("beautitemplate"))
        self.assertEqual("", root.get("beautistatus"))


class TestRandomLocalClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'random-local' clock model is used.
    """

    clock_model = "random-local"

    def test_expected_template(self):
        """
        Passing a 'random-local' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldMean.c:alignment"]'
        )
        self.assertTrue(logger is not None)
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldStdev.c:alignment"]'
        )
        self.assertTrue(logger is not None)


class TestRelaxedExponentialClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'relaxed-exponential' clock model is used.
    """

    clock_model = "relaxed-exponential"

    def test_expec(self):
        """
        Passing a 'relaxed-exponential' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucedMean.c:alignment"]'
        )
        self.assertTrue(logger is not None)


class TestRelaxedLognormalClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'relaxed-lognormal' clock model is used.
    """

    clock_model = "relaxed-lognormal"

    def test_expected_template(self):
        """
        Passing a 'relaxed-lognormal' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldMean.c:alignment"]'
        )
        self.assertTrue(logger is not None)
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="ucldStdev.c:alignment"]'
        )
        self.assertTrue(logger is not None)


class TestStrictClockModel(TestCase, ClockModelMixin):
    """
    Test when a 'strict' clock model is used.
    """

    clock_model = "strict"

    def test_expected_template(self):
        """
        Passing a 'strict' clock model must result in the expected
        XML template being loaded.
        """
        xml = BEAST2XML(clock_model=self.clock_model)
        tree = ET.ElementTree(ET.fromstring(xml.to_string()))
        root = tree.getroot()
        logger = root.find(
            './run/logger[@id="tracelog"]/log[@idref="clockRate.c:alignment"]'
        )
        self.assertTrue(logger is not None)
