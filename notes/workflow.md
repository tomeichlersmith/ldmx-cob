# General Workflow

## Data Generation

### pftool
Jeremy has developed this command using a menu-based application derived from uMNio.
After installing, you can launch this menu-based app along with the hostname that has
the polarfire we wish to talk to.
Since the polarfire is connected to DPM 1.0 on COB 13 we use
```
pftool cob13_dpm1_0
```
This may change in the future if we need to change which DPM has the polarfire or which shelf has the COB.
A successful open of the tool looks like
```
pftool cob13_dpm1_0
 Polarfire firemware :     1.24

  ... menu printout ...
 >
```
while an unsuccessful connection will usually report a timeout error.
The firmware version will change periodically as Jeremy makes developments.

You can exit the tool at anytime using ctrl+C.

More notes are in [pflib](pflib.md) but they go stale quickly as we develop the tool.
Use slack with an error printout if you are seeing something funky or have questions.

## Decoding and Analysis
After generating new data using the pftool (or however).

**NOTE**: The current decoding software in ldmx-sw makes the hard-coded assumption that the FPGA ID is 5.

### Pedestal Run
1. Decode `ldmx fire decode.py <file>.raw`
2. Check if pedestals look good `ldmx python3 plot.py adc_<file>.root`
3. If you want, make a pedestal table: `ldmx python3 gen_pedestals.py adc_<file>.root --output <name>.csv`

### Other Runs
1. Decode with pedestals `ldmx fire decode.py --pedestals <name>.csv <file>.raw`
2. Plot: `ldmx python3 plot.py adc_<file>.root`

