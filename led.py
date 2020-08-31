from __future__ import print_function
from __future__ import division

import platform
import numpy as np
import settings


import neopixel
strip = neopixel.Adafruit_NeoPixel(settings.No_Of_Leds, settings.Led_Input_Pin,
                                       settings.Led_Refreash_Rate, settings.DMA_Channel,
                                       settings.Led_Inversion, settings.Max_Brightness)
strip.begin()

_gamma = np.load(settings.Gamma_Table_PATH)
"""Gamma lookup table used for nonlinear Max_Brightness correction"""

_prev_pixels = np.tile(253, (3, settings.No_Of_Leds))
"""Pixel values that were most recently displayed on the LED strip"""

pixels = np.tile(1, (3, settings.No_Of_Leds))
"""Pixel values for the LED strip"""

_is_python_2 = int(platform.python_version_tuple()[0]) == 2

def _update_pi():
    """Writes new LED values to the Raspberry Pi's LED strip

    Raspberry Pi uses the rpi_ws281x to control the LED strip directly.
    This function updates the LED strip with new values.
    """
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    # Optional gamma correction
    p = _gamma[pixels] if settings.Gamma_Correction else np.copy(pixels)
    # Encode 24-bit LED values in 32 bit integers
    r = np.left_shift(p[0][:].astype(int), 8)
    g = np.left_shift(p[1][:].astype(int), 16)
    b = p[2][:].astype(int)
    rgb = np.bitwise_or(np.bitwise_or(r, g), b)
    # Update the pixels
    for i in range(settings.No_Of_Leds):
        # Ignore pixels if they haven't changed (saves bandwidth)
        if np.array_equal(p[:, i], _prev_pixels[:, i]):
            continue
        strip._led_data[i] = rgb[i]
    _prev_pixels = np.copy(p)
    #print("It was in Led.py")
    strip.show()
