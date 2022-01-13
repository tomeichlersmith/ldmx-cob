
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35
export cob_shelf=13

if [[ -z ${ROGUE_DIR} ]]; then
  source /opt/rogue/setup_rogue.sh || return $?
fi

if [[ -z ${COB_HOME} ]]; then
  COB_HOME="$(dirname ${BASH_SOURCE[0]})"
  export COB_HOME="$(realpath ${COB_HOME})"
fi

if [ "$1" == "dev" ]; then
  # ldmx-daq-dev is my (development) branch
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${COB_HOME}/ldmx-daq-dev/software/install/lib
  export PYTHONPATH=${PYTHONPATH}:${COB_HOME}/ldmx-daq-dev/software/install/lib
  export PATH=${PATH}${COB_HOME}/ldmx-daq-dev/software/install/bin
  tag='cob-dev'
else
  # ldmx-daq is Jeremy's (more stable) branch
  #  so it is the default
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${COB_HOME}/ldmx-daq/software/install/lib
  export PYTHONPATH=${PYTHONPATH}:${COB_HOME}/ldmx-daq/software/install/lib
  export PATH=${PATH}${COB_HOME}/ldmx-daq/software/install/bin
  tag='cob'
fi

if [[ -d ${COB_HOME}/sdk ]]; then
  source ${COB_HOME}/sdk/i86-linux-64/tools/envs-sdk.sh || return $?
fi
export PS1="\[$(tput setaf 5)\][${tag}]\[$(tput sgr0)\] ${PS1}"
unset tag

reboot_cob_shelf() {
  ssh root@${shmm_ip} "clia deactivate ${cob_shelf} && sleep 5 && clia activate ${cob_shelf}"
}

raw2txt() {
  hexdump -v -e '1/4 "%08x " "\n"' $@
}

