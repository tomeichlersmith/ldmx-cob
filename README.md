# ldmx-cob

Notes and helper scripts for working with LDMX COBs.

## Setup
Define where your `cob` working directory is going to be.
In my work, I have it in `~/cob`. Then

```
git clone <this-repo> ~/cob
source ~/cob/env.sh
```

I suggest putting something similar to the following lines in your `.bashrc` (or equivalent):
```
cob-env() {
  source $HOME/cob/env.sh
  unset -f cob-env
}
```

## ldmx-sw Configuration
The branch of ldmx-sw is called `umn/hgcroc`.
```
cd ldmx-sw
git fetch
<<<<<<< HEAD
git checkout umn/hgcroc
cd Hcal
git checkout umn/hgcroc
=======
git checkout umn/hgcroc # first time
git pull # to update
cd Hcal
git fetch
git checkout umn/hgcroc # first time
git pull # to update
>>>>>>> main
```

The current decoder makes the _hardcoded assumption_ that the FPGA ID is 5.

### General Workflow
After generating new data using the pftool (or however).

#### Pedestal Run
<<<<<<< HEAD
1. Decode `ldmx fire decode.py --num_samples <N> <file>.raw`
=======
1. Decode `ldmx fire decode.py <file>.raw`
>>>>>>> main
2. Check if pedestals look good `ldmx python3 plot.py adc_<file>.root`
3. If you want, make a pedestal table: `ldmx python3 gen_pedestals.py adc_<file>.root --output <name>.csv`

#### Other Runs
<<<<<<< HEAD
1. Decode with pedestals `ldmx fire decode.py --num_samples <N> --pedestals <name>.csv <file>.raw`
=======
1. Decode with pedestals `ldmx fire decode.py --pedestals <name>.csv <file>.raw`
>>>>>>> main
2. Plot: `ldmx python3 plot.py adc_<file>.root`


## SLAC RCE SDK
We use the [SLAC RCE Software Development Kit (SDK)](https://confluence.slac.stanford.edu/display/RPTUSER/SDK+Download+and+Installation) a lot. 
This environment script assumes that a version of the SDK has been downloaded
and unpacked to `${COB_HOME}/sdk`. My setup has a symlink from `sdk` to the version
unpacked from the tarball.

## Rogue
- [Long Intro to Rogue by Ryan](https://indico.cern.ch/event/752029/contributions/3114636/attachments/1703930/2744976/ROGUE_Overview.pdf)
- [Rogue Docs](https://slaclab.github.io/rogue/index.html)
