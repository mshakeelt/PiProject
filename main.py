from __future__ import print_function
from __future__ import division
import time
import pyaudio
from neopixel import *
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import settings
import signalprocessing
import led
import sys
from os import sys
from multiprocessing import Process,Queue
import RPi.GPIO as GPIO
import os


visType = sys.argv[1]


def _normalized_linspace(size):
    return np.linspace(0, 1, size)


def interpolate(y, new_length):
    """Intelligently resizes the array by linearly interpolating the values"""
    if len(y) == new_length:
        return y
    x_old = _normalized_linspace(len(y))
    x_new = _normalized_linspace(new_length)
    z = np.interp(x_new, x_old, y)
    return z


r_filt = signalprocessing.ExpFilter(np.tile(0.01, settings.No_Of_Leds // 2),
                       alpha_decay=0.2, alpha_rise=0.99)
g_filt = signalprocessing.ExpFilter(np.tile(0.01, settings.No_Of_Leds // 2),
                       alpha_decay=0.05, alpha_rise=0.3)
b_filt = signalprocessing.ExpFilter(np.tile(0.01, settings.No_Of_Leds // 2),
                       alpha_decay=0.1, alpha_rise=0.5)
common_mode = signalprocessing.ExpFilter(np.tile(0.01, settings.No_Of_Leds // 2),
                       alpha_decay=0.99, alpha_rise=0.01)
p_filt = signalprocessing.ExpFilter(np.tile(1, (3, settings.No_Of_Leds // 2)),
                       alpha_decay=0.1, alpha_rise=0.99)
p = np.tile(1.0, (3, settings.No_Of_Leds // 2))
gain = signalprocessing.ExpFilter(np.tile(0.01, settings.No_Of_FFT_Bins),
                     alpha_decay=0.001, alpha_rise=0.99)

fft_plot_filter = signalprocessing.ExpFilter(np.tile(1e-1, settings.No_Of_FFT_Bins),
                         alpha_decay=0.5, alpha_rise=0.99)
mel_gain = signalprocessing.ExpFilter(np.tile(1e-1, settings.No_Of_FFT_Bins),
                         alpha_decay=0.01, alpha_rise=0.99)
mel_smoothing = signalprocessing.ExpFilter(np.tile(1e-1, settings.No_Of_FFT_Bins),
                         alpha_decay=0.5, alpha_rise=0.99)
volume = signalprocessing.ExpFilter(settings.Min_Volume_Threshold,
                       alpha_decay=0.02, alpha_rise=0.02)
fft_window = np.hamming(int(settings.Mic_Rate / settings.FPS) * settings.No_Of_Rolling_History)
prev_fps_update = time.time()


def start_stream(q,callback):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(settings.Mic_Rate / settings.FPS)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=settings.Mic_Rate,
                    input=True,
                    frames_per_buffer=frames_per_buffer)
    overflows = 0
    prev_ovf_time = time.time()
    #def test
    while True:
        try:
            y = np.fromstring(stream.read(frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
            y = y.astype(np.float32)
            callback(y)
           
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    
    stream.stop_stream()
    stream.close()
    p.terminate()

# Number of audio samples to read every time frame
samples_per_frame = int(settings.Mic_Rate / settings.FPS)

# Array containing the rolling audio sample window
y_roll = np.random.rand(settings.No_Of_Rolling_History, samples_per_frame) / 1e16

def microphone_update(audio_samples):
    global y_roll, prev_rms, prev_exp, prev_fps_update
    #print("Audio Samples in microphone update")
    # Normalize samples between 0 and 1
    y = audio_samples / 2.0**15
    # Construct a rolling window of audio samples
    y_roll[:-1] = y_roll[1:]
    y_roll[-1, :] = np.copy(y)
    y_data = np.concatenate(y_roll, axis=0).astype(np.float32)
    
    vol = np.max(np.abs(y_data))
    if vol < settings.Min_Volume_Threshold:
        print('No audio input. Volume below threshold. Volume:', vol)
        led.pixels = np.tile(0, (3, settings.No_Of_Leds))
        led._update_pi()
    else:
        # Transform audio input into the frequency domain
        N = len(y_data)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N
        # Pad with zeros until the next power of two
        y_data *= fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * signalprocessing.mel_y.T
        # Scale data to values more suitable for output
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= mel_gain.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip
        output = output_effect(mel)
        led.pixels = output
        led._update_pi()


if sys.argv[1] == "frequency":
        output_effect = output_frequency
elif sys.argv[1] == "intensity":
        output_effect = output_intensity  


def output_intensity(y):
    """Effect that expands from the center with increasing sound intensity"""
    global p
    y = np.copy(y)
    gain.update(y)
    y /= gain.value
    # Scale by the width of the LED strip
    y *= float((settings.No_Of_Leds // 2) - 1)
    # Map color channels according to intensity in the different freq bands
    scale = 0.9
    r = int(np.mean(y[:len(y) // 3]**scale))
    g = int(np.mean(y[len(y) // 3: 2 * len(y) // 3]**scale))
    b = int(np.mean(y[2 * len(y) // 3:]**scale))
    # Assign color to different frequency regions
    p[0, :r] = 255.0
    p[0, r:] = 0.0
    p[1, :g] = 255.0
    p[1, g:] = 0.0
    p[2, :b] = 255.0
    p[2, b:] = 0.0
    p_filt.update(p)
    p = np.round(p_filt.value)
    # Apply substantial blur to smooth the edges
    p[0, :] = gaussian_filter1d(p[0, :], sigma=4.0)
    p[1, :] = gaussian_filter1d(p[1, :], sigma=4.0)
    p[2, :] = gaussian_filter1d(p[2, :], sigma=4.0)
    # Set the new pixel value
    return np.concatenate((p[:, ::-1], p), axis=1)


_prev_frequency = np.tile(0.01, settings.No_Of_Leds // 2)


def output_frequency(y):
    """Effect that maps the Mel filterbank frequencies onto the LED strip"""
    global _prev_frequency
    y = np.copy(interpolate(y, settings.No_Of_Leds // 2))
    common_mode.update(y)
    diff = y - _prev_frequency
    _prev_frequency = np.copy(y)
    # Color channel mappings
    r = r_filt.update(y - common_mode.value)
    g = np.abs(diff)
    b = b_filt.update(np.copy(y))
    # Mirror the color channels for symmetric output
    r = np.concatenate((r[::-1], r))
    g = np.concatenate((g[::-1], g))
    b = np.concatenate((b[::-1], b))
    output = np.array([r, g,b]) * 255
    return output


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(144):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)    



if __name__ == '__main__':
    
    strip = Adafruit_NeoPixel(settings.No_Of_Leds, settings.Led_Input_Pin, settings.Led_Refreash_Rate, 10, settings.Led_Inversion, settings.Max_Brightness, 0)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    led._update_pi()
    
    q = Queue()
    process1 = Process(target=start_stream,args=(q,microphone_update))
    process1.start()
    print("Process Started")
    
    
    while True:
        if GPIO.input(21)== GPIO.LOW:
            time.sleep(0.5)
            print("Pin 21 Pressed, Stop the Process")
            if process1.is_alive():
                process1.terminate()
            strip.begin()
            print("Before Color Wipe")
            colorWipe(strip, Color(0,0,0), 10)
            print("After Color Wipe")
            print("intensity is Running from main")
            
            os.system("sudo python /home/pi/Desktop/Pyproject/dancyPi-audio-reactive-led/python/main.py intensity")
            
        
        elif GPIO.input(16)== GPIO.LOW:
            time.sleep(0.5)
            print("Pin 16 Pressed, Stop the Process")
            if process1.is_alive():
                process1.terminate()
            
            strip.begin()
            print("Before Color Wipe")
            colorWipe(strip, Color(0,0,0), 10)
            print("After Color Wipe")
            print("frequency is Running from main")
            
            os.system("sudo python /home/pi/Desktop/Pyproject/dancyPi-audio-reactive-led/python/main.py frequency")
            

        elif GPIO.input(20)== GPIO.LOW:
            time.sleep(0.5)
            print("Pin 20 Pressed, Turning Off the lights")
            
            if process1.is_alive():
                process1.terminate()
                print("Process Terminated")
        
                
                
            strip.begin()
            print("Before Color Wipe")
            colorWipe(strip, Color(0,0,0), 10)
            print("After Color Wipe")
            print("Waiting for new Command")
            
    
            
            break
            
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    time.sleep(1)
    print("Pins has been reset")
    print("Press 21 to Visualize intensity, 16 to visualize Frequency, or press 20 to Keep it Off")
    
