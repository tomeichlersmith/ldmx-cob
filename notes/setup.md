# Setup on cmslab1
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
