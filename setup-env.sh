if test -z "${BASH_SOURCE%*/*}"
then
    CNUCNU_BASEDIR="${BASH_SOURCE%/*}"
else
    CNUCNU_BASEDIR="."
fi

export PYTHONPATH=${CNUCNU_BASEDIR:-${PWD}}/lib

#echo "new PYTHONPATH: ${PYTHONPATH}"
