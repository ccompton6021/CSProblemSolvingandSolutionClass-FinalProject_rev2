from scipy.io import wavfile
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from pydub import AudioSegment

# Assuming we already have user input
audio_file_path = Path(r'C:\Users\amseb_7f4cpmk\Documents\Python_Files\COP2080\final_project\Audio_Clap_AulaMagna.wav')


# Function that converts audio file to wav
def convert_audio_to_wav(audio_file_path):
    if audio_file_path.suffix != '.wav':
        file_extension = audio_file_path.suffix
        if file_extension == '.m4a':
            audio_file = AudioSegment.from_file(audio_file_path, format='mp4')
            audio_file.export('audio_file.wav', format='wav')
            wav_audio_file = AudioSegment('audio_file.wav', format='wav')
        else:
            audio_file = AudioSegment.from_file(audio_file_path, format=file_extension)
            audio_file.export('audio_file.wav', format='wav')
            wav_audio_file = AudioSegment('audio_file.wav', format='wav')
        return wav_audio_file
    else:
        wav_audio_file = AudioSegment.from_file(audio_file_path, format='wav')
        return wav_audio_file


wav_file = convert_audio_to_wav(audio_file_path)


def clean_audio(wav_audio_file):
    channels = wav_audio_file.channels
    if channels >= 2:
        mono_wav = wav_audio_file.set_channels(1)
        mono_wav.export('audio_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file('audio_mono.wav', format='wav')
        return mono_wav_audio
    else:
        wav_audio_file.export('audio_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file('audio_mono.wav', format='wav')
        return mono_wav_audio


wav_file_mono = clean_audio(wav_file)
# print(wav_file.channels)

# Creating the spectrogram
sample_rate, data = wavfile.read('audio_mono.wav')
spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate,
      NFFT=1024, cmap=plt.get_cmap('autumn_r'))

plt.show()
