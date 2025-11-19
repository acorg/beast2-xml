

#%% md
# Import packages.
#%%
import pandas as pd
from beast2xml.date_utilities import date_to_decimal
from dark.fasta import FastaReads
from beast2xml.beast2 import BEAST2XML
from copy import deepcopy

#%%
# Parameters
chain_length = 500000
collection_date_field = "sample collection date"
sample_id_field = "specimen collector sample ID"
screen_log_every = 2500
store_state_every = 500
template_xml_path = "example_inputs/BDSKY_serial_COVID-19_template.xml"
trace_log_every = 500
tree_log_every = 500
save_dir = "output_xmls"
sampling_prop_change_dates = ["2023-10-09"]


#%% md
# ## Generating the BEAST2 xmls.
#%%
beast2xml_original = BEAST2XML(template=template_xml_path)
#%% Our two methods
methods = [
    "Slice", # function fix_first_few_dimension_values using the Slice class in the xml.
    'ExcludablePrior' # function fix_dimension_values using the ExcludablePrior class in the xml.
]
#%% Setting up the two data sets.
states = ['working', 'not_working'] # I have two states that affect both data source and value
data_uploads = {} # dictionary of beast2xml instances loaded with different data sources.
for state in states:
    beast2xml = deepcopy(beast2xml_original)
    seqs = FastaReads([f'example_inputs/{state}_sequences.fasta'])
    beast2xml.add_sequences(seqs)
    beast2xml.add_dates(date_data=f'example_inputs/{state}_metadata.csv',
                        seperator=',',
                        sample_id_field=sample_id_field,
                        collection_date_field=collection_date_field)

    beast2xml.add_rate_change_dates(
            parameter="samplingRateChangeTimes",
            dates=sampling_prop_change_dates)
    data_uploads[state] = beast2xml


#%% setting up the working and not working values to be fixed at.
# Note wiht the 'not_working' value  BEAST2 still runs but the MCMC process changes the values
values  = {'working': 0, 'not_working': 0.00001}

#%% Finally generating the xmls for this factorial test.
# With both methods the combination of working value bet not working data causes the xml to crash BEAST with -infinity likelihood error.
for method in methods:
    for value_type, value in values.items():
        for data_type, beast2xml in data_uploads.items():
            beast2xml = deepcopy(beast2xml)
            if method == "Slice":
                beast2xml.fix_first_few_dimension_values(parameter='samplingProportion', values = [value])
            if method == "ExcludablePrior":
                beast2xml.fix_dimension_values(parameter='samplingProportion', indexed_and_values = {0: value})
            beast2xml.to_xml(
                f'{save_dir}/{method}_data_{data_type}_value_{value_type}.xml',
                chain_length=chain_length,
                log_file_basename=f'{method}_data_{data_type}_value_{value_type}',
                trace_log_every=trace_log_every,
                tree_log_every=tree_log_every,
                screen_log_every=screen_log_every,
                store_state_every=store_state_every,
            )