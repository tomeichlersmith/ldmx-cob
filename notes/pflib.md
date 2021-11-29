# pflib Notes

Short notes on using PolarFire configuration Library.

## Start Up

Jeremy has developed most of the interaction using a menu-based
application derived from uMNio. Not super important, just some background.

On his branch `polarfire-lib-dev`, the cmake integration has not been merged yet;
however, Jeremy has included a `Makefile` which does the job with minor changes 
to the environment script.

```
cd ~/cob
source env.sh
cd ldmx-daq/software/pflib
make
./tool/pftool.exe
```

The last line helps us check if things are linked properly and will
print out the help message showing how to use this tool.
We need to provide the hostname or IP address of the DPM we want to play with.

I can't figure out how Jeremy was able to get the hostname working,
so I'm just going to provide the IP address for now.

#### Sidenote: Lookup IP addresses for DPMs
These are stored and defined in the `/etc/dhcpd_cob.conf` file on `cmslab0`.
```
ssh cmslab0 cat /etc/dhcpd_cob.conf
```

## Running
A successful open of the tool looks like
```
> ./tool/pftool.exe 192.168.28.103
 Polarfire firmware :    1.24

   STATUS       Status summary
   FAST_CONTROL Fast Control
   ROC          ROC Configuration
   BIAS         BIAS voltage setting
   ELINKS       Manage the elinks
   DAQ          DAQ
   EXPERT       Expert functions
   EXIT         Exit this tool
 >
```
Notice that the firmware version is printed. This shows a successful connection to the DPM.
This tool opens up a rudimentary terminal with various menus and submenus with commands
for configuring the chips and aquiring data.

#### Exiting
You can leave the tool at anytime by pressing ctrl+C.

### DAQ Menu
```
 > daq

   DEBUG        Debugging menu
   STATUS       Status of the DAQ
   ENABLE       Toggle enable status
   ZS           Toggle ZS status
   L1APARAMS    Setup parameters for L1A capture
   READ         Read an event
   RESET        Reset the DAQ
   HARD_RESET   Reset the DAQ, including all parameters
   STANDARD     Do the standard setup for HCAL
   PEDESTAL     Take a simple random pedestal run
   QUIT         Back to top menu
 >
```

The menu will be re-printed after each command. 
I will omit this printout for the rest of the snippets.

For this DPM, the status is helpful to look at.
```
 > status
-----Front-end FIFO-----
 Header occupancy : 0  Maximum occupancy : 1
 Next event info: 0x78c89024
-----Per-ROCLINK processing-----
 Link  ID  EN ZS FL EM
   0  0500  1  0  0  1      00800001
   1  0501  1  0  0  1      00800001
   2  0502  1  1  0  1      00800007
   3  0503  1  1  0  1      00800007
   4  0504  1  1  0  1      00800007
   5  0505  1  1  0  1      00800007
   6  0506  1  1  0  1      00800007
   7  0507  1  1  0  1      00800007
-----Off-detector FIFO-----
 NOT-FULL     EMPTY  Events ready :   0  Next event size : 101
```
Notice links 0 and 1 have no zero suppression (ZS = 0) and all of the links are enabled (EN = 1).
The ID number is defined during the execution of `standard` and is `(<fpga-id> << 8) + <link>`.
This is the status for a "standard" setup. You can get back to the "standard" setup
by running the `daq` commands `hard_reset`, `standard`, `enable` (in that order).

Now we can take runs of data.
The simplest data we can take is a "pedestal run" 
where we just watch the incoming links and read out the data.
This is done with the `pedestal` command in the `daq` menu.
We can choose the number of events as well as the name of the output raw file.

The output raw file is a binary file, so it won't be viewable by us.
I have included a function in the environment script to help printout this data
in 32-bit word increments. This is how the data is encoded by the firmware/chip and
will be how the data is decoded within ldmx-sw, so it is a good debugging tool.
```
raw2txt <file.raw>
```
