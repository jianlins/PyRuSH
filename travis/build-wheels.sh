#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y atlas-devel
ARGS=("$@")

PLAT=${ARGS[0]}
PROJECT_NAME=${ARGS[1]}
PYBIN=${ARGS[2]}
if [ $PYBIN ==  3.5 ]; then
  PYBIN='cp35-cp35m'
elif [ $PYBIN ==  3.8 ]; then
  PYBIN='cp38-cp38'
elif [ $PYBIN ==  3.7 ]; then
  PYBIN='cp37-cp37m'
#  sudo apt-get install libssl-dev
else
  PYBIN='cp36-cp36m'
fi

# Compile wheels
which python
PYBIN="/opt/python/${PYBIN}/bin"
echo "PYBIN:$PYBIN"
"${PYBIN}/pip" install -q -r /io/dev-requirements.txt
"${PYBIN}/pip" wheel /io/ -w wheelhouse/

pwd
ls wheelhouse -l
[ ! -d "/io/wheelhouse/" ] && mkdir /io/wheelhouse/
# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    if [[ $whl == wheelhouse/${PROJECT_NAME}* ]]; then
      if [[ $whl == wheelhouse/*linux* ]]; then
        auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/;
      else
        cp $whl /io/wheelhouse;
        ls /io -l;
        ls /io/wheelhouse -l;
      fi
    else
      rm $whl
    fi
done

ls /io/wheelhouse -l
"${PYBIN}/pip" install -q /io/wheelhouse/${PROJECT_NAME}*
(cp -R /io/tests "$HOME"/tests; cd "$HOME"; ls tests; "${PYBIN}/nosetests" tests;)
# Install packages and test
