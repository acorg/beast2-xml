##
from beast2xml.beast2 import BEAST2XML
import pandas as pd
from dark.fasta import FastaReads

temp_xml_tile = 'invader_first_160.xml'
temp_xml = BEAST2XML(template=temp_xml_tile)

metadata = pd.read_csv('first_160.csv', parse_dates=['date'])
youngest_tip = metadata.date.max(skipna=True)
oldest_tip = metadata.date.min(skipna=True)

##
end_date = youngest_tip.replace(day=1)
start_date = oldest_tip.replace(day=1)

date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
dates = date_range
temp_xml.add_rate_change_dates(parameter='birthRateChangeTimes', dates=dates,  youngest_tip=youngest_tip)

voi_seqs = FastaReads(['first_160.fasta'])
voi_dates = 'first_160.txt'
temp_xml.add_sequences(voi_seqs)
temp_xml.add_ages(voi_dates)

temp_xml.to_xml('VOI_with_monthly_R_changes.xml')