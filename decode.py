"""Basic HGCROCv2RawDataFile reformatting configuration"""

import argparse, sys

parser = argparse.ArgumentParser(f'ldmx fire {sys.argv[0]}')

parser.add_argument('input_file')
parser.add_argument('--pause',action='store_true')
parser.add_argument('--max_events',default=100,type=int)
parser.add_argument('--num_samples',default=1,type=int,required=True)
parser.add_argument('--pedestals',default='NO_PEDESTALS',type=str)

arg = parser.parse_args()

"""
# single sample packet with no zero suppression

len = 41*(num actually connected links) 
    + 2*(not connection links) 
    + 2 # fpga headers
    + 2 # fpga link count words
    + 1 # fpga checksum footer

For Jeremy's test setup at CERN, there are 6 actually
connected links (or 3 HGC ROCs both halves connected),
so we get an event packet lenght of

    255

This is the length of event packets for runs 207, 208.

# multi-sample event packet with no zero supp

For the multi-sample no zero supp event packet,
Jeremy added a few extra words.

len = 2 # header signal words
    + 0 # event header <- seems to be missing in run208 file
    + (half of num samples rounded up) # counter words
    + (num sample sample packets)
    + 2 # footer signal words

For run208 Jeremy had 4 samples for each event but it seems
to be missing the whole-event header word.

    1026

The text version of the run208 file that Jeremy produced has 102600
lines for a one-hundred event run, so I'm trusting this.

When Jeremy adds the extra event header word in, this number will
increase to 1027.

# UMN HGC ROC Setup
  Firmware Version 1.24 Pedestal Run
    (quoting firmware version because this might change)

  len = 2 # header signal words
      + 1 # event header
      + 1 # num samples per event in pedestal run
      + 2 # fpga header
      + 2 # link count words
      + 41*2 # actual readout links
      + 2*7 # unconnected links
      + 1 # fpga footer
      + 2 # event footers
    = 107
"""

from LDMX.Framework import ldmxcfg

p = ldmxcfg.Process('unpack')
p.maxEvents = arg.max_events
p.termLogLevel = 0
p.logFrequency = 1

import LDMX.Hcal.hgcrocFormat as hcal_format
import LDMX.Hcal.digi as hcal_digi
import LDMX.Hcal.HcalGeometry
import LDMX.Hcal.hcal_hardcoded_conditions
from LDMX.DQM import umn
from LDMX.Packing import rawio

import os
base_name = os.path.basename(arg.input_file).replace('.raw','')
dir_name  = os.path.dirname(arg.input_file)
if not dir_name :
    dir_name = '.'

p.outputFiles = [f'{dir_name}/unpacked_{base_name}.root']

# where the ntuplizing tree will go
p.histogramFile = f'adc_{base_name}.root'

def num_words(n_samples) :
    """Num Words in HGC ROC MultiSample Readout 
      len = 2 # header signal words
          + 1 # event header
          + (n+1)//2 # num samples per event divided by 2 rounded up
          + n*( # num sample packets
              2 # fpga header
            + 2 # link count words
            + 41*2 # actual readout links
            + 2*7 # unconnected links
            + 1 # fpga footer
          )
          + 2 # event footers
        = 5 + (n+1)//2 + n*101
    """
    return 5 + (n_samples+1)//2 + n_samples*101

# sequence
#   1. split file into event packets
#   2. decode event packet into digi collection
#   3. ntuplize digi collection
p.sequence = [ 
        rawio.SingleSubsystemUnpacker(
            raw_file = arg.input_file, 
            output_name = 'UMNChipSettingsTestRaw', 
            num_bytes_per_event = 4*num_words(arg.num_samples),
            detector_name = 'DNE'
            ),
        hcal_format.HcalRawDecoder(
            input_name = 'UMNChipSettingsTestRaw', 
            output_name = 'UMNChipSettingsTestDigis'
            ),
        umn.TestHgcRoc(
            input_name = 'UMNChipSettingsTestDigis',
            pedestal_table = arg.pedestals
            )
        ]

if arg.pause :
    p.pause()
