
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35
export cob_shelf=13

if [[ -z ${ROGUE_DIR} ]]; then
  source /opt/rogue/setup_rogue.sh
fi

if [[ -z ${COB_HOME} ]]; then
  COB_HOME="$(dirname ${BASH_SOURCE[0]})"
  export COB_HOME="$(realpath ${COB_HOME})"
fi

if [[ -f ${COB_HOME}/ldmx-daq/software/pflib/Makefile ]]; then
  # we are on Jeremy's branch with the Makefile
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${COB_HOME}/ldmx-daq/software/pflib/lib
  alias tool='${COB_HOME}/ldmx-daq/software/pflib/tool/pftool.exe'
else
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${COB_HOME}/ldmx-daq/software/install/lib
  export PYTHONPATH=${PYTHONPATH}:${COB_HOME}/ldmx-daq/software/install/lib
fi

if [[ -d ${COB_HOME}/sdk ]]; then
  source ${COB_HOME}/sdk/i86-linux-64/tools/envs-sdk.sh
fi
export PS1="\[$(tput setaf 5)\][cob]\[$(tput sgr0)\] ${PS1}"

reboot_cob_shelf() {
  ssh root@${shmm_ip} "clia deactivate ${cob_shelf} && sleep 5 && clia activate ${cob_shelf}"
}

alias cob-git='git --git-dir=${COB_HOME}/.git --work-tree=${COB_HOME}'

raw2txt() {
  hexdump -v -e '1/4 "%08x " "\n"' $@
}

