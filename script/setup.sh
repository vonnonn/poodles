#!/bin/bash

# Sets up a Vonn Nonn Digital Terrain Model filter in a
# Debian-based environment on an x86-64 machine
# using Miniconda (because Conda, as opposed to
# Python venv, has well-maintained packages for PDAL
# provided by the PDAL development team).
# Originally built and tested on Ubuntu 20.04 

echo checking if Conda is installed
if ! type "conda"; then
    echo Conda is not installed, attempting install now
    mkdir -p miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3/miniconda.sh
    bash miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf miniconda3/miniconda.sh
    miniconda3/bin/conda init bash
else echo Conda seems to be already installed, attempting update
     conda update -y conda
fi


echo checking if vonnonn environmnet already installed

echo checking if envs folder already created
if [ ! -d "envs" ]; then
    echo creating project environment with PDAL
    conda create -y --prefix ./envs --channel conda-forge python-pdal scipy pandas
else echo Looks like the Conda envs directory is already present
fi

echo You can probably now use the Von Nonn filter. First, activate the Conda environment with
echo
echo *********************
echo conda activate ./envs
echo *********************
echo
echo then
echo
echo *************************************
echo python3 app/dtm_filter.py <inputfile>
echo *************************************
echo
