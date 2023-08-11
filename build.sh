#!/bin/bash

rm -rf build
mkdir build
cd build
meson -Dprefix=$PWD/build/testdir ..
