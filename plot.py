"""Plotting data ntuplized by the umn/hgcroc branch of ldmx-sw
using the ldmx-cob/decode.py configuration script"""

import ROOT
import sys
import argparse
# turn on batch mode so ROOT doesn't try to launch a graphical interface
ROOT.gROOT.SetBatch(1)

parser = argparse.ArgumentParser(f'ldmx python3 {sys.argv[0]}',
        description=sys.modules[__name__].__doc__)

parser.add_argument('input_file',help='Data file to plot.')
parser.add_argument('--comment',help='Comment to be used instead of data file name in plot titles.')

arg = parser.parse_args()

if arg.comment is None :
    arg.comment = f'run {arg.input_file}'

rf = ROOT.TFile(arg.input_file)
tree = rf.Get('hgcroc/adc')
c = ROOT.TCanvas()

# adc by channel for link 1
tree.Draw('adc:channel','link==1','colz')
ROOT.gPad.GetPrimitive("htemp").SetTitle(f'{comment}, link 1')
c.SaveAs('link1_pedestals_by_channel_'+fn.replace('root','pdf'))

