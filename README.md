# ufscar-mba-machine-learning-tcc
TCC de Machine Learning - UFSCar MBA

#Referencias
https://machinelearningmastery.com/how-to-train-an-object-detection-model-with-keras/
https://machinelearningmastery.com/how-to-perform-object-detection-with-yolov3-in-keras/
https://keras.io/examples/vision/retinanet/


https://www.youtube.com/watch?v=Sx_HioMUtiY
https://www.youtube.com/watch?v=8L3PCqADFPo


!!cool
https://www.youtube.com/watch?v=xhdNV5VYdGM
https://github.com/arunponnusamy/cvlib
https://www.youtube.com/watch?v=uoh1ssohiXU

#Raspberry PI


```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```

```
sudo apt-get update --allow-releaseinfo-change

sudo apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 python3-dev -y

sudo apt-get install qt-sdk 
sudo apt-get install libssl-dev
```

```
sudo pip3 install virtualenv
virtualenv venv
```

```
source venv/bin/activate
pip3 install -r requirements.txt
```

https://egemenertugrul.github.io/blog/Darknet-NNPACK-on-Raspberry-Pi/
https://github.com/digitalbrain79/darknet-nnpack
https://github.com/mrhosseini/NNPACK-darknet


avoid ninja https://github.com/digitalbrain79/darknet-nnpack/issues/60

mkdir build
cd build
cmake -G "Unix Makefiles" ..
make

opencv-python==4.5.5.64
opencv-contrib-python==4.5.5.64
opencv-python-headless==4.5.5.64

https://pytorch.org/tutorials/intermediate/realtime_rpi.html