# Setup Development Host for Wildlife Project

## Create Python conda environment
```
conda create --name wildlife python=3.8
source activate wildlife

conda install -c conda-forge opencv=4.1.0
conda install -c conda-forge imutils
// conda install -c conda-forge python-telegram-bot
pip install telepot
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
pip install telepot

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
pip3 install telepot

// Install the required developer tools and packages
sudo apt-get install build-essential cmake pkg-config

// Install the necessary image I/O packages.
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

// Install the necessary video I/O packages.
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

// Install libraries  additional OpenCV dependencies
sudo apt-get install libatlas-base-dev gfortran

// Optional: If you want to show the videos on the raspberry
sudo apt-get install libgtk2.0-dev

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

# Start WildLife 
```
// start software on development host
./wildlife.py -c config.json

// start software on raspberry pi
./wildlife.py -c config_pi.json
```
# The WildLife Config
```
// codecs
{
    "system" : "dev-host",
    "show_video": true,
    "store_video": true,
    "store_codec": "mp4v",                // encoding format (e.g. x264, h264, mp4v)
    "store_path": "./videostore",
    "store_activity_count_threshold": 50,
    "motion_detection": true,             // enable/disable motion detection
    "motion_rectangle": true,             // enable/disable rectangle around motion area
    "clean_store_on_startup": true,
    "delta_threshold": 5,
    "resolution": [
        640,
        480
    ],
    "fps": 30,
    "motion_detection_width": 300,        // width of the input frame for the motion detction
    "min_area": 400,
    "min_recording_time_seconds": 10
}
```

