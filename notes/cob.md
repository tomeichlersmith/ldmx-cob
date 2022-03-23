
# Image Construction

Steps taken to make a bootable DPM/DTM image and notes about 
necessary changes to the lab infrastructure are kept in [images.md](images.md).

# Terminology

- DAQ - Data AQuisition
- Crate - physical structure holding DAQ electronics
- Shelf - a single entry in the crate
- Shelf Manager - board with software to control the entries in the crate as well as supporting infrastructure (like fans)
    - our shelf manager is a [Pigeon Point Shelf Manager](https://schroff.nvent.com/sites/g/files/hdkjer281/files/acquiadam/2020-11/ShelfManagerUG_3_7_1_20180515.pdf)
- COB - Cluster On Board, a board filling a shelf in a crate
- RCE - Reconfigurable Cluster Element
- DPM - Data Processing Module, each holds two RCEs
- DTM - Data Transfer Module, interfacing module between DPMs and outside world, has one RCE
- SDK - Software Development Kit, software/firmware that can be used for our purposes with RCEs
- bay - One of the connections to a module on the COB

# Common Processes
I have tried to store helpful short-cuts in a short environment script that is pretty portable.
The command below assume that you have entered this environment.
```
source env.sh
```

## Watching a Shelf Component Boot
The normal way to access any of the shelf components is through ssh,
but ssh is not available during boot. This means if you want to access
a component during its boot (to debug an error or change some boot settings),
you will need to access the shelf component via a serial connection.

### Wired Connection
Both our COB and our shelf manager have wired connections allowing the user
to connect serially to the component using a tool called 'minicom' and a USB port.
You will need sudo access on the computer you are using 'minicom' on.

### Wireless Connection
This can be done for watching the DPMs boot since they are serially connected to the DTM,
and it requires the DTM to be already booted and accessible via ssh.

```
ssh root@${dtm_ip}
minicom bay<dpm>.<rce>
```

## Checking the Status of the COB
This is done using tools from the RCE SDK provided by SLAC.
Our COB is in shelf number 13 on the crate.

```
cob_dump --rce ${shmm_ip}/13
```

Boot Codes: https://confluence.slac.stanford.edu/display/RPTUSER/RCE+Boot+Status+Codes

## Remotely Restarting a COB Component
Again, this is done using tools from the SDK.

```
cob_rce_reset ${shmm_ip}/13/<dpm>/<rce>
```

Run `cob_rce_reset` without any arguments to get a printout
of its help message - there are many shortcuts for specifying
all DPMs or the DTM without having to know its numbers.

## Determining Where you Are
Sometimes you forget which component you are on, the simplest method I've found for figuring
this out is by using a property of how the COB compoents boot. Currently (as of 10/6/2021),
they all boot with a specific environment variable.

```
HOST=1/13/<dpm>/<rce>
```

The shelf manager does not have this environment variable.

Another option is to run `sysinfo` which should print the RCE ID on the COB components
and is not available on the shelf manager.

## Changing COB component to boot from NFS
DHCPD configuration
- Make sure `root-path` points to full path of root direcotry for that COB component on cmslab0
- Make sure `root-path` is inside a directory exported by cmslab0 (showmount --exports)
- Make sure `next-server` is the IP address of cmslab0

Watch Boot of COB component via minicom (either wired or wireless) and interrupt autoboot.
- Reset to default environment: `env default -a`
- Set boot mode to nfs: `setenv modeboot nfsboot`
- Persist boot delay: `setenv bootdelay 5`
- (for DTM): Change command to use differently named firmware file:
  - `setenv nfsfpga 'nfs 0x1000000 ${rootpath}/boot/fpga.bit.dtm && fpga loadb 0 0x1000000 ${filesize}'` 
  - The only change should be changing the bit file name from `fpga.bit` to `fpga.bit.dtm`
- Save environment: `saveenv`
- Restart component: `reset`

## Looking at SD Card
You can still look at the SD Card even when booting from NFS.
This is important for determining which boot.bin and uboot.env is being used
during the part of the boot process that is before NFS takes over.

```
# on DPM/DTM of interest
mkdir /mnt/sdcard
mount /dev/mmcblk0p1 /mnt/sdcard/
```

## Restarting Whole COB
We can do this from the shelf manager by deactiviating and then reactivating the shelf
that the COB is in.

```
ssh shmm
clia deactivate 13
# wait a few seconds
clia activate 13
```

# Check how RCE was Booted
You can look at the contents of the `/proc/cmdline` file to see what the commandline options for 
booting the kernel were. When booted from the SD card, the 'root' option is set to 
`/dev/mmcblk0p1` (the SD card's device point). When booted from NFS, the 'root' option
is set to `/dev/nfs`.

# Installing Rogue on RCE NFS

[Rogue building from source docs](https://slaclab.github.io/rogue/installing/build.html)

I chose to do a 'system' install because I think that makes the most sense for our use case.

Command log of what I did.

```
ssh bay3.2
pacman -Syu cmake
pacman-key --init
pacman-key --populate
pacman-key- --refresh
pacman -Sy archlinux-keyring
  # ctrl-C after stuck in gpg key check loop
pacman -Sy cmake
  # success!
pacman -Syu cmake python3 boost bzip2 python-pip git zeromq pyqt5
  # takes a long time
git clone https://github.com/slaclab/rogue.git
cd rogue
git checkout v5.11.0
pip3 install -r pip_requirements.txt
  # takes a long time, seems to be hanging on 'Installing build dependencies ...'
  # see error on numpy setup 'Broken toolchain: cannot link a simple C program'
pacman -Sy gcc
pip3 install -r pip_requirements.txt
  # hung at same point
pip3 install numpy
  # slow at Building wheel for numpy
  #   looked at pip_requirements, and looks like code formatting/testing modules, so skipping
cmake -B build -S . -DROGUE_INSTALL=system
  # failed to find builder
pacman -Sy make
cmake -B build -S . -DROGUE_INSTALL=system
  # failed to find numpy headers
pacman -Sy python-numpy
cmake -B build -S . -DROGUE_INSTALL=system
  # success!
cd build
make
  # take a long time probably
make install
  # finished over the weekend
  
# add /usr/local to list of directories to default link
echo "
  # include libraries installed to /usr/local
  /usr/local/lib
  " >> /etc/ld.so.conf
ldconfig
```

## Getting pyroque to Work
Trying to install more of the python dependencies.
```
python -m pip install -r pip_requirements.txt
  # hung on p4p
python -m pip install sqlalchemy pyserial
  # successful
python -m pip install p4p
```
