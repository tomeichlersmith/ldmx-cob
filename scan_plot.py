"""Plotting scans of parameters using uproot, pandas, and matplotlib

python3 -m pip install --upgrade uproot matplotlib pandas notebook

Unfortunately, the "JPEG" libraries are not available on cmslab1,
so we cannot run matplotlib-based plotting there at this time.
"""

import uproot
import matplotlib.pyplot as plt

input_file_name = 'some_file.root'

# open tree created by ntuplizer in decoding sequence
#   and read into pandas dataframe
with uproot.open(f'{input_file_name:adc/adc}') as t :
    df = t.arrays(library='pd')

# df is now a pandas.DataFrame with columns corresponding to the branches of the TTree
print(df)

events_per_sample = 100
min_value = 1
max_value = 5
step = 1

for i, sample in enumerate(range(min_value,max_value,step)) :
    data_using_this_sample = df[(df['event']>=events_per_sample*i)&(df['event']<events_per_sample*(i+1))]
    plt.hist(data_using_this_smaple['channel'], data_using_this_sample['adc'])
