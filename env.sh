
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35
export cob_shelf=13

if [[ -z ${ROGUE_DIR} ]]; then
  source /opt/rogue/setup_rogue.sh || return $?
fi

if [[ ":$LD_LIBRARY_PATH:" != *":/opt/cactus/lib:"* ]]; then
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/cactus/lib
fi

if [[ -z ${FiberTrackerDAQ_DIR} ]]; then
  export FiberTrackerDAQ_DIR=/home/eichl008/FiberTrackerDAQ
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${FiberTrackerDAQ_DIR}/lib:${FiberTrackerDAQ_DIR}/dip-5.7.0/lib64
fi

if [[ -z ${EUDAQ_DIR} ]]; then
  export EUDAQ_DIR=$HOME/eudaq
  export PATH=${PATH}:${EUDAQ_DIR}/bin
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${EUDAQ_DIR}/lib
fi

if [[ -z ${yamlcpp_DIR} ]]; then
  export yamlcpp_DIR=$HOME/yaml-cpp/install
  export PATH=${PATH}:${yamlcpp_DIR}/bin
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${yamlcpp_DIR}/lib64
  export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:${yamlcpp_DIR}
fi

if [[ -z ${pflib_DIR} ]]; then
  export pflib_DIR=$HOME/ldmx/pflib/install
  export PATH=${PATH}:${pflib_DIR}/bin
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${pflib_DIR}/lib
  export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:${pflib_DIR}
  export PFTOOLRC=$HOME/ldmx/pflib/umn.pftoolrc
fi

if [[ ":$LD_LIBRARY_PATH:" != *":$HOME/ldmx/tb-online/install/software/lib:"* ]]; then
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$HOME/ldmx/tb-online/software/install/lib
  export PATH=${PATH}:$HOME/ldmx/tb-online/software/install/bin
fi

if [[ -z ${COB_HOME} ]]; then
  COB_HOME="$(dirname ${BASH_SOURCE[0]})"
  export COB_HOME="$(realpath ${COB_HOME})"
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

