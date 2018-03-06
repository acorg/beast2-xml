from __future__ import print_function, division

import xml.etree.ElementTree as ET
from dark.reads import Reads

DEFAULT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<beast namespace="beast.core:beast.evolution.alignment:beast.evolution.tree.coalescent:beast.core.util:beast.evolution.nuc:beast.evolution.operators:beast.evolution.sitemodel:beast.evolution.substitutionmodel:beast.evolution.likelihood" required="" version="2.4">

<data id="alignment" name="alignment">
</data>

<map name="Uniform" >beast.math.distributions.Uniform</map>
<map name="Exponential" >beast.math.distributions.Exponential</map>
<map name="LogNormal" >beast.math.distributions.LogNormalDistributionModel</map>
<map name="Normal" >beast.math.distributions.Normal</map>
<map name="Beta" >beast.math.distributions.Beta</map>
<map name="Gamma" >beast.math.distributions.Gamma</map>
<map name="LaplaceDistribution" >beast.math.distributions.LaplaceDistribution</map>
<map name="prior" >beast.math.distributions.Prior</map>
<map name="InverseGamma" >beast.math.distributions.InverseGamma</map>
<map name="OneOnX" >beast.math.distributions.OneOnX</map>

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
    """

    TRACELOG_SUFFIX = '.log'
    TREELOG_SUFFIX = '.trees'

    def __init__(self, template=None):
        if template is not None:
            self._tree = ET.parse(template)
        else:
            self._tree = ET.ElementTree(ET.fromstring(DEFAULT_TEMPLATE))
        self._sequences = Reads()
        self._ages = {}

    def addAge(self, sequenceId, age):
        """
        Set the age of a sequence.

        @param sequenceId: The C{str} name of a sequence id.
        @param age: The C{float} age of the sequence.
        @raise KeyError: If no sequence with id C{sequenceId} is known.
        """
        # Note that The raising of a KeyError could be relaxed, but that
        # could allow errors to creep in.
        self._ages[sequenceId] = age

    def addSequence(self, sequence, age=None):
        """
        Add a sequence (optionally with an age) to the run.

        @param sequence: A C{dark.read} instance.
        @param age: If not C{None}, the C{float} age of the sequence.
        """
        self._sequences.add(sequence)
        if age is not None:
            self.addAge(sequence.id, age)

    def addSequences(self, sequences):
        """
        Add a set of sequences to the run.

        @param sequences: An iterable of C{dark.read} instances.
        """
        for sequence in sequences:
            self._sequences.add(sequence)

    def toStr(self, chainLength=None, logFileBasename=None,
              traceLogEvery=None, treeLogEvery=None, screenLogEvery=None,
              transformFunc=None):
        """
        @param chainLength: The C{int} length of the MCMC chain. If C{None},
            the value in the template will be retained.
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
        """
        root = self._tree.getroot()
        data = root.find('data')

        if data is None:
            raise ValueError('Could not find <data> tag in XML template')

        # Delete any existing children of the data node.
        for child in data:
            data.remove(child)

        trait = root.find('./run/state/tree/trait')

        if trait is None:
            raise ValueError('Could not find <trait> tag in XML template')

        # Add in all sequences.
        traitText = []
        for sequence in self._sequences:
            traitText.append('%s=%f' %
                             (sequence.id, self._ages.get(sequence.id, 0.0)))
            ET.SubElement(data, 'sequence', id='seq_' + sequence.id,
                          taxon=sequence.id, totalcount='4',
                          value=sequence.sequence)

        trait.text = ',\n'.join(traitText) + '\n'

        if chainLength is not None:
            # This must succeed as the find on run/state/tree/trait succeeded.
            run = root.find('run')
            run.set('chainLength', str(chainLength))

        if logFileBasename is not None:
            # Trace log.
            logger = root.find("./run/logger[@id='tracelog']")

            if logger is None:
                raise ValueError('Could not find <logger id="tracelog"> tag '
                                 'in XML template')

            logger.set('fileName', logFileBasename + self.TRACELOG_SUFFIX)

            # Tree log.
            logger = root.find("./run/logger[@id='treelog.t:alignment']")

            if logger is None:
                raise ValueError(
                    'Could not find <logger id="treelog.t:alignment"> tag '
                    'in XML template')

            logger.set('fileName', logFileBasename + self.TREELOG_SUFFIX)

        if traceLogEvery is not None:
            logger = root.find("./run/logger[@id='tracelog']")

            if logger is None:
                raise ValueError('Could not find <logger id="tracelog"> tag '
                                 'in XML template')

            logger.set('logEvery', str(traceLogEvery))

        if treeLogEvery is not None:
            logger = root.find("./run/logger[@id='treelog.t:alignment']")

            if logger is None:
                raise ValueError(
                    'Could not find <logger id="treelog.t:alignment"> tag '
                    'in XML template')

            logger.set('logEvery', str(treeLogEvery))

        if screenLogEvery is not None:
            logger = root.find("./run/logger[@id='screenlog']")

            if logger is None:
                raise ValueError('Could not find <logger id="screenlog"> tag '
                                 'in XML template')

            logger.set('logEvery', str(screenLogEvery))

        if transformFunc is not None:
            tree = transformFunc(self._tree)

        return ET.tostring(tree.getroot(), encoding='unicode')
