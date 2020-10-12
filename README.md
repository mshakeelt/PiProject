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

# Reference
https://github.com/scottlawsonbc/audio-reactive-led-strip
# Setup Tutorial without Push Buttons and Multiprocessing
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/FA9rMkuVmvQ/0.jpg)](http://www.youtube.com/watch?v=FA9rMkuVmvQ)
