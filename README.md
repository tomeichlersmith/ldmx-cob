# ldmx-cob

Notes and helper scripts for working with LDMX COBs.
Meant to be used as a bare repository.

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

## SLAC RCE SDK
We use the [SLAC RCE Software Development Kit (SDK)](https://confluence.slac.stanford.edu/display/RPTUSER/SDK+Download+and+Installation) a lot. 
This environment script assumes that a version of the SDK has been downloaded
and unpacked to `${COB_HOME}/sdk`. My setup has a symlink from `sdk` to the version
unpacked from the tarball.

## Rogue
- [Long Intro to Rogue by Ryan](https://indico.cern.ch/event/752029/contributions/3114636/attachments/1703930/2744976/ROGUE_Overview.pdf)
- [Rogue Docs](https://slaclab.github.io/rogue/index.html)
