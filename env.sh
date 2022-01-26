
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35
export cob_shelf=13

if [[ -z ${ROGUE_DIR} ]]; then
  source /opt/rogue/setup_rogue.sh || return $?
fi

if [[ -z ${EUDAQ_DIR} ]]; then
  export EUDAQ_DIR=$HOME/eudaq
  export PATH=${PATH}:${EUDAQ_DIR}/bin
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${EUDAQ_DIR}/lib
fi

if [[ -z ${yamlcpp_DIR} ]]; then
  export yamlcpp_DIR=$HOME/yaml-cpp/install
  export PATH=${PATH}:${yamlcpp_DIR}/bin
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${yamlcpp_DIR}/lib
  export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:${yamlcpp_DIR}
fi

if [[ -z ${COB_HOME} ]]; then
  COB_HOME="$(dirname ${BASH_SOURCE[0]})"
  export COB_HOME="$(realpath ${COB_HOME})"
  # add ldmx-daq/software install directories to the env variables
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${COB_HOME}/ldmx-daq/software/install/lib
  export PYTHONPATH=${PYTHONPATH}:${COB_HOME}/ldmx-daq/software/install/lib
  export PATH=${PATH}:${COB_HOME}/ldmx-daq/software/install/bin
  # add [cob] tag to shell prompt
  export PS1="\[$(tput setaf 5)\][cob]\[$(tput sgr0)\] ${PS1}"
  # if SDK exists here, source its environment
  if [[ -d ${COB_HOME}/sdk ]]; then
    source ${COB_HOME}/sdk/i86-linux-64/tools/envs-sdk.sh || return $?
    reboot_cob_shelf() {
      ssh root@${shmm_ip} "clia deactivate board ${cob_shelf} && sleep 5 && clia activate board ${cob_shelf}"
    }
  fi
fi

raw2txt() {
  hexdump -v -e '1/4 "%08x " "\n"' $@
}

