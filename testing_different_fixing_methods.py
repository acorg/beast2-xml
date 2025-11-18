

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
fasta_path = 'example_inputs/sequences.fasta'
metadata_path = 'example_inputs/metadata.csv'


#%% md
# ## Generating the BEAST2 xmls.
#%%
if metadata_path.endswith('.tsv'):
    delimiter = '\t'
elif metadata_path.endswith('.csv'):
    delimiter = ','
else:
    raise TypeError(
        f"metadata_path must be a csv or tsv file, ending with the appropriate file extension. Value given is {metadata_path}")
metadata_df = pd.read_csv(metadata_path, parse_dates=[collection_date_field], sep=delimiter)
metadata_df['year_decimal'] = metadata_df[collection_date_field].map(date_to_decimal)
beast2xml = BEAST2XML(template=template_xml_path)
seqs = FastaReads([fasta_path])
beast2xml.add_sequences(seqs)
beast2xml.add_dates(date_data=metadata_path,
                    seperator=delimiter,
                    sample_id_field=sample_id_field,
                    collection_date_field=collection_date_field)

beast2xml.add_rate_change_dates(
        parameter="samplingRateChangeTimes",
        dates=sampling_prop_change_dates)

methods = ["Slice", 'ExcludablePrior']

for value in [0, 0.000001]:
    for method in methods:
        beast2xml_copy = deepcopy(beast2xml)
        beast2xml_copy.fix_dimension_values(parameter='samplingProportion', indexed_and_values = {0: value})
        beast2xml_copy.to_xml(
            f'{save_dir}/{method}_fixed_at_{str(value)}.xml',
            chain_length=chain_length,
            log_file_basename=f'{method}_fixed_at_{str(value)}',
            trace_log_every=trace_log_every,
            tree_log_every=tree_log_every,
            screen_log_every=screen_log_every,
            store_state_every=store_state_every,
        )