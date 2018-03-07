from __future__ import print_function, division

import io
import re
import xml.etree.ElementTree as ET
from dark.reads import Reads

DEFAULT_TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<beast namespace="beast.core:beast.evolution.alignment:beast.evolution.tree.coalescent:beast.core.util:beast.evolution.nuc:beast.evolution.operators:beast.evolution.sitemodel:beast.evolution.substitutionmodel:beast.evolution.likelihood" required="" version="2.4">

<data id="alignment" name="alignment">
</data>

<map name="Uniform">beast.math.distributions.Uniform</map>
<map name="Exponential">beast.math.distributions.Exponential</map>
<map name="LogNormal">beast.math.distributions.LogNormalDistributionModel</map>
<map name="Normal">beast.math.distributions.Normal</map>
<map name="Beta">beast.math.distributions.Beta</map>
<map name="Gamma">beast.math.distributions.Gamma</map>
<map name="LaplaceDistribution">beast.math.distributions.LaplaceDistribution</map>
<map name="prior">beast.math.distributions.Prior</map>
<map name="InverseGamma">beast.math.distributions.InverseGamma</map>
<map name="OneOnX">beast.math.distributions.OneOnX</map>

<run id="mcmc" spec="MCMC" chainLength="20000000">
    <state id="state" storeEvery="5000">
        <tree id="Tree.t:alignment" name="stateNode">
            <trait id="dateTrait.t:alignment" spec="beast.evolution.tree.TraitSet" traitname="date-backward">
              <taxa id="TaxonSet.alignment" spec="TaxonSet">
                    <alignment idref="alignment"/>
              </taxa>
            </trait>
            <taxonset idref="TaxonSet.alignment"/>
        </tree>
        <parameter id="clockRate.c:alignment" lower="1.0E-9" name="stateNode" upper="0.001">1.0E-4</parameter>
        <parameter id="rateAG.s:alignment" lower="0.0" name="stateNode">1.0</parameter>
        <parameter id="rateCG.s:alignment" lower="0.0" name="stateNode">1.0</parameter>
        <parameter id="rateGT.s:alignment" lower="0.0" name="stateNode">1.0</parameter>
        <parameter id="popSize.t:alignment" lower="-1.0E100" name="stateNode" upper="1.0E100">0.3</parameter>
        <parameter id="proportionInvariant.s:alignment" lower="0.0" name="stateNode" upper="1.0">0.3</parameter>
        <parameter id="gammaShape.s:alignment" name="stateNode">1.0</parameter>
        <parameter id="freqParameter.s:alignment" dimension="4" lower="0.0" name="stateNode" upper="1.0">0.25</parameter>
    </state>

    <init id="RandomTree.t:alignment" spec="beast.evolution.tree.RandomTree" estimate="false" initial="@Tree.t:alignment" taxa="@alignment">
        <populationModel id="ConstantPopulation0.t:alignment" spec="ConstantPopulation">
            <parameter id="randomPopSize.t:alignment" name="popSize">1.0</parameter>
        </populationModel>
    </init>

    <distribution id="posterior" spec="util.CompoundDistribution">
        <distribution id="prior" spec="util.CompoundDistribution">
            <distribution id="CoalescentConstant.t:alignment" spec="Coalescent">
                <populationModel id="ConstantPopulation.t:alignment" spec="ConstantPopulation" popSize="@popSize.t:alignment"/>
                <treeIntervals id="TreeIntervals.t:alignment" spec="TreeIntervals" tree="@Tree.t:alignment"/>
            </distribution>
            <prior id="ClockPrior.c:alignment" name="distribution" x="@clockRate.c:alignment">
                <Uniform id="Uniform.0" lower="1.0E-9" name="distr" upper="0.001"/>
            </prior>
            <prior id="GammaShapePrior.s:alignment" name="distribution" x="@gammaShape.s:alignment">
                <Exponential id="Exponential.0" name="distr">
                    <parameter id="RealParameter.0" lower="0.0" name="mean" upper="0.0">1.0</parameter>
                </Exponential>
            </prior>
            <prior id="PopSizePrior.t:alignment" name="distribution" x="@popSize.t:alignment">
                <OneOnX id="OneOnX.1" name="distr"/>
            </prior>
            <prior id="PropInvariantPrior.s:alignment" name="distribution" x="@proportionInvariant.s:alignment">
                <Uniform id="Uniform.2" name="distr"/>
            </prior>
            <prior id="RateAGPrior.s:alignment" name="distribution" x="@rateAG.s:alignment">
                <Gamma id="Gamma.1" name="distr">
                    <parameter id="RealParameter.3" estimate="false" name="alpha">0.05</parameter>
                    <parameter id="RealParameter.4" estimate="false" name="beta">20.0</parameter>
                </Gamma>
            </prior>
            <prior id="RateCGPrior.s:alignment" name="distribution" x="@rateCG.s:alignment">
                <Gamma id="Gamma.3" name="distr">
                    <parameter id="RealParameter.7" estimate="false" name="alpha">0.05</parameter>
                    <parameter id="RealParameter.8" estimate="false" name="beta">10.0</parameter>
                </Gamma>
            </prior>
            <prior id="RateGTPrior.s:alignment" name="distribution" x="@rateGT.s:alignment">
                <Gamma id="Gamma.5" name="distr">
                    <parameter id="RealParameter.11" estimate="false" name="alpha">0.05</parameter>
                    <parameter id="RealParameter.12" estimate="false" name="beta">10.0</parameter>
                </Gamma>
            </prior>
        </distribution>
        <distribution id="likelihood" spec="util.CompoundDistribution" useThreads="true">
            <distribution id="treeLikelihood.alignment" spec="ThreadedTreeLikelihood" data="@alignment" tree="@Tree.t:alignment">
                <siteModel id="SiteModel.s:alignment" spec="SiteModel" gammaCategoryCount="4" proportionInvariant="@proportionInvariant.s:alignment" shape="@gammaShape.s:alignment">
                    <parameter id="mutationRate.s:alignment" estimate="false" name="mutationRate">1.0</parameter>
                    <substModel id="gtr.s:alignment" spec="GTR" rateAC="@rateCG.s:alignment" rateAG="@rateAG.s:alignment" rateAT="@rateGT.s:alignment" rateCG="@rateCG.s:alignment" rateGT="@rateGT.s:alignment">
                        <parameter id="rateCT.s:alignment" estimate="false" lower="0.0" name="rateCT">1.0</parameter>
                        <frequencies id="estimatedFreqs.s:alignment" spec="Frequencies" frequencies="@freqParameter.s:alignment"/>
                    </substModel>
                </siteModel>
                <branchRateModel id="StrictClock.c:alignment" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockRate.c:alignment"/>
            </distribution>
        </distribution>
    </distribution>

    <operator id="StrictClockRateScaler.c:alignment" spec="ScaleOperator" parameter="@clockRate.c:alignment" scaleFactor="0.75" weight="3.0"/>

    <operator id="strictClockUpDownOperator.c:alignment" spec="UpDownOperator" scaleFactor="0.75" weight="3.0">
        <up idref="clockRate.c:alignment"/>
        <down idref="Tree.t:alignment"/>
    </operator>

    <operator id="RateAGScaler.s:alignment" spec="ScaleOperator" parameter="@rateAG.s:alignment" scaleFactor="0.5" weight="0.1"/>
    <operator id="RateCGScaler.s:alignment" spec="ScaleOperator" parameter="@rateCG.s:alignment" scaleFactor="0.5" weight="0.1"/>
    <operator id="RateGTScaler.s:alignment" spec="ScaleOperator" parameter="@rateGT.s:alignment" scaleFactor="0.5" weight="0.1"/>
    <operator id="CoalescentConstantTreeScaler.t:alignment" spec="ScaleOperator" scaleFactor="0.5" tree="@Tree.t:alignment" weight="3.0"/>
    <operator id="CoalescentConstantTreeRootScaler.t:alignment" spec="ScaleOperator" rootOnly="true" scaleFactor="0.5" tree="@Tree.t:alignment" weight="3.0"/>
    <operator id="CoalescentConstantUniformOperator.t:alignment" spec="Uniform" tree="@Tree.t:alignment" weight="30.0"/>
    <operator id="CoalescentConstantSubtreeSlide.t:alignment" spec="SubtreeSlide" tree="@Tree.t:alignment" weight="15.0"/>
    <operator id="CoalescentConstantNarrow.t:alignment" spec="Exchange" tree="@Tree.t:alignment" weight="15.0"/>
    <operator id="CoalescentConstantWide.t:alignment" spec="Exchange" isNarrow="false" tree="@Tree.t:alignment" weight="3.0"/>
    <operator id="CoalescentConstantWilsonBalding.t:alignment" spec="WilsonBalding" tree="@Tree.t:alignment" weight="3.0"/>
    <operator id="PopSizeScaler.t:alignment" spec="ScaleOperator" parameter="@popSize.t:alignment" scaleFactor="0.75" weight="3.0"/>
    <operator id="proportionInvariantScaler.s:alignment" spec="ScaleOperator" parameter="@proportionInvariant.s:alignment" scaleFactor="0.5" weight="0.1"/>
    <operator id="gammaShapeScaler.s:alignment" spec="ScaleOperator" parameter="@gammaShape.s:alignment" scaleFactor="0.5" weight="0.1"/>
    <operator id="FrequenciesExchanger.s:alignment" spec="DeltaExchangeOperator" delta="0.01" weight="0.1">
        <parameter idref="freqParameter.s:alignment"/>
    </operator>

    <logger id="tracelog" fileName="strict-const.log" logEvery="2000" model="@posterior" sanitiseHeaders="true" sort="smart">
        <log idref="posterior"/>
        <log idref="likelihood"/>
        <log idref="prior"/>
        <log idref="treeLikelihood.alignment"/>
        <log id="TreeHeight.t:alignment" spec="beast.evolution.tree.TreeHeightLogger" tree="@Tree.t:alignment"/>
        <log idref="clockRate.c:alignment"/>
        <log idref="rateAG.s:alignment"/>
        <log idref="rateCG.s:alignment"/>
        <log idref="rateGT.s:alignment"/>
        <log idref="popSize.t:alignment"/>
        <log idref="CoalescentConstant.t:alignment"/>
        <log idref="proportionInvariant.s:alignment"/>
        <log idref="gammaShape.s:alignment"/>
        <log idref="freqParameter.s:alignment"/>
    </logger>

    <logger id="screenlog" logEvery="5000">
        <log idref="posterior"/>
        <log id="ESS.0" spec="util.ESS" arg="@posterior"/>
        <log idref="likelihood"/>
        <log idref="prior"/>
    </logger>

    <logger id="treelog.t:alignment" fileName="strict-const.trees" logEvery="2000" mode="tree">
        <log id="TreeWithMetaDataLogger.t:alignment" spec="beast.evolution.tree.TreeWithMetaDataLogger" tree="@Tree.t:alignment"/>
    </logger>

</run>
</beast>
"""


class BEAST2XML(object):
    """
    Create BEAST2 XML.

    @param template: An C{str} filename or an open file pointer to read the
        XML template from. If C{None} a default strict clock constant
        population size template will be used.
    @param sequenceIdDateRegex: If not C{None}, gives a C{str} regular
        expression that will be used to capture sequence dates from their ids.
        The regular expression must have a single (...) capture region.
    @param sequenceIdDateRegexMayNotMatch: If C{True} it should not be
        considered an error if a sequence id does not match the regular
        expression given by C{sequenceIdDateRegex}.
    """

    TRACELOG_SUFFIX = '.log'
    TREELOG_SUFFIX = '.trees'

    def __init__(self, template=None, sequenceIdDateRegex=None,
                 sequenceIdDateRegexMayNotMatch=False):
        if template is not None:
            self._tree = ET.parse(template)
        else:
            self._tree = ET.ElementTree(ET.fromstring(DEFAULT_TEMPLATE))
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

        stream = io.StringIO()
        tree.write(stream, 'unicode', xml_declaration=True)
        return stream.getvalue()
