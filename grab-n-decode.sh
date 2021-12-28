# environment script for writing a helpful bash function

__grabndecode_help__() {
  cat <<\HELP

 Download a file from cmslab1, decode and plot it.
 This script requires the user to be in the ldmx environment
 and have a compiled version of ldmx-sw ready to decode the raw data file.

 USAGE:
  grab-n-decode <file> [destination]

 ARGUMENTS:
  file          (required) the path to the raw data file on cmslab1 relative to your home directory on the remote server
  destination   (optional) directory for where the raw data file, its unpacked data, and the plots should be.
                 this directory needs to be mounted to the container for decoding and plotting purposes
                 the current directory is used as the default

 CONFIGURATION:
HELP
  echo "  Decoding Script: ${grabndecode_decode_py}"
  echo "  Plotting Script: ${grabndecode_plot_py}"
  echo "  Raw data file origin: ${grabndecode_origin}"
  echo ""
}

__grabndecode_return__() {
  # pass actual old pwd as first arg
  cd - &>/dev/null
  export OLDPWD=$1
}

__grabndecode_deduce_configuration__() {
  # get the directory this source code is in
  # https://stackoverflow.com/a/246128/17617632
  local _script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)

  export grabndecode_decode_py=${_script_dir}/decode.py
  export grabndecode_plot_py=${_script_dir}/plot.py
  export grabndecode_origin=cmslab1

  if [ ! -f ${grabndecode_decode_py} ] ; then
    echo "${grabndecode_decode_py} decoding config script not found."
    echo "  You can set this manually using"
    echo "    export grabndecode_decode_py=full/path/to/decode.py"
    return 1
  fi
  if [ ! -f ${grabndecode_plot_py} ] ; then
    echo "${grabndecode_plot_py} plotting script not found."
    echo "  You can set this manually using"
    echo "    export grabndecode_plot_py=full/path/to/plot.py"
    return 1
  fi
  if ! ssh -q ${grabndecode_origin} exit; then
    echo "Unable to connect to ${grabndecode_origin}."
    echo "  You can set the origin manually using"
    echo "    export grabndecode_origin=user@hostname"
    return 1
  fi
  return 0
}

grab-n-decode() {
  if [ -z $1 ]; then
    __grabndecode_help__
    return 0 
  fi

  local _file="$1"
  local _dest="${2:-"."}" #default is current

  local _rc=0
  local _oldpwd=$OLDPWD
  cd ${_dest}

  if ! scp ${grabndecode_origin}:${_file} . ; then
    echo "ERROR: Unable to download ${_file} from ${grabndecode_origin}."
    __grabndecode_return__ ${_oldpwd}
    return 2
  fi

  # update file name to just the basename since it is downloaded
  _file=$(basename ${_file})

  if ! ldmx fire ${grabndecode_decode_py} ${_file} ; then
    echo "ERROR: Unable to decode ${_file}."
    __grabndecode_return__ ${_oldpwd}
    return 3
  fi

  # update file name to the output of decode.py
  _file=adc_${_file//raw/root}

  if ! ldmx python3 ${grabndecode_plot_py} ${_file} ; then
    echo "ERROR: Unable to plot ${_file}."
    __grabndecode_return__ ${_oldpwd}
    return 4
  fi

  __grabndecode_return__
  return 0;
}

if ! hash ldmx &> /dev/null; then
  echo "ERROR: You are not in the ldmx computing environment! ('ldmx' is not available.)"
  return 1
fi

__grabndecode_deduce_configuration__
return $?
