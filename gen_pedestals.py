"""Generate a CSV table of pedestals from the input decoded data"""

import ROOT
import argparse
import sys
# turn on batch mode so ROOT doesn't try to launch a graphical interface
ROOT.gROOT.SetBatch(1)

parser = argparse.ArgumentParser(f'ldmx python3 {sys.argv[0]}')

parser.add_argument('input_file')
parser.add_argument('--output',default='pedestals.csv',type=str)

arg = parser.parse_args()

rf = ROOT.TFile(arg.input_file)

# get the tree of data
tree = rf.Get('hgcroc/adc')

pedestal_table = {}
for entry in tree :
    if entry.raw_id not in pedestal_table :
        pedestal_table[entry.raw_id] = [0., 0]

    pedestal_table[entry.raw_id][0] += sum(entry.raw_adc)
    pedestal_table[entry.raw_id][1] += len(entry.raw_adc)

# print to a CSV
with open(arg.output,'w') as f :
    f.write('DetID,PEDESTAL\n')
    for raw_id, pedestal in pedestal_table.items() :
        f.write(f'{hex(raw_id)},{int(pedestal[0]/pedestal[1])}\n')
