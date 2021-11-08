
export dtm_ip=192.168.28.100
export shmm_ip=192.168.1.35

source /home/eichl008/cob/V3.4.1/i86-linux-64/tools/envs-sdk.sh || return $?
export PS1="\[$(tput setaf 5)\][cob]\[$(tput sgr0)\] ${PS1}"

export cob_shelf=13

reboot_cob_shelf() {
  ssh root@${shmm_ip} "clia deactivate ${cob_shelf} && sleep 5 && clia activate ${cob_shelf}"
}
