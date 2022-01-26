# ldmx-cob

Notes and helper scripts for working with LDMX COBs.

## Setup on cmslab1
Our lab computer which we are using to connect to the COB and its components is cmslab1.
Here, I assume that you already can `ssh` to cmslab1 and you have an ssh-key on cmslab1
that is connected to your GitHub account (if you don't have that setup yet, you can always
switch the github links from ssh-style to http-style.)

#### Downloads
Here is a summary of the commands to run to download the various code we use with
the COB. I also have the code place in a certain structure so that the environment
script in the ldmx-cob repository can pickup the SDK downloaded for the RCEs.
```
mkdir ~/ldmx
cd ~/ldmx
git clone --recursive git@github.com:LDMX-Software/ldmx-sw.git ldmx-sw
git clone git@github.com:tomeichlersmith/ldmx-cob.git cob
cd cob
wget http://www.slac.stanford.edu/projects/CTK/SDK/rce-sdk-V3.4.1.tar.gz
tar xzvf rce-sdk-V3.4.1.tar.gz
ln -s V3.4.1 sdk
tar xzvf /home/eichl008/ldmx-daq-pflib-v1.0.tar.gz
ln -s ldmx-daq-pflib-v1.0 ldmx-daq
```

#### Compiling
First, we go to the branch of ldmx-sw we are using to decode the raw data
from our hgcroc and then we compile ldmx-sw.
```
cd ~/ldmx/ldmx-sw
git checkout umn/hgcroc
git submodule update
cd Hcal
git checkout umn/hgcroc
cd ..
source scripts/ldmx-env.sh # this will download a container image
ldmx cmake -B build -S .
cd build
ldmx make -j2 install
```
Compile and install ldmx-daq/software for using our Polarfire interaction library.
```
source ~/ldmx/cob/env.sh
cd ~/ldmx/cob/ldmx-daq/software
cmake -B build -S .
cd build
make -j2 install
```

#### Usability

I suggest putting something similar to the following lines in your `.bashrc` (or equivalent):
```
cob-env() {
  source $HOME/ldmx/ldmx-sw/scripts/ldmx-env.sh
  source $HOME/ldmx/cob/env.sh
  unset -f cob-env
}
```
This lets you setup the environment pretty quickly, but also doesn't pollute your default environment with our software.

## ldmx-sw Configuration
The branch of ldmx-sw is called `umn/hgcroc`.
```
cd ldmx-sw
git fetch
git checkout umn/hgcroc # first time
git pull # to update
cd Hcal
git fetch
git checkout umn/hgcroc # first time
git pull # to update
```

The current decoder makes the _hardcoded assumption_ that the FPGA ID is 5.

### General Workflow
After generating new data using the pftool (or however).

#### Pedestal Run
1. Decode `ldmx fire decode.py <file>.raw`
2. Check if pedestals look good `ldmx python3 plot.py adc_<file>.root`
3. If you want, make a pedestal table: `ldmx python3 gen_pedestals.py adc_<file>.root --output <name>.csv`

#### Other Runs
1. Decode with pedestals `ldmx fire decode.py --pedestals <name>.csv <file>.raw`
2. Plot: `ldmx python3 plot.py adc_<file>.root`


## SLAC RCE SDK
We use the [SLAC RCE Software Development Kit (SDK)](https://confluence.slac.stanford.edu/display/RPTUSER/SDK+Download+and+Installation) a lot. 
This environment script assumes that a version of the SDK has been downloaded
and unpacked to `${COB_HOME}/sdk`. My setup has a symlink from `sdk` to the version
unpacked from the tarball.

## Rogue
- [Long Intro to Rogue by Ryan](https://indico.cern.ch/event/752029/contributions/3114636/attachments/1703930/2744976/ROGUE_Overview.pdf)
- [Rogue Docs](https://slaclab.github.io/rogue/index.html)
