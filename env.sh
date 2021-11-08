
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35
export cob_shelf=13

if [[ -z ${COB_HOME} ]]; then
  export COB_HOME="$(dirname ${BASH_SOURCE[0]})"
fi

source ${COB_HOME}/sdk/i86-linux-64/tools/envs-sdk.sh || return $?
export PS1="\[$(tput setaf 5)\][cob]\[$(tput sgr0)\] ${PS1}"

reboot_cob_shelf() {
  ssh root@${shmm_ip} "clia deactivate ${cob_shelf} && sleep 5 && clia activate ${cob_shelf}"
}

alias cob-git='git --git-dir=${COB_HOME}/.git --work-tree=${COB_HOME}'
