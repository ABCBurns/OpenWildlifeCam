# Setup Development Host for Wildlife Project

## Create Python conda environment
```
conda create --name wildlife python=3.8
source activate wildlife

conda install -c conda-forge opencv=4.1.0
conda install -c conda-forge imutils
```

# Setup Raspberry Pi 2 for Wildlife Project
## Solution 1: Install conda environment with precompiled opencv on raspberry pi
```
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
chmod 755 Miniconda3-latest-Linux-armv7l.sh
./Miniconda3-latest-Linux-armv7l.sh

conda create --name wildlife python=3.4

# install precompiled opencv on raspberry
# https://github.com/ctrlfizz/raspiquickcv2/blob/master/opencv.sh
conda config --add channels "microsoft-ell"
sudo apt install -y libjasper1
conda install -y -c microsoft-ell/label/stretch opencv
pip install imutils
pip install picamera

source activate wildlife
```

## Solution 2: Compile and install opencv on raspberry pi 2
```
// updating and upgrading installed packages
sudo apt-get update
sudo apt-get upgrade
sudo rpi-updat

// set python3 as default and install necessary modules
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
pip3 install numpy
pip3 install picamera
pip3 install imutils

// Install the required developer tools and packages
sudo apt-get install build-essential cmake pkg-config

// Install the necessary image I/O packages.
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

// Install the necessary video I/O packages.
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

// Install libraries  additional OpenCV dependencies
sudo apt-get install libatlas-base-dev gfortran

// download and unzip opencv
cd ~/Downloads
wget -O opencv-3.4.3.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/3.4.3/opencv-3.4.3.zip/download
unzip opencv-3.4.3.zip

// compile opencv
cd opencv-3.4.3/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON  -D BUILD_EXAMPLES=ON ..
make

// install opencv
sudo make install
sudo ldconfig
```

