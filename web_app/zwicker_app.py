import streamlit as st
import numpy as np
from scipy import fft
import matplotlib.pyplot as plt

T = 60

def get_normalized_white_noise(sampling_frequency):
    white_noise = np.random.normal(size = (T*sampling_frequency))
    white_noise /= np.max(abs(white_noise))
    return white_noise

def apply_band_stop_filter(signal, sample_rate, low_pass, high_pass):
    ft = fft.rfft(signal)
    freq = fft.rfftfreq(signal.size, d = 1/sample_rate)

    band = (freq >= low_pass) * (freq <= high_pass)
    ft[band] = 0

    return fft.irfft(ft)

st.title("The Zwicker Tone")

sampling_frequency = st.number_input("Sampling Frequency (Hz)", min_value=1, max_value=352_800, value=44_100)
effect_type = st.selectbox("Type", ["Monaural","Binaural", "Alternating Silence"])

if effect_type == "Binaural":
    n_channels = 2
    slider_ranges = [st.slider(f"Band-stop Filter for channel {channel + 1} (Hz)", 
                            min_value = 0, 
                            max_value=sampling_frequency//2, 
                            value=[2_200, 3_300],
                            step=100) for channel in range(n_channels)]
    signal = np.stack([apply_band_stop_filter(get_normalized_white_noise(sampling_frequency), 
                                         sampling_frequency, 
                                         slider_ranges[i][0], 
                                         slider_ranges[i][1]) 
                                         for i in range(n_channels)])
    
    fig, ax = plt.subplots(2, 2)
    fig.set_figheight(10)
    fig.set_figwidth(20)

    time = np.arange(0, T, 1/sampling_frequency)

    ax[0][0].plot(time, signal[0])
    ax[0][0].set_title("Channel 1 Audioform")
    ax[0][0].set_ylabel("Amplitude")
    ax[0][0].set_xlabel("Time (s)")

    ax[0][1].plot(time, signal[1])
    ax[0][1].set_title("Channel 2 Audioform")
    ax[0][1].set_ylabel("Amplitude")
    ax[0][1].set_xlabel("Time (s)")

    ax[1][0].specgram(signal[0], Fs = sampling_frequency)
    ax[1][0].set_title("Channel 1 Spectrograph")
    ax[1][0].set_ylabel("Frequency (Hz)")
    ax[1][0].set_xlabel("Time (s)")
    
    ax[1][1].specgram(signal[1], Fs = sampling_frequency)
    ax[1][1].set_title("Channel 2 Spectrograph")
    ax[1][1].set_ylabel("Frequency (Hz)")
    ax[1][1].set_xlabel("Time (s)")
    st.pyplot(fig)
else:
    n_channels = 1
    slider_range = st.slider(f"Band-stop Filter (Hz)", 
                             min_value = 0, 
                             max_value=sampling_frequency//2, 
                             value=[2_200, 3_300],
                             step=100) 
    if effect_type == "Alternating Silence":
        noise_interval = st.number_input("Noise Interval Duration (ms)", 0, T*1000, value=500)
        noise_samples= int(noise_interval/1000 * sampling_frequency)

        silence_interval = st.number_input("Silence Interval Duration (ms)", 0, T*1000, value=500)
        silence_samples = int(silence_interval/1000 * sampling_frequency)

        signal = apply_band_stop_filter(get_normalized_white_noise(sampling_frequency), 
                                            sampling_frequency, 
                                            slider_range[0], 
                                            slider_range[1])
        i = 0 
        while i*(noise_interval + silence_interval) < T*sampling_frequency:
            signal[noise_samples*i+silence_samples*i:noise_samples*i + silence_samples*(i+1)] = 0
            i+= 1

        fig, ax = plt.subplots(2, 1)
        fig.set_figheight(10)
        fig.set_figwidth(20)

        time = np.arange(0, T, 1/sampling_frequency)
        ax[0].plot(time, signal)
        ax[0].set_title("Audioform")
        ax[0].set_ylabel("Amplitude")
        ax[0].set_xlabel("Time (s)")

        ax[1].specgram(signal, Fs = sampling_frequency)
        ax[1].set_title("Spectrograph")
        ax[1].set_ylabel("Frequency (Hz)")
        ax[1].set_xlabel("Time (s)")
        st.pyplot(fig)

    elif effect_type == "Monaural":

        signal = apply_band_stop_filter(get_normalized_white_noise(sampling_frequency), 
                                            sampling_frequency, 
                                            slider_range[0], 
                                            slider_range[1])

        fig, ax = plt.subplots(2, 1)
        fig.set_figheight(10)
        fig.set_figwidth(20)

        time = np.arange(0, T, 1/sampling_frequency)
        ax[0].plot(time, signal)
        ax[0].set_title("Audioform")
        ax[0].set_ylabel("Amplitude")
        ax[0].set_xlabel("Time (s)")

        ax[1].specgram(signal, Fs = sampling_frequency)
        ax[1].set_title("Spectrograph")
        ax[1].set_ylabel("Frequency (Hz)")
        ax[1].set_xlabel("Time (s)")
        st.pyplot(fig)



st.audio(signal, sample_rate=sampling_frequency)