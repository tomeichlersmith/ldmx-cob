"""Example plotting script to be run inside the container"""

import ROOT
import sys

# turn on batch mode so ROOT doesn't try to launch a graphical interface
ROOT.gROOT.SetBatch(1)

fn = sys.argv[1]

comment = f'run {fn}'
if len(sys.argv) > 2 :
  comment = ' '.join(sys.argv[2:])

# assume first command line argument is the file to plot
rf = ROOT.TFile(fn)

# get the tree of data
tree = rf.Get('hgcroc/adc')

# create a canvas to draw plots on
c = ROOT.TCanvas()

# draw what you want
tree.Draw('adc:channel','link==1','colz')
ROOT.gPad.GetPrimitive("htemp").SetTitle(f'{comment}, link 1')

# print
c.SaveAs('link1_pedestals_by_channel_'+fn.replace('root','pdf'))

