#!/bin/bash

# determine if we're running on a Mac (specify specific version of
# gcc/g++ to avoid , or in a Travis CI VM
# (Travis CI defines TRAVIS=true)
if [[ $OSTYPE == darwin* ]]
then
  CPP=g++
  CC=gcc
#   CPP=g++-5
#   CC=gcc-5
else
  CPP=g++
  CC=gcc
fi

# Set the path to cxxtestgen depending on whether we're running under Travis or not
if env | grep -q ^TRAVIS=
then
  CXXTEST=/usr
else
  CXXTEST=/usr/local/cxxtest-4.4
fi
CXXTESTGEN=$CXXTEST/bin/cxxtestgen

echo
echo "Generating and compiling unit tests for image_io..."
$CXXTESTGEN --error-printer -o test_runner_imageio.cpp unit_tests/unittest_image_io.t.h 
$CPP -o test_runner_imageio test_runner_imageio.cpp core/image_io.cpp -I. -I/usr/local/include -Icore -I$CXXTEST -lcfitsio -lfftw3
if [ $? -eq 0 ]
then
  echo "Running unit tests for image_io:"
  ./test_runner_imageio
  exit
else
  echo "Compilation of unit tests for image_io.cpp failed."
  exit 1
fi
