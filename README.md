# ldmx-cob

Notes and helper scripts for working with LDMX COBs.
Meant to be used as a bare repository.

## Setup
Similar to this [tracking dotfiles tutorial](https://www.atlassian.com/git/tutorials/dotfiles).

Define where your `cob` working directory is going to be.
In my work, I have it in `~/cob`. Then

```
mkdir ~/cob
git clone --bare <this-repo> $HOME/cob/.git
git --git-dir $HOME/cob/.git --work-tree $HOME/cob checkout main
source ~/cob/env.sh
cob-git config --local status.showUntrackedFiles no
```
The environment script defines a helpful valias for the ugly `git` command `cob-git` which
you can treat like a normal `git`.

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
