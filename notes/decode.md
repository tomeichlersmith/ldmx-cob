# Decoding and Plotting Raw Data

Originally posted to a [GitHub gist](https://gist.github.com/tomeichlersmith/5af6ef62eac5c0a7ce1a7a456bac72df) but
moved here for more persistence.

After downloading data taken using `pflib` on `cmslab1`,
we need to decode it before being able to plot the various quantities of interest.
Most of this decoding work has already been implemented in ldmx-sw,
so we just need to massage that into our purposes.

In this GitHub gist, I've included this note as well as a ldmx-sw configuration
script for running with `fire` that will decode the raw data for you and put it
into an easier-to-analyze form.

## Start Up
I needed to add some stuff to ldmx-sw in order to match our needs,
so you will need to re-compile ldmx-sw with my changes.
These changes have been merged into ldmx-sw:trunk, so you just
need to make sure to be on a more recent version of it.

```
cd ldmx-sw
git fetch
git checkout trunk
git pull
git submodule update
source scripts/ldmx-env.sh
ldmx clean src
ldmx cmake -B build -S .
cd build
ldmx make install
```

After completing this re-compilation, you should be good to move on to decoding and then analysis.

## Decoding
Using the code in ldmx-sw is done through the program `fire` which is supplied a python
script to configure how it runs. This GitHub gist has the python configuration script `decode.py`
which is written to configure `fire` for decoding the raw pedestal run data collected at UMN.
```
ldmx fire decode.py some_file.raw
```
`decode.py` is treated by `fire` as a regular Python script, so I have added some additional
command-line parameters. You can see them all by running `ldmx fire decode.py --help`, but
the most important one (which is also required) is `some_file.raw` which is the file with
raw pedestal data. The reason to have this raw file be a command line parameter is so that
you can have multiple raw files each named after different settings that you are testing
and then you can decode them with the same procedure.

### Outputs
Mainly, this program will output a file named similarly to your input raw file.
Using the example above where you input `some_file.raw`, the output file will be `adc_some_file.root`.
This ROOT file has the decoded data in it.

## Plotting
After decoding the raw data, we want to view it.
There are two main ways to view the data (1) interactively with ROOT's broswer
and (2) using a python script to print out plots.

I suggest to start with (1) since it is easier and allows you to discover
what types of plots you want to print out. Once you have found out which plots
you want to be printing, then you can move to (2) in order to speed up the process 
of plotting.

#### ROOT's Browser
We have packaged ROOT's browser into the container, so after decoding the raw
data file you can provide the browser the ROOT file with the decoded data.
```
ldmx rootbrowse adc_some_file.root
```
This launches a graphical interface for exploring the data stored in the file.

**Note**: In order to use a graphical interface from a program within WSL,
you will need to install whats called an "X-server" _outside_ of WSL so that
the program within WSL can connect to your screen. [Here](https://techcommunity.microsoft.com/t5/windows-dev-appconsult/running-wsl-gui-apps-on-windows-10/ba-p/1493242) is tutorial
on getting graphical applications running from within WSL.

ROOT's browser has a specific feature that is incredibly helpful
which is called the "tree viewer". Right-clicking on a tree in the browser
and selecting "StartViewer" opens up this menu.

(I will probably need to show you how to do this, it is not very intuitive.)

#### Python Script
The basic idea of having a plotting script is to allow you to print out
pre-determined plots quickly without having to wait for the extra work
of launching a graphical interface and clicking around inside of it.

Writing plotting scripts is tough, so I've included an example one in
this gist as well. It would be run through the container as well, but
this time using `python3` rather than `fire`.

```
ldmx python3 plot.py adc_some_file.root
```

The output of this command is a PDF file containing a plot
of various channels and their pedestal readings.
You'll notice that this plot is ugly; this is becuase I did not invest
any time into making the plotting script improve how the plot looks.
For internal plots (just you, me, and Jeremy), it doesn't really matter
if a plot is "ugly" as long as it is understandable.
