from __future__ import print_function, division

import re
import six
from datetime import date
from beast2xml.date_utilities import date_to_decimal
import xml.etree.ElementTree as ET
import xml
import ete3

import warnings

from importlib.resources import files

from dark.reads import Reads
import pandas as pd
from copy import deepcopy


def delete_child_nodes(node):
    """
    Delete any existing children of xml node.

    Parameters
    ----------
    node: xml.etree.ElementTree.Element

    """
    # Delete any existing children of xml node.
    for child in list(node):
        node.remove(child)


class BEAST2XML(object):
    """
    Create BEAST2 XML instance.

    Parameters
    ----------
    template: str, default=None
        A filename or an open file pointer to read the
        XML template from. If C{None}, a template based on C{clockModel}
        will be used.
    clock_model: str, default="strict"
        Clock model to be used. Possible values
        are 'random-local', 'relaxed-exponential', 'relaxed-lognormal',
        and 'strict.
    sequence_id_date_regex: str, default=None
        If not C{None}, gives a C{str} regular
        expression that will be used to capture sequence dates from their ids.
        See the explanation in ../bin/beast2-xml.py
    sequence_id_age_regex: str, default=None
        If not C{None}, gives a C{str} regular
        expression that will be used to capture sequence ages from their ids.
        See the explanation in ../bin/beast2-xml.py
    sequence_id_regex_must_match: bool, default=True
        If C{True} it will be considered an error
        if a sequence id does not match the regular expression given by
        C{sequenceIdDateRegex} or C{sequenceId_age_regex}.
    date_unit: str, default="year"
        A C{str}, either 'day', 'month', or 'year' indicating the
        date time unit.

    """

    TRACELOG_SUFFIX = ".log"
    TREELOG_SUFFIX = ".trees"
    _rate_change_to_param_dict = {
        "birthRateChangeTimes": "reproductiveNumber",
        "deathRateChangeTimes": "becomeUninfectiousRate",
        "samplingRateChangeTimes": "samplingProportion",
    }
    _distribution_args = {
        "Uniform": ["lower", "upper", "offset"],
        "LogNormal": ["meanInRealSpace", "M", "S", "offset"],
        "Beta": ["alpha", "beta", "offset"],
        "Gamma": ["alpha", "beta", "offset"],
        "InverseGamma": ["alpha", "beta", "offset"],
        "LaplaceDistribution": ["mu", "scale", "offset"],
        "Exponential": ["mean", "offset"],
        "Normal": ["mean", "sigma", "offset"],
        "WeibullDistribution": ["shape", "scale", "meanOne", "offset"],
        "Poisson": ["lambda", "offset"],
    }

    def __init__(
        self,
        template=None,
        clock_model="strict",
        sequence_id_date_regex=None,
        sequence_id_age_regex=None,
        sequence_id_regex_must_match=True,
        date_unit="year",
    ):
        if template is None:
            self._tree = ET.parse(
                files("beast2xml").joinpath(f"templates/{clock_model}.xml")
            )
        else:
            self._tree = ET.parse(template)
        if sequence_id_date_regex is None:
            self._sequence_id_date_regex = None
        else:
            self._sequence_id_date_regex = re.compile(sequence_id_date_regex)

        if sequence_id_age_regex is None:
            self._sequence_id_age_regex = None
        else:
            self._sequence_id_age_regex = re.compile(sequence_id_age_regex)

        self._sequence_id_regex_must_match = sequence_id_regex_must_match
        self._sequences = Reads()
        self._age_by_full_id = {}
        self._age_by_short_id = {}
        self._date_unit = date_unit
        self._initial_phylo_tree = None

    @staticmethod
    def find_elements(tree):
        """
        Check that an XML file_path has the required structure and return the found
        elements.

        Parameters
        ----------
        file_path : xml.etree.ElementTree.Element


        Returns
        -------
        result: dict {str:xml.etree.ElementTree.Element}
            A dictionary where the keys are the element_path names and the values
            are the corresponding elements.

        """
        result = {}
        root = tree.getroot()
        for tag in (
            "data",
            "run",
            "./run/state/tree/trait",
            "./run/logger[@id='tracelog']",
            "./run/logger[@id='treelog.t:",
            "./run/logger[@id='screenlog']",
        ):
            if tag == "./run/logger[@id='treelog.t:":
                tag = tag + data_id + "']"
            element = root.find(tag)
            if element is None:
                raise ValueError("Could not find %r tag in XML template" % tag)
            if tag == "data":
                data_id = element.get("id")
            result[tag] = element

        return result

    def add_ages(self, age_data, seperator="\t", age_column="year_decimal"):
        """
        Add age data.

        Parameters
        ----------
        age_data: str
            Path to seperated value file.
        seperator: str
            Seperator to use to separate age data.
        age_column: str, default = 'year_decimal'
           Column name to use for age data.

        """
        if isinstance(age_data, str):
            age_data = pd.read_csv(age_data, sep=seperator)
        if isinstance(age_data, pd.DataFrame):
            if "id" in age_data.columns:
                age_data = age_data.set_index("id")
            elif "strain" in age_data.columns:
                age_data = age_data.set_index("strain")
            else:
                raise ValueError("An age_data column must be id or strain")
            age_data = age_data[age_column]
        if isinstance(age_data, pd.Series):
            age_data = age_data.to_dict()
        if not isinstance(age_data, dict):
            raise ValueError(
                "age_data must be a C{dict} a C{pd.DataFrame}, a C{pd.Series} or a path to tsv/csv."
            )
        self._age_by_full_id.update(age_data)
        age_data = {key.split()[0]: value for key, value in age_data.items()}
        self._age_by_short_id.update(age_data)

    def add_age(self, sequence_id, age):
        """
        Specify the age of a sequence.

        Parameters
        ----------
        sequence_id : str
            The name of a sequence id. An age will be
            recorded for both the full id and for the part of it up to its
            first space. This makes it convenient for giving sequence ids from
            the command line (e.g., using ../bin/beast2-xml.py) without having
            to specify the full id. On id lookup (when creating XML), full ids
            always have precedence so there is no danger of short id
            duplication error if full ids are always used.
        age : float or int
        The age of a sequence.
        """
        self._age_by_short_id[sequence_id.split()[0]] = age
        self._age_by_full_id[sequence_id] = age

    def add_sequence(self, sequence, age=None):
        """

        Parameters
        ----------
        sequence : dark.read
            Sequence to be added.
        age : float, default=None
            If not C{None}, the C{float} age of the sequence.

        Returns
        -------

        """
        self._sequences.add(sequence)

        if age is not None:
            self.add_age(sequence.id, age)
            return

        age = None

        if self._sequence_id_date_regex is not None:
            match = self._sequence_id_date_regex.match(sequence.id)
            if match:
                try:
                    sequence_date = date(
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
                    days = (date.today() - sequence_date).days
                    if self._date_unit == "year":
                        age = days / 365.25
                    elif self._date_unit == "month":
                        age = days / (365.25 / 12)
                    else:
                        assert self._date_unit == "day"
                        age = days

        if age is None and self._sequence_id_age_regex is not None:
            match = self._sequence_id_age_regex.match(sequence.id)
            if match:
                try:
                    age = match.group(1)
                except IndexError:
                    pass

        if age is None:
            if self._sequence_id_regex_must_match and (
                self._sequence_id_date_regex or self._sequence_id_age_regex
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

        Parameters
        ----------
        sequences : iterable of dark.read instances
            The sequences to be added.

        """
        for sequence in sequences:
            self.add_sequence(sequence)

    def _to_xml_tree(
        self,
        chain_length=None,
        default_age=0.0,
        date_direction=None,
        log_file_basename=None,
        trace_log_every=None,
        tree_log_every=None,
        screen_log_every=None,
        store_state_every=None,
        transform_func=None,
        mimic_beauti=False,
    ):
        """
        Generate xml.etree.ElementTree for running on BEAST.

        Parameters
        ----------
        chain_length : int, default=None
            The length of the MCMC chain. If C{None}, the value in the template will
             be retained.
        default_age : float or int, default=0.0
            The age to use for sequences that have not
            explicitly been given (see C{add_age}, C{add_ages} C{add_sequence},
             C{add_sequences}).
        date_direction : str, default=None
            A C{str}, either 'backward', 'forward' or "date" indicating whether dates are
             back in time from the present or forward in time from some point in the
              past.
        log_file_basename : str, default=None
            The base filename to write logs to. A .log or .trees suffix will be appended
            to this to make the actual log file names.  If None, the log file names in
            the template will be retained.
        trace_log_every : int, default=None
            Specifying how often to write to the trace log file. If None, the value in the
            template will be retained.
        tree_log_every : int, default=None
            Specifying how often to write to the file_path log file. If None, the value in the
            template will be retained.
        screen_log_every : int, default=None
            Specifying how often to write to the terminal (screen) log. If None, the
            value in the template will be retained.
        store_state_every  : int, default=None
            Specifying how often to write MCMC state file. If None, the
            value in the template will be retained.
        transform_func : callable, default=None
            A callable that will be passed the C{ElementTree} instance and which
            must return an C{ElementTree} instance.
        mimic_beauti : bool, default=False
            If True, add attributes to the <beast> tag in the way that BEAUti does, to
            allow BEAUti to load the XML we produce.

        Returns
        -------
        file_path: xml.etree.ElementTree
            ElementTree for running on BEAST
        """
        if mimic_beauti:
            root = self._tree.getroot()
            root.set("beautitemplate", "Standard")
            root.set("beautistatus", "")

        elements = self.find_elements(self._tree)

        # Get data element_path
        data = elements["data"]
        data_id = data.get("id")
        tree_logger_key = "./run/logger[@id='treelog.t:" + data_id + "']"
        trait = elements["./run/state/tree/trait"]

        # Delete any existing children of the data node.
        delete_child_nodes(data)

        if not isinstance(default_age, (float, int)):
            raise TypeError("The default age must be an integer or float.")

        sequences = self._sequences
        age_by_short_id = deepcopy(self._age_by_short_id)
        if self._initial_phylo_tree is not None:
            tip_set_diffs = self.set_diffs_initial_tree_and_sequences()
            if tip_set_diffs["in initial tree"]:
                raise ValueError(
                    "Initial tree has additional sequences to the ones you have added."
                )
            if tip_set_diffs["in sequences"]:
                warnings.warn(
                    "\n".join(
                        [
                            "One or more you have added sequences are not represented in the initial tree you gave.",
                            "These sequences will not be added to the xml being generated.",
                            "Use method set_diffs_initial_tree_and_sequences to view these.",
                        ]
                    )
                )
                sequences = Reads(
                    [
                        sequence
                        for sequence in self._sequences
                        if sequence.id not in tip_set_diffs["in sequences"]
                    ]
                )
                age_by_short_id = {
                    key: age
                    for key, age in self._age_by_short_id.items()
                    if key not in tip_set_diffs["in sequences"]
                }

            initial_tree_nodes = self._tree.findall("./run/init")
            if len(initial_tree_nodes) == 0:
                raise ValueError("Template has no initial tree.")
            if len(initial_tree_nodes) > 1:
                raise ValueError(
                    "More than one intial tree is in the template xml BEAST2-xml only supports template xmls with one initial tree."
                )
            elements["run"].remove(initial_tree_nodes[0])
            newick_tree = self._initial_phylo_tree.write(
                format=self._initial_phylo_tree_format
            )
            replacement = ET.SubElement(
                elements["run"],
                "init",
                spec="beast.util.TreeParser",
                id="NewickTree.t:" + data_id,
                initial="@Tree.t:" + data_id,
                taxa="@" + data_id,
                IsLabelledNewick="true",
                adjustTipHeights="false",
                newick=newick_tree,
            )

        # Add in all sequences.
        for sequence in sorted(
            sequences
        ):  # Sorting adds the sequences alphabetically like in BEAUti.
            seq_id = sequence.id
            short_id = seq_id.split()[0]
            if seq_id not in age_by_short_id:
                age_by_short_id[short_id] = default_age

            ET.SubElement(
                data,
                "sequence",
                id="seq_" + short_id,
                spec="Sequence",
                taxon=short_id,
                totalcount="4",
                value=sequence.sequence,
            )

        trait_order = [
            sequence.id.split()[0] for sequence in sequences
        ]  # ensures order is the same as BEAUti's.
        trait_text = [
            short_id + "=" + str(age_by_short_id[short_id]) for short_id in trait_order
        ]
        if date_direction is None:
            trait.set(
                "value", ",".join(trait_text)
            )  # Replaces old age info with new age info
            if trait.get("traitname") is None:
                raise ValueError(
                    "No traitname attribute in dateTrait element_path of template xml."
                    + " This can be set through date_direction argument with the options "
                    + '"backward", "forward" or "date".'
                )
        else:
            if date_direction not in ["backward", "forward", "date"]:
                raise ValueError(
                    'If supplied date_direction must be either "backward", "forward" or "date".'
                )
            trait.set("value", "")  # Removes old age info
            trait.text = ",\n".join(trait_text) + "\n"  # Adds new age info
            if date_direction == "date":
                trait.set("traitname", date_direction)
            else:
                trait.set("traitname", "date-" + date_direction)

        # Set the date unit (if not 'year').
        if self._date_unit != "year":
            trait.set("units", self._date_unit)

        if chain_length is not None:
            elements["run"].set("chainLength", str(chain_length))

        if store_state_every is not None:
            elements["run"].set("storeEvery", str(store_state_every))

        if log_file_basename is not None:
            # Trace log.
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set("fileName", log_file_basename + self.TRACELOG_SUFFIX)
            # Tree log.
            logger = elements[tree_logger_key]
            logger.set("fileName", log_file_basename + self.TREELOG_SUFFIX)

        if trace_log_every is not None:
            logger = elements["./run/logger[@id='tracelog']"]
            logger.set("logEvery", str(trace_log_every))

        if tree_log_every is not None:
            logger = elements[tree_logger_key]
            logger.set("logEvery", str(tree_log_every))

        if screen_log_every is not None:
            logger = elements["./run/logger[@id='screenlog']"]
            logger.set("logEvery", str(screen_log_every))

        tree = self._tree if transform_func is None else transform_func(self._tree)
        ET.indent(tree, "\t")
        return tree

    def to_string(
        self,
        chain_length=None,
        default_age=0.0,
        date_direction=None,
        log_file_basename=None,
        trace_log_every=None,
        tree_log_every=None,
        screen_log_every=None,
        store_state_every=None,
        transform_func=None,
        mimic_beauti=False,
    ):
        """Generate str version of xml.etree.ElementTree for running on BEAST.

        Parameters
        ----------
        chain_length: int, default=None
            The length of the MCMC chain. If C{None}, the value in the template will
             be retained.
        default_age: float or int, default=0.0
            The age to use for sequences that have not
            explicitly been given (see C{add_age}, C{add_ages} C{add_sequence},
             C{add_sequences}).
        date_direction: str, default=None
            A C{str}, either 'backward', 'forward' or "date" indicating whether dates are
             back in time from the present or forward in time from some point in the
              past.
        log_file_basename: str, default=None
            The base filename to write logs to. A .log or .trees suffix will be appended
            to this to make the actual log file names.  If None, the log file names in
            the template will be retained
        trace_log_every: int, default=None
            Specifying how often to write to the trace log file. If None, the value in the
            template will be retained.
        tree_log_every: int, default=None
            Specifying how often to write to the file_path log file. If None, the value in the
            template will be retained.
        screen_log_every: int, default=None
            Specifying how often to write to the terminal (screen) log. If None, the
            value in the template will be retained.
        store_state_every: int, default=None
            Specifying how often to write MCMC state file. If None, the
            value in the template will be retained.
        transform_func: callable, default=None
            A callable that will be passed the C{ElementTree} instance and which
            must return an C{ElementTree} instance.
        mimic_beauti: bool, default=False
            If True, add attributes to the <beast> tag in the way that BEAUti does, to
            allow BEAUti to load the XML we produce.

        Returns
        -------
        file_path: str
            String representation of xml.etree.ElementTree for running on BEAST
        """
        tree = self._to_xml_tree(
            chain_length=chain_length,
            default_age=default_age,
            date_direction=date_direction,
            log_file_basename=log_file_basename,
            trace_log_every=trace_log_every,
            tree_log_every=tree_log_every,
            screen_log_every=screen_log_every,
            store_state_every=store_state_every,
            transform_func=transform_func,
            mimic_beauti=mimic_beauti,
        )

        stream = six.StringIO()
        tree.write(stream, "unicode" if six.PY3 else "utf-8", xml_declaration=True)
        return stream.getvalue()

    def to_xml(
        self,
        path,
        chain_length=None,
        default_age=0.0,
        date_direction=None,
        log_file_basename=None,
        trace_log_every=None,
        tree_log_every=None,
        screen_log_every=None,
        store_state_every=None,
        transform_func=None,
        mimic_beauti=False,
    ):
        """
        Generate xml.etree.ElementTree for running on BEAST and write to xml file.

        Parameters
        ----------
        path: str
            Path to write xml file to.
        chain_length : int, default=None
            The length of the MCMC chain. If C{None}, the value in the template will
             be retained.
        default_age: float or int, default=0.0
            The age to use for sequences that have not
            explicitly been given (see C{add_age}, C{add_ages} C{add_sequence},
             C{add_sequences}).
        date_direction: str, default=None
            A C{str}, either 'backward', 'forward' or "date" indicating whether dates are
            back in time from the present or forward in time from some point in the
            past.
        log_file_basename: str, default=None
            The base filename to write logs to. A .log or .trees suffix will be appended
            to this to make the actual log file names.  If None, the log file names in
            the template will be retained.
        trace_log_every: int, default=None
            Specifying how often to write to the trace log file. If None, the value in the
            template will be retained.
        tree_log_every: int, default=None
            Specifying how often to write to the file_path log file. If None, the value in the
            template will be retained.
        screen_log_every: int, default=None
            Specifying how often to write to the terminal (screen) log. If None, the
            value in the template will be retained.
        store_state_every : int, default=None
            Specifying how often to write MCMC state file. If None, the
            value in the template will be retained.
        transform_func: callable, default=None
            A callable that will be passed the C{ElementTree} instance and which
            must return an C{ElementTree} instance.
        mimic_beauti: bool, default=False
            If True, add attributes to the <beast> tag in the way that BEAUti does, to
            allow BEAUti to load the XML we produce.

        Returns
        -------
        None

        """
        if not isinstance(path, str):
            raise TypeError("filename must be a string.")
        tree = self._to_xml_tree(
            chain_length=chain_length,
            default_age=default_age,
            date_direction=date_direction,
            log_file_basename=log_file_basename,
            trace_log_every=trace_log_every,
            tree_log_every=tree_log_every,
            screen_log_every=screen_log_every,
            store_state_every=store_state_every,
            transform_func=transform_func,
            mimic_beauti=mimic_beauti,
        )
        tree.write(path, "unicode" if six.PY3 else "utf-8", xml_declaration=True)

    def _search_for_parameter_in_element(
        self, element_path, parameter, wild_card_ending
    ):
        if wild_card_ending:
            parameter_nodes = [
                potential_parameter_node
                for potential_parameter_node in self._tree.findall(element_path)
                if potential_parameter_node.attrib["id"].startswith(parameter)
            ]
        else:
            parameter_nodes = self._tree.findall(
                "./run/state/parameter[@id='%s']" % parameter
            )
        if len(parameter_nodes) == 0:
            raise ValueError(
                "No parameter with id %s (or starting with) was found." % parameter
            )
        if len(parameter_nodes) > 1:
            raise ValueError(
                "More than one parameter with id %s (or starting with) was found."
                % parameter
            )
        return parameter_nodes[0]

    def change_parameter_state_node(
        self,
        parameter,
        value=None,
        dimension=None,
        lower=None,
        upper=None,
        wild_card_ending=True,
    ):
        """
        Change the values of the stateNode for a parameter.

        Parameters
        ----------
        parameter: str
            The name of the parameter.
        value: int or float
            The value of the parameter.
        dimension:  int
            The dimensions over which a parameter is estimated.
        lower:  int, float or str
            The lower bound of the parameter.
        upper: int, float or str
            The upper bound of the parameter.
        wild_card_ending: bool (default True)
            If true parameter starting with parameter will be searched for.

        """
        if all(arg is None for arg in [value, dimension, lower, upper]):
            raise ValueError(
                "Either a value, dimension, lower or upper argument must be provided."
            )

        parameter_node = self._search_for_parameter_in_element(
            "./run/state/parameter", parameter, wild_card_ending
        )
        if value is not None:
            parameter_node.text = str(value)
        if dimension is not None:
            if not isinstance(dimension, int):
                raise ValueError("Dimension must be an integer.")
            parameter_node.set("dimension", str(dimension))
        if lower is not None:
            parameter_node.set("lower", str(lower))
        if upper is not None:
            parameter_node.set("upper", str(upper))

    def change_prior(self, parameter, distribution, wild_card_ending=True, **kwargs):
        """
        Change the values of a parameters prior.

        Parameters
        ----------
        parameter: str
            The name of the parameter.
        distribution: str
            The name of the distribution.
        wild_card_ending: bool (default True)
            If true parameter starting with parameter will be searched for.
        kwargs: dict
            Keyword arguments parameterising the distribution.

        """
        parameter_node = self._search_for_parameter_in_element(
            "./run/distribution/distribution/prior", parameter, wild_card_ending
        )

        if distribution in [
            "lognorm",
            "lognormal",
            "log norm",
            "log normal",
            "log-norm",
            "log-normal",
        ]:
            distribution = "LogNormal"
        elif distribution in ["inversegamma", "inverse gamma", "inverse-gamma"]:
            distribution = "InverseGamma"
        elif distribution in [
            "LogNormal",
            "InverseGamma",
            "WeibullDistribution",
            "LaplaceDistribution",
        ]:
            pass
        else:
            distribution = distribution.title()

        if distribution in ["Weibull", "Laplace"]:
            distribution = distribution + "Distribution"

        if distribution not in self._distribution_args:
            raise ValueError(
                "Currently only the following distributions are supported: "
                + ", ".join(self._distribution_args.keys())
                + "."
            )

        if distribution == "LogNormal":
            if "meanInRealSpace" not in kwargs:
                kwargs["meanInRealSpace"] = "false"
            elif isinstance(kwargs["meanInRealSpace"], bool):
                kwargs["meanInRealSpace"] = str(kwargs["meanInRealSpace"]).lower()
            else:
                raise TypeError(
                    "Argument meanInRealSpace must be a boolean or"
                    + " not given as argument."
                )

        if distribution == "WeibullDistribution":
            if "meanOne" not in kwargs:
                kwargs["meanOne"] = "false"
            elif isinstance(kwargs["meanOne"], bool):
                kwargs["meanOne"] = str(kwargs["meanOne"]).lower()
            else:
                raise TypeError(
                    "Argument meanOne must be a boolean or" + " not given as argument."
                )

        if "offset" not in kwargs:
            kwargs["offset"] = 0.0

        for key in kwargs:
            if key not in self._distribution_args[distribution]:
                raise ValueError(
                    key
                    + " is not a parameter of the "
                    + distribution
                    + " distribution."
                )
        for arg in self._distribution_args[distribution]:
            if arg not in kwargs.keys():
                raise ValueError("%s has not being given as a kwarg." % arg)

        for keyword, value in kwargs.items():
            if keyword not in ["meanInRealSpace", "meanOne"]:
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        "Argument %s must be an integer or float." % keyword
                    )
        kwargs = {key: str(value) for key, value in kwargs.items()}

        delete_child_nodes(parameter_node)
        i_d = "_".join([parameter, distribution])
        if distribution == "Uniform":
            self.change_parameter_state_node(
                parameter, lower=kwargs["lower"], upper=kwargs["upper"]
            )

        if distribution in ["Poisson", "WeibullDistribution"]:
            ET.SubElement(
                parameter_node,
                "distr",
                id=i_d,
                spec="beast.math.distributions." + distribution,
                **kwargs,
            )
        else:
            ET.SubElement(parameter_node, distribution, id=i_d, name="distr", **kwargs)

    def add_rate_change_dates(self, parameter, dates):
        """
        Add specific dates for parameter changes in skyline models.

        Parameters
        ----------
        parameter : str
            The name of the parameter.
        dates : list, tuple, pd.Series or pd.DatetimeIndex of dates

        """
        if not isinstance(dates, (list, tuple, pd.Series, pd.DatetimeIndex)):
            raise TypeError(
                "dates must be a list, tuple pandas.Series or pandas.DatetimeIndex."
            )
        year_decimals = [date_to_decimal(item) for item in dates]
        youngest_tip = max(self._age_by_short_id.values())
        times = [youngest_tip - year_decimal for year_decimal in year_decimals]
        self.add_rate_change_times(parameter, times)

    def add_rate_change_times(self, parameter, times):
        """
        Add specific times for parameter changes in skyline models.

        Parameters
        ----------
        parameter : str
            The name of the parameter.
        times : iterable of floats
            Times of changes.

        """
        skyline_element = self._tree.find(
            "./run/distribution/distribution/distribution[@spec='beast.evolution.speciation.BirthDeathSkylineModel']"
        )
        if skyline_element is None:
            raise ValueError(
                "No distribution of spec BirthDeathSkylineModel was found."
                + "Currently this method only supports Birth Death Skyline Models."
            )
        rev_time_element = skyline_element.find("reverseTimeArrays")
        if rev_time_element is None:
            rev_time_array = [False, False, False, False, False]
        else:
            rev_time_array = rev_time_element.text
            rev_time_array = rev_time_array.split(" ")
            rev_time_array = [val in ["true", "True", "TRUE"] for val in rev_time_array]
            del rev_time_element  # Delete existing rev_time_element.
        if parameter == "birthRateChangeTimes":
            rev_time_array[0] = True
        elif parameter == "deathRateChangeTimes":
            rev_time_array[1] = True
        elif parameter == "samplingRateChangeTimes":
            rev_time_array[2] = True
        else:
            raise ValueError(
                "Currently this method only supports parameter being: "
                + "birthRateChangeTimes (for changes in reproductive number), "
                "deathRateChangeTimes (for changes in uninfectious rate) and "
                + "samplingRateChangeTimes (for sampling proportion)."
            )
        rev_time_array = [str(val).lower() for val in rev_time_array]
        rev_time_array = " ".join(rev_time_array)
        ET.SubElement(
            skyline_element,
            "reverseTimeArrays",
            spec="beast.core.parameter.BooleanParameter",
            value=rev_time_array,
        )
        parameter_element = skyline_element.find(parameter)
        if parameter_element is not None:
            del parameter_element  # delete old parameter element_path if it exists.
        if not any(time == 0.0 for time in times):
            times.append(0.0)
        dimensions = len(times)
        ET.SubElement(
            skyline_element,
            parameter,
            spec="parameter.RealParameter",
            value=" ".join([str(time) for time in times]),
        )
        self.change_parameter_state_node(
            self._rate_change_to_param_dict[parameter], dimension=dimensions
        )

    def add_initial_tree(self, file_path, format=1):
        """
        Add initial newick tree.

        Parameters
        ----------
        file_path:  str
            Path to the newick tree file.
        format: int, default 1
            Format of the newick tree file:
                0	flexible with support values
                1	flexible with internal node names
                2	all branches + leaf names + internal supports
                3	all branches + all names
                4	leaf branches + leaf names
                5	internal and leaf branches + leaf names
                6	internal branches + leaf names
                7	leaf branches + all names
                8	all names
                9	leaf names
                100	topology only

        Returns
        -------
        None
        """
        self._initial_phylo_tree = ete3.Tree(file_path, format=format)
        self._initial_phylo_tree_format = format

    def set_diffs_initial_tree_and_sequences(self):
        tree_tips = set(self._initial_phylo_tree.get_leaf_names())
        sequence_tips = set([sequence.id for sequence in self._sequences])
        return {
            "in initial tree": tree_tips - sequence_tips,
            "in sequences": sequence_tips - tree_tips,
        }
