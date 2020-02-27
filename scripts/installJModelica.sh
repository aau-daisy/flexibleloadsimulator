#!/bin/bash
###################################################################################################
#
# Original Author: Cristian Di Pietrantonio (https://github.com/Halolegend94)
# Adapted By: Muhammad Aftab (https://github.com/muhaftab)
#
# Description: Install easly the last version of JModelica.
# ATTENTION: set manually the requested variables in "manual setting" section before launching this
# Script.
#
###################################################################################################

###################################################################################################
#
#                                  !! MANUAL SETTINGS !!
# Set the instalation path

if [ $# -eq 0 ]
  then
    echo "Must provide a path where JModelica will be installed"
    exit
fi

DIR=${1%/}
if [[ ! -d ${DIR} ]]; then
   echo ${DIR} is not a directory
else
   echo Installing to ${DIR}/JModelica
fi


InstallLocation=${DIR}/JModelica
JMODELICA_HOME=${InstallLocation}

# Set path containing HSL download. You can download it at
# http://www.hsl.rl.ac.uk/download/coinhsl-archive-linux-x86_64/2014.01.17/
COINHSL=$(pwd)/coinhsl-archive-linux-x86_64-2014.01.17.tar.gz

###################################################################################################
## NOTE: Oracle Java 8 is needed (use the following commands to install 
## if not already installed
###################################################################################################
pkg=oracle-java8-installer
if sudo apt -qq install $pkg; then
    echo "$pkg already installed"
else
  echo "$pkg not installed. Installing now"
  sudo add-apt-repository --remove ppa:webupd8team/java -y
  sudo add-apt-repository ppa:webupd8team/java -y
  sudo apt update -y
  # if you get error, run the next command
  # sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C2518248EEA14886
  sudo apt install oracle-java8-installer -y
  sudo apt install oracle-java8-set-default -y
  oracle-java8-set-default

fi

###################################################################################################
#                                   SCRIPT STARTS HERE
###################################################################################################

###install dependencies
sudo apt -y install g++
sudo apt -y install subversion
sudo apt -y install gfortran
sudo apt -y install ipython
sudo apt -y install cmake
sudo apt -y install swig
sudo apt -y install ant
sudo apt -y install python-dev
sudo apt -y install python-numpy
sudo apt -y install python-scipy
sudo apt -y install python-matplotlib
sudo apt -y install python-lxml
sudo apt -y install python-nose
sudo apt -y install python-jpype
sudo apt -y install python-pip
sudo apt -y install cython
sudo apt -y install curl
sudo apt -y install libboost-dev
sudo apt -y install default-jdk
pip install JCC # if you get error, install oracle java (see above)
pip install cython

#
if ! [ -d $InstallLocation ]; then
   mkdir $InstallLocation
fi
if ! [ -d $InstallLocation/tmpBuild ]; then
   mkdir $InstallLocation/tmpBuild
fi
cd $InstallLocation/tmpBuild

########################################################################
##
##                       IPOPT
##
########################################################################

#now get the last version of Ipopt from internet, by parsing its official page
VER=3.12.9
wget https://www.coin-or.org/download/source/Ipopt/Ipopt-$VER.tgz
tar -xvf Ipopt-$VER.tgz

#get external dependencies
cd Ipopt-$VER/ThirdParty/Blas
./get.Blas
cd ../Lapack
./get.Lapack
cd ../ASL
./get.ASL
cd ../Mumps
./get.Mumps
cd ../Metis
./get.Metis
cd ../HSL
tar xaf $COINHSL --strip-components 0 # see INSTALL.HSL for instruction on how to add coinhsl
cd ../../
mkdir build
cd build
../configure --prefix=$InstallLocation/CoinIpoptBuild
if [[ $? != 0 ]]; then
   echo "Error configure Ipopt!"
   exit 1
fi
make
if [[ $? != 0 ]]; then
   echo "Error make ipopt!"
   exit 1
fi

make install
if [[ $? != 0 ]]; then
   echo "Error make install ipopt!"
   exit 1
fi
cd ../..

#OK, now install JMODELICA
svn co https://svn.jmodelica.org/trunk JMSrc # get last version of jmodelica
#svn co https://svn.jmodelica.org/tags/2.1 JMSrc # get version 2.1
cd JMSrc
svn checkout https://svn.jmodelica.org/assimulo/trunk external/Assimulo
mkdir build
cd build
../configure --prefix=$InstallLocation --with-ipopt=$InstallLocation/CoinIpoptBuild
make
if [[ $? != 0 ]]; then
   echo "Error make jmodelica!"
   exit 1
fi
make install
if [[ $? != 0 ]]; then
   echo "Error make install jmodelica!"
   exit 1
fi
make casadi_interface
if [[ $? != 0 ]]; then
   echo "Error make casadi_interface!"
   exit 1
fi

echo "Post Installation..."
# Before you can use jmodelica modules in python, the environment variables 
# from $InstallLocation/bin/jm_python.sh have to be appended to $HOME/.bashrc
tee -a $HOME/.profile << END

# JModelica
export JAVA_HOME=/usr/lib/jvm/java-8-oracle
export JMODELICA_HOME=$JMODELICA_HOME
export IPOPT_HOME=\$JMODELICA_HOME/CoinIpoptBuild
export SUNDIALS_HOME=\$JMODELICA_HOME/ThirdParty/Sundials
export PYTHONPATH=\$PYTHONPATH:\$JMODELICA_HOME/Python
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$IPOPT_HOME/lib:\$SUNDIALS_HOME/lib:\$JMODELICA_HOME/ThirdParty/CasADi/lib
export SEPARATE_PROCESS_JVM=/usr/lib/jvm/java-8-oracle
END
# if the following command doesnot work, then logoff the logon or restart
source $HOME/.profile

## clean-up
cd ../../..
rm -rf tmpBuild

#########
# Note 1.
#########
# if you get an error like below (I got it in Ubuntu 17.10):

#  File "/usr/lib/python2.7/xml/sax/expatreader.py", line 235, in _close_source
#      file.close()
#      AttributeError: KeepLastStream instance has no attribute 'close'
#
# to fix this problem add the following method to KeepLastStream class in
# <jmodelica_install_directory>/Python/pymodelica/compiler_logging.py
#
#    def close(self):
#        self.stream.close()
#
# Reference: http://www.jmodelica.org/27909
