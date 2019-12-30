#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y atlas-devel
ARGS=("$@")

PLAT=${ARGS[0]}

PYBINS=${ARGS[@]:1}
# Compile wheels
for PYBIN in PYBINS;do
  PYBIN=/opt/python/${PYBIN}/bin
  echo ${PYBIN}
  "${PYBIN}/pip" install -r /io/dev-requirements.txt
  "${PYBIN}/python" -m spacy download en
  "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/
done

# Install packages and test
for PYBIN in ${PYBINS}; do
    PYBIN=/opt/python/${PYBIN}/bin
    "${PYBIN}/pip" install python-manylinux-demo --no-index -f /io/wheelhouse
    (cd "$HOME"; "${PYBIN}/nosetests" PyRuSH)
done