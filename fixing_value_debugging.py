#%% md
# <span style="color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;">An Exception was encountered at '<a href="#papermill-error-cell">In [4]</a>'.</span>
#%% md
# # Phase 3: Setting up the BEAST xmls
# 
# <details>
#     <summary>Click To See A Decription of Parameters</summary>
#         <pre>
#             <code>
# save_dir: str  
#     Path to directory for saving outputs in.
# 
# cache_dir: str 
#     Path to directory for cached objects in.
# 
# template_xml_path: str
#     Path to template BEAST xml.
# 
# use_initial_tree:  bool, default True
#     Is there an inital tree to be used. If not the initial tree will not be used in generating a BEAST 2 xml
#     and will BEAST 2 generate its own.
# 
# rt_dims: int, optional
#     Number of Rt dimensions (time periods over which Rt is estimated).
# 
# rt_change_dates: : list, tuple, pd.Series or pd.DatetimeIndex of datetimes
#     Internal partitions of Rt estimation periods.
# 
# sampling_prop_dims: int, optional
#     Number of sampling proportion dimensions (time periods over which sampling proportion is estimated).
# 
# sampling_prop_change_dates: : list, tuple, pd.Series or pd.DatetimeIndex of dates
#     Internal partitions of sampling proportion estimation periods.
# 
# metadata_path: str
#        Path to csv or tsv containing metadata.
# 
# collection_date_field: str, default='date'
#     Name of field in metadata_db containing collection dates of sequences. Should be format YYYY-MM-DD.
# 
# sample_id_field: str, default 'strain'
#     Name of field in metadata_db containing ids corresponding to those used in fasta_path.
# 
# initial_tree_path: str
#     Path to initial_tree. Should .nwk file.
# 
# fasta_path: str
#     Path to fasta file containing sequences.
# 
# origin_start_addition float
#     This + initial temporal tree height is used as starting value of origin.
#     We recommend using an estimate of infection period for the pathogen being studied. **Value should be in years.**
#     Origin prio will be unform:
#         Lower value: time in years from oldest to youngest sequence in fasta_path
#         Start value: origin_start_addition + initial temporal tree height
#         Upper value:  initial temporal tree height + origin_upper_addition.
# 
# origin_upper_addition: float/int
#     This + initial temporal tree height is used as upper value of origin prior. **Value should be in years.**
#     Origin prio will be unform:
#         Lower value: time in years from oldest to youngest sequence in fasta_path
#         Start value: origin_start_addition + initial temporal tree height
#         Upper value:  initial temporal tree height + origin_upper_addition.
# 
# origin_prior: dict {'lower': float, 'upper': float, 'start': float}, optional
#        Details of the origin prior. assumed to be uniformly distributed.
# 
# log_file_basename: str, optional
#     If provided .tree, .log and .state files from running BEAST 2 will have this name prefixed by 'run-with-seed-{seed}-',
#     number being that of the chain.
# 
# chain_length: int
#     Number of chains to use for BEAST runs.
# 
# trace_log_every: int
#     How often to save a log file during BEAST runs.
# 
# tree_log_every: int
#     How often to save a tree file during BEAST runs.
# 
# screen_log_every: int
#     How often to output to screen during BEAST runs.
# 
# store_state_every: int 
#     How often to store MCMC state during BEAST runs.
#   </code>
# </pre>
# 
#%%
save_dir = None
template_xml_path = None
fasta_path = None
use_initial_tree = True
initial_tree_path = None
metadata_path = None
rt_dims = None
rt_change_dates = None
sampling_prop_dims=None
sampling_prop_change_dates=None
collection_date_field = 'date'
sample_id_field='strain'
origin_upper_addition = None
origin_prior = None
origin_start_addition = None
log_file_basename=None
chain_length = None
trace_log_every = None
tree_log_every = None
screen_log_every = None
store_state_every = None
#%%
# Parameters
chain_length = 500000
collection_date_field = "sample collection date"
log_file_basename = "BDSKY_serial"
origin_prior = None
origin_start_addition = 0.02737850787132101
origin_upper_addition = 2
rt_dims = None
sample_id_field = "specimen collector sample ID"
sampling_prop_dims = None
screen_log_every = 2500
store_state_every = 500
template_xml_path = "BDSKY_serial_COVID-19_template.xml"
trace_log_every = 500
tree_log_every = 500
use_initial_tree = True
save_dir = "Local-Test-BDSKY-Rt_change_times/2025-11-10_13-28-02"
cache_dir = "Local-Test-BDSKY-Rt_change_times/2025-11-10_13-28-02/cache"
rt_change_dates = ["2023-11-23", "2023-12-04"]
sampling_prop_change_dates = ["2023-11-23", "2023-12-04"]
fasta_path = "Local-Test-BDSKY-Rt_change_times/2025-11-10_13-28-02/down_sampled_sequences.fasta"
metadata_path = "Local-Test-BDSKY-Rt_change_times/2025-11-10_13-28-02/down_sampled_metadata.csv"
initial_tree_path = "Local-Test-BDSKY-Rt_change_times/2025-11-10_13-28-02/initial_trees/down_sampled_time.nwk"

#%% md
# Import packages. 
#%%
from dark.fasta import FastaReads
from beast2xml.beast2 import BEAST2XML
import ete3
import pandas as pd
from beast2xml.date_utilities import date_to_decimal
import warnings
#%% md
# ## Generating the BEAST2 xmls.
#%% md
# <span id="papermill-error-cell" style="color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;">Execution using papermill encountered an exception here and stopped:</span>
#%%
def two_df_cols_to_dict(df, key, value):
    return df[[key, value]].set_index(key).to_dict()[value]

def gen_bdsky_serial_xml(template_path,
                         sequences_path,
                         metadata_path,
                         output_path,
                         collection_date_field='date',
                         sample_id_field='strain',
                         initial_tree_path=None,
                         origin_upper_height_addition=None,
                         origin_start_addition=None,
                         origin_prior=None,
                         rt_dims=None,
                         rt_change_dates=None,
                         sampling_prop_dims=None,
                         sampling_prop_change_dates=None,
                         no_sampling_first_period=True,
                         log_file_basename=None,
                         chain_length=None,
                         trace_log_every=None,
                         tree_log_every=None,
                         screen_log_every=None,
                         store_state_every=None):
    """
    Generate a BDSKY xml with initial tree inserted.

    Parameters
    ----------
    template_path: str
        Path to template_xml_path.
    sequences_path: str
        Path to sequences must be fasta_path.
    metadata_path: str
        Path to metadata_update must be csv.
    output_path: str
        Path to save output xml to.
    sample_id_field: str, default 'strain'
        Field used to identify samples.
    collection_date_field: str, default 'date'
        Field to use as sequence collection date.
    initial_tree_path: str, optional
        Path to initial_tree    must be Newick file (nwk).
    origin_upper_height_addition: int or float, optional
        Value to add to tree height for upper limit of origin prior. Origin prior is
         uniformly distributed.
    origin_start_addition: int or float, optional
        Value to add to tree height for starting value. . Origin prior is uniformly
         distributed.
    origin_prior: dict {'lower': float, 'upper': float, 'start': float}, optional
        Details of the origin prior assumed to be uniformly distributed.
    rt_dims: int, optional
        Number of Rt dimensions (time periods).
    rt_change_dates: : list, tuple, pd.Series or pd.DatetimeIndex of datetimes
        Internal partitions of Rt estimation periods.
    sampling_prop_dims: int, optional
        Number of sampling proportion dimensions (time periods).
    sampling_prop_change_dates: : list, tuple, pd.Series or pd.DatetimeIndex of dates
        Internal partitions of sampling proportion estimation periods.
    log_file_basename: str, optional
            The base filename to write logs to. A .log or .trees suffix will be appended
            to this to make the actual log file names.  If None, the log file names in
            the template will be retained.
    chain_length : int, optional
        The length of the MCMC chain. If C{None}, the value in the template will
         be retained.
    trace_log_every: int, optional
        Specifying how often to write to the trace log file. If None, the value in the
        template will be retained.
    tree_log_every: int, optional
        Specifying how often to write to the file_path log file. If None, the value in the
        template will be retained.
    screen_log_every: int, optional
        Specifying how often to write to the terminal (screen) log. If None, the
        value in the template will be retained.
    store_state_every : int, optional
        Specifying how often to write MCMC state file. If None, the
        value in the template will be retained.

    """
    if metadata_path.endswith('.tsv'):
        delimiter = '\t'
    elif metadata_path.endswith('.csv'):
        delimiter = ','
    else:
        raise TypeError(
            f"metadata_path must be a csv or tsv file, ending with the appropriate file extension. Value given is {metadata_path}")
    metadata_df = pd.read_csv(metadata_path, parse_dates=[collection_date_field], sep=delimiter)
    metadata_df['year_decimal'] = metadata_df[collection_date_field].map(date_to_decimal)
    if origin_prior is None:
        if origin_upper_height_addition is not None and  origin_start_addition is not None:
            if initial_tree_path is None:
                raise ValueError('If parameterising the origin prior via ' +
                                 'origin_upper_height_addition and origin_start_addition an ' +
                                 'initial tree must be provided.')
            tree = ete3.Tree(initial_tree_path, format=1)
            furthest_leaf, tree_height = tree.get_farthest_leaf()
            youngest_tip = metadata_df.year_decimal.max()
            oldest_tip = metadata_df.year_decimal.min()
            tip_distance = youngest_tip - oldest_tip
            if tip_distance > tree_height:
                raise ValueError('tree_height must be greater than distance between youngest_tip_date and oldest_tip.')
            origin_prior = {
                'lower': tip_distance,
                'upper': tree_height + origin_upper_height_addition,
                'start': tree_height + origin_start_addition}
    else:
        warnings.warn("If using your own origin prior there is a chance" +
                      " that an origin value will be less than the tree " +
                      " height when BEAST 2 is running." +
                      " If this happens BEAST 2 will crash.\n"+
                      "We recommend using one generated by supplying:\n" +
                      "* An initial temporal tree. \n" +
                      "* origin_upper_height_addition \n" +
                      "* origin_start_addition")
    beast2xml = BEAST2XML(template=template_path)
    seqs = FastaReads([sequences_path])
    beast2xml.add_sequences(seqs)
    age_dict = two_df_cols_to_dict(metadata_df, sample_id_field, 'year_decimal')
    beast2xml.add_ages(age_dict)
    if origin_prior is not None:
        # Change Origin starting value, lower and upper limit on state node
        beast2xml.change_parameter_state_node("origin", value=origin_prior["start"])
        del origin_prior["start"]
        beast2xml.change_prior("origin", "uniform", **origin_prior)
    else:
        warnings.warn("If using the Origin prior in the template xml there is a chance" +
                      " that an origin value will be less than the tree " +
                      " height when BEAST 2 is running.." +
                      " If this happens BEAST 2 will crash.\n"+
                      "We recommend using one generated by supplying:\n" +
                      "* An initial temporal tree. \n" +
                      "* origin_upper_height_addition \n" +
                      "* origin_start_addition")
    if rt_change_dates is not None:
        if rt_dims is not None:
            raise AssertionError("Either rt_dims or rt_change_dates can be given but not both.")
        beast2xml.add_rate_change_dates(
            parameter="birthRateChangeTimes",
            dates=rt_change_dates)
    if rt_dims is not None:
        beast2xml.change_parameter_state_node(parameter='reproductiveNumber',
                                              dimension=rt_dims)
    if sampling_prop_change_dates is not None:
        if sampling_prop_dims is not None:
            raise AssertionError("Either sampling_prop_dims or sampling_prop_change_dates can be given but not both.")
        beast2xml.add_rate_change_dates(
            parameter="samplingRateChangeTimes",
            dates=sampling_prop_change_dates)
        if no_sampling_first_period:
            #beast2xml.fix_dimension_values(parameter='samplingProportion')
            beast2xml.fix_first_few_dimension_values(parameter='samplingProportion')
    if sampling_prop_dims is not None:
        beast2xml.change_parameter_state_node(parameter='samplingProportion',
                                              dimension=sampling_prop_dims)
    if initial_tree_path is not None:
        beast2xml.add_initial_tree(initial_tree_path)
    beast2xml.to_xml(
        output_path,
        chain_length=chain_length,
        log_file_basename=log_file_basename,
        trace_log_every=trace_log_every,
        tree_log_every=tree_log_every,
        screen_log_every=screen_log_every,
        store_state_every=store_state_every,
    )


gen_bdsky_serial_xml(
    template_path=template_xml_path,
    sequences_path=fasta_path,
    metadata_path=metadata_path,
    initial_tree_path=initial_tree_path,
    origin_prior=origin_prior,
    collection_date_field=collection_date_field,
    sample_id_field=sample_id_field,
    origin_upper_height_addition=origin_upper_addition,
    origin_start_addition=origin_start_addition,
    output_path="output_xmls/Slice_method.xml",
    rt_dims=rt_dims,
    rt_change_dates=rt_change_dates,
    sampling_prop_dims=sampling_prop_dims,
    sampling_prop_change_dates=sampling_prop_change_dates,
    log_file_basename=log_file_basename,
    chain_length=chain_length,
    trace_log_every=trace_log_every,
    tree_log_every=tree_log_every,
    screen_log_every=screen_log_every,
    store_state_every=store_state_every
)