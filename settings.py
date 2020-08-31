from __future__ import print_function
from __future__ import division
import os

Led_Input_Pin = 18
"""GPIO pin connected to the LED strip pixels"""

Led_Refreash_Rate = 800000
"""LED signal frequency in Hz (usually 800kHz)"""

DMA_Channel = 5
"""DMA channel used for generating PWM signal"""

Max_Brightness = 255
"""Maximum Brightness of a single LED"""

Led_Inversion = False

No_Of_Leds = 144
"""Number of LEDs in the LED strip"""

Mic_Rate = 48000
"""Sampling frequency of the microphone in Hz"""

FPS = 50
"""Desired refresh rate of the visualization (frames per second)"""


Min_Frequency = 500
"""Frequencies below this value will be removed during audio processing"""

Max_Frequency = 16000
"""Frequencies above this value will be removed during audio processing"""

No_Of_FFT_Bins = 24
"""Number of frequency bins to use when transforming audio to frequency domain"""

No_Of_Rolling_History = 2
"""Number of past audio frames to include in the rolling window"""

Min_Volume_Threshold = 1e-7
"""No music visualization displayed if recorded audio volume below threshold"""
