##
from beast2xml.beast2 import BEAST2XML
from dark.fasta import FastaReads

temp_xml_tile = 'invader_first_160.xml'
temp_xml = BEAST2XML(template=temp_xml_tile)

## Adding replacing the sequence and age data with resident data
res_seqs = FastaReads(['res_random_200_draw_1.fasta'])
res_dates = 'res_random_200_draw_1.txt'
temp_xml.add_sequences(res_seqs)
temp_xml.add_ages(res_dates)
# Change Origin starting value, lower and upper limit on statenode
temp_xml.change_prior('origin', 'uniform', lower='0.3973744292234187', upper='4.665342465753156')
temp_xml.change_parameter_state_node('origin', value='4.665342465753156')
temp_xml.to_xml('res_random_200_draw_1.xml')