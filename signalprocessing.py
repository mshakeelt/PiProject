from __future__ import print_function
import numpy as np
import settings
from numpy import abs, append, arange, insert, linspace, log10, round, zeros



class ExpFilter:
    """Simple exponential smoothing filter"""
    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


def hertz_to_mel(freq):
    """Returns mel-frequency from linear frequency input """
    return 2595.0 * log10(1 + (freq / 700.0))


def mel_to_hertz(mel):
    """Returns frequency from mel-frequency input"""
    return 700.0 * (10**(mel / 2595.0)) - 700.0


def melfrequencies_mel_filterbank(num_bands, freq_min, freq_max, num_fft_bands):
    """Returns centerfrequencies and band edges for a mel filter bank """

    mel_max = hertz_to_mel(freq_max)
    mel_min = hertz_to_mel(freq_min)
    delta_mel = abs(mel_max - mel_min) / (num_bands + 1.0)
    frequencies_mel = mel_min + delta_mel * arange(0, num_bands + 2)
    lower_edges_mel = frequencies_mel[:-2]
    upper_edges_mel = frequencies_mel[2:]
    center_frequencies_mel = frequencies_mel[1:-1]
    return center_frequencies_mel, lower_edges_mel, upper_edges_mel


def compute_melmat(num_mel_bands=12, freq_min=64, freq_max=8000,
                   num_fft_bands=513, sample_rate=16000):
    """Returns tranformation matrix for mel Frequencies"""
    center_frequencies_mel, lower_edges_mel, upper_edges_mel =  \
        melfrequencies_mel_filterbank(
            num_mel_bands,
            freq_min,
            freq_max,
            num_fft_bands
        )

    center_frequencies_hz = mel_to_hertz(center_frequencies_mel)
    lower_edges_hz = mel_to_hertz(lower_edges_mel)
    upper_edges_hz = mel_to_hertz(upper_edges_mel)
    freqs = linspace(0.0, sample_rate / 2.0, num_fft_bands)
    melmat = zeros((num_mel_bands, num_fft_bands))

    for imelband, (center, lower, upper) in enumerate(zip(
            center_frequencies_hz, lower_edges_hz, upper_edges_hz)):

        left_slope = (freqs >= lower) == (freqs <= center)
        melmat[imelband, left_slope] = (
            (freqs[left_slope] - lower) / (center - lower)
        )

        right_slope = (freqs >= center) == (freqs <= upper)
        melmat[imelband, right_slope] = (
            (upper - freqs[right_slope]) / (upper - center)
        )

    return melmat, (center_frequencies_mel, freqs)






def Create_Mel_Bank():
    global samples, mel_y, mel_x
    samples = int(settings.Mic_Rate * settings.No_Of_Rolling_History / (2.0 * settings.FPS))
    mel_y, (_, mel_x) = compute_melmat(num_mel_bands=settings.No_Of_FFT_Bins,
                                               freq_min=settings.Min_Frequency,
                                               freq_max=settings.Max_Frequency,
                                               num_fft_bands=samples,
                                               sample_rate=settings.Mic_Rate)
    
samples = None
mel_y = None
mel_x = None
Create_Mel_Bank()
