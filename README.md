# ldmx-cob

Notes and helper scripts for working with LDMX COBs.

**Note**: The decoding script has been moved to the [ldmx-tb-online/near-offline directory](https://github.com/LDMX-Software/ldmx-tb-online).

- [setup](notes/setup.md) - first time getting started on cmslab1
- [workflow](notes/workflow.md) - data generation, decoding, and analysis commands
- [cob](notes/cob.md) - general notes on setting up COB at UMN
- [decode](notes/decode.md) - decoding and plotting raw data from UMN setup
- [images](notes/images.md) - how the DPM and DTM images at UMN were constructed
- [pflib](notes/pflib.md) - configuration library for the polar fire

## Interactive Notebooks
cmslab1 has the necessary depedencies installed so we can launch jupyter notebook/lab from that computer and connect to it on our remote computers. I prefer `jupyter lab` due to its higher number of features; however, `jupyter notebook` can function as well.

### First Time
On the first time connecting to `cmslab1`, make sure the interactive notebook and its dependencies are installed for your user.
```bash
python3 -m pip install --user --upgrade wheel
python3 -m pip install --user --upgrade notebook jupyterlab uproot pandas
```

### Outline of Setup Commands
Summarized from [a blog post](https://medium.com/@apbetahouse45/how-to-run-jupyter-notebooks-on-remote-server-part-1-ssh-a2be0232c533).
1. Connect to cmslab1 with a specific port number (run from your laptop): `ssh -L 1234:localhost:1234 cmslab1`
2. Launch the jupyter notebook with the same port number (on cmslab1, assuming already in `ldmx-cob` directory): `jupyter notebook --no-browser --port 1234`
3. Open one of the links provided in your browser on your computer. On my computer (Ubuntu 20.04), you can do this by holding down `Shift` and then right-clicking on the link and selecting `Open link`. You could also hold down `Shift` to highlight the link and the use `Ctrl+Shift+C` to copy the link and then paste it into your browser.

#### Tip
You can avoid having to type the `-L` part every time by adding the `LocalForward 1234 localhost:1234` to your ssh config file.
```
# example ~/.ssh/config
Host cmslab1 :
  User <umn-username>
  HostName cmslab1.spa.umn.edu
  LocalForward 1234 localhost:1234
```

#### Jupyter Lab
[`jupyter lab`](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html) can be accessed the same way except its more complicated to change the port it displays to, so it is easiest to just use its default port `8888` and make sure that port is open when you `ssh`.

## SLAC RCE SDK
We use the [SLAC RCE Software Development Kit (SDK)](https://confluence.slac.stanford.edu/display/RPTUSER/SDK+Download+and+Installation) a lot. 
This environment script assumes that a version of the SDK has been downloaded
and unpacked to `${COB_HOME}/sdk`. My setup has a symlink from `sdk` to the version
unpacked from the tarball.

## Rogue
- [Long Intro to Rogue by Ryan](https://indico.cern.ch/event/752029/contributions/3114636/attachments/1703930/2744976/ROGUE_Overview.pdf)
- [Rogue Docs](https://slaclab.github.io/rogue/index.html)

