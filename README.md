# Visualization of Realtime Sound Frequency and Intensity using Raspberry Pi 3B+ and WS2812b LED Strip
This repository contains the fork of scot lawson library of audio reactive led strip. I have implemented the library with multiprocessing and GPIO inputs.
GPIO pins are connected with the pushbutton to change the visualization from frequency to intensity and vice versa. 

# Required Hardware
* Raspberry Pi 3B+
* USB Microphone
* Individually Addressable LED Strip (WS2812b)
* Strip case (optional)
* Breadboard + connectors
* Push Buttons
* Some Resistors and Capacitors for Debouncing Circuit for Push Buttons

# Required Libraries
* pyaudio
* neopixel
* numpy
* scipy
* sys
* multiprocessing
* RPi.GPIO
* platform

# Usage
python main.py frequency
or 
python main.py intensity

# Multiprocessing Block Diagram
With the device bootup the raspberrypi starts waiting for the GPIO input. When user push a button connected to GPIO pin then update function gets called and corresponsing visualization gets displayed on the led strip as a separate process. So one process checks on the GPIO pins and other takes the audio input and create a display on the led strip. 
![multiprocessing](https://github.com/mshakeelt/Sound_Visualizer_Using_RaspberryPi/blob/master/images/Process%20Block%20Diagram.JPG)

# Device Flow Diagram
Here is the device flow diagram when tells how push buttons are communicating with the raspberrypi.
![Device Flow](https://github.com/mshakeelt/Sound_Visualizer_Using_RaspberryPi/blob/master/images/Device%20Flow%20Diagram.JPG)

# Visualizations
Here are some examplary visualizations.
![visualizations](https://github.com/mshakeelt/Sound_Visualizer_Using_RaspberryPi/blob/master/images/Frequency%20and%20Intensity%20Testing.JPG)

# Reference
https://github.com/scottlawsonbc/audio-reactive-led-strip
# Setup Tutorial without Push Buttons and Multiprocessing
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/FA9rMkuVmvQ/0.jpg)](http://www.youtube.com/watch?v=FA9rMkuVmvQ)
