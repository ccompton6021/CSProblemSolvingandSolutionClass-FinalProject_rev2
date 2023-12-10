# Import statements
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.signal import spectrogram, find_peaks
from project_model import Model

def calculate_rt60(model, spectrogram_data, decay_percentage=60):
    """
    Calculate RT60 using the decay threshold method

    Parameters:
    - spectrogram_data: 2D array representing the spectrogram
    - decay_percentage: Percentage threshold for decay (default: 60%)

    Returns:
    - rt60_values: 1D array of RT60 values for each channel
    """
    # Find the maximum value in each frequency bin for each channel
    max_amplitudes = np.max(spectrogram_data, axis=1)

    # Calculate the decay threshold as a percentage of the maximum amplitude for each channel
    decay_threshold = max_amplitudes * (decay_percentage / 100.0)

    # Initialize an array to store decay indices for each channel
    decay_indices = np.zeros(spectrogram_data.shape[0], dtype=int)

    # Iterate over channels and find the time indices where the amplitude falls below the decay threshold
    for i in range(spectrogram_data.shape[0]):
        decay_indices[i] = np.argmax(spectrogram_data[i] < decay_threshold[i])

    # Calculate the RT60 values based on the time indices
    rt60_values = decay_indices / model.sample_rate

    return rt60_values

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Analyzer")

        # Load button
        self.load_button = tk.Button(root, text="Load file", command=self.load_file)
        self.load_button.pack()

        # Display file name
        self.file_label = tk.Label(root, text="")
        self.file_label.pack()

        # Display time value
        self.time_label = tk.Label(root, text="")
        self.time_label.pack()

        # Plot canvas
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

        # Analyze button
        self.analyze_button = tk.Button(root, text="Analyze", command=self.analyze_audio)
        self.analyze_button.pack()

    def load_file(self, model):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3;*.aac")])
        if file_path:
            model.load_file(file_path)
            self.file_label.config(text=f"File: {model.filename}")
            self.plot_waveform()

    def plot_waveform(self, model):
        if model.audio_data is not None:
            self.ax.clear()
            time = np.arange(0, len(model.audio_data)) / model.sample_rate
            self.ax.plot(time, model.audio_data, color='b')
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Amplitude')
            self.canvas.draw()

    def analyze_audio(self, model):
        if model.audio_data is not None:
            num_channels = model.audio_data.shape[1] if len(model.audio_data.shape) > 1 else 1

            # Calculate spectrogram
            f, t, Sxx = spectrogram(model.audio_data.T, model.sample_rate, axis=0)

            # Find peak frequency
            peak_freq_index = np.unravel_index(np.argmax(Sxx), Sxx.shape)
            peak_freq = f[peak_freq_index[0]]

            # Calculate RT60 for low, mid, and high frequencies
            low_freq_mask = (f >= 20) & (f < 500)
            mid_freq_mask = (f >= 500) & (f < 2000)
            high_freq_mask = (f >= 2000) & (f <= 10000)

            rt60_low = calculate_rt60(model, Sxx[low_freq_mask, :])
            rt60_mid = calculate_rt60(model, Sxx[mid_freq_mask, :])
            rt60_high = calculate_rt60(model, Sxx[high_freq_mask, :])

            # Display results
            self.time_label.config(text=f"Duration: {len(model.audio_data) / model.sample_rate:.2f} seconds")
            self.show_peak_frequency(peak_freq, model)
            self.show_rt60_values(rt60_low, rt60_mid, rt60_high)

    def show_peak_frequency(self, peak_freq, model):
        # Display peak frequency
        self.file_label.config(text=f"File: {model.filename} | Peak Frequency: {peak_freq:.2f} Hz")

    def show_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        # Calculate the mean of the arrays
        rt60_low_scalar = np.mean(rt60_low) if np.any(rt60_low) else 0.0
        rt60_mid_scalar = np.mean(rt60_mid) if np.any(rt60_mid) > 0 else 0.0
        rt60_high_scalar = np.mean(rt60_high) if np.any(rt60_high) > 0 else 0.0

        rt60_text = f"RT60 - Low: {rt60_low_scalar:.2f} s | Mid: {rt60_mid_scalar:.2f} s | High: {rt60_high_scalar:.2f} s"
        self.time_label.config(text=self.time_label.cget("text") + f"\n{rt60_text}")
