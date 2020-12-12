## create python wildlife environment
```
conda create --name wildlife python=3.8

source activate wildlife
```

conda install -c auto picamera

## install opencv on ubuntu 18.04
```
conda install -c conda-forge opencv=4.1.0
conda install -c conda-forge imutils
```

#install raspberry pi
## install conda environment and opencv
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

