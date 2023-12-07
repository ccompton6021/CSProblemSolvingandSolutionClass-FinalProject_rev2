from scipy.io import wavfile
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from pydub import AudioSegment

# Assuming we already have user input
# Obtaining the file name without the extension
audio_file_path = Path(r'C:\Users\amseb_7f4cpmk\Documents\Python_Files\COP2080\final_project\Audio_Clap_AulaMagna.wav')
file_name = audio_file_path.stem

# Function that converts audio file to wav
# First we check if the file is not in .wav
# if no then we check if the file extension is in .m4a
# if yes then we create a .mp4 object and convert to uncleaned .wav

# if the original file was a .wav in the first place,
# we simply create a .wav object to represent it
# After all of this, we pass it to cleaning function
def convert_audio_to_wav(audio_file_path):
    file_extension = audio_file_path.suffix
    if file_extension != '.wav':
        if file_extension == '.m4a':
            audio_file = AudioSegment.from_file(audio_file_path, format='mp4')
            audio_file.export(f'{file_name}_uncleaned.wav', format='wav')
            wav_audio_file = AudioSegment(f'{file_name}_uncleaned.wav', format='wav')
        else:
            audio_file = AudioSegment.from_file(audio_file_path, format=file_extension)
            audio_file.export(f'{file_name}_uncleaned.wav', format='wav')
            wav_audio_file = AudioSegment(f'{file_name}_uncleaned.wav', format='wav')
        return wav_audio_file
    else:
        wav_audio_file = AudioSegment.from_file(audio_file_path, format='wav')
        return wav_audio_file


wav_file = convert_audio_to_wav(audio_file_path)


def clean_audio(wav_audio_file):
    channels = wav_audio_file.channels
    if channels >= 2:
        mono_wav = wav_audio_file.set_channels(1)
        mono_wav.export(f'{file_name}_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file(f'{file_name}_mono.wav', format='wav')
        return mono_wav_audio
    else:
        wav_audio_file.export(f'{file_name}_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file(f'{file_name}_mono.wav', format='wav')
        return mono_wav_audio


wav_file_mono = clean_audio(wav_file)
# print(wav_file.channels)

# Creating the spectrogram
'''
Reading the file using wavfile.read
Returns tuple with first element being the sample rate (in Hz),
second being the actual audio data (what makes the waves),
and third being the type (which we ignore)

Then we create a spectrogram which returns a tuple and we assign those
values appropriately

'''
sample_rate, data = wavfile.read(f'{file_name}_mono.wav')
spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate,
                                      NFFT=1024, cmap=plt.get_cmap('autumn_r'))


# simple debugg function
# uncomment pass to disable calls
def debugg(string):
    # print(string)
    pass


# Now we look for three frequencies within the audio data:
# low, mid, and high frequencies.
# Want to establish the range of frequencies that
# we are going to work with by finding the max
def find_target_frequencies(freqs):
    for x in freqs:
        if x > 500:
            low_freq = x
            break
    for x in freqs:
        if x > 1000:
            mid_freq = x
            break
    for x in freqs:
        if x > 1500:
            high_freq = x
            break
    return low_freq, mid_freq, high_freq


def frequency_check():
    # Using debugg function to check intermediate calculations
    debugg(f'freqs {freqs[:5]}')
    # Assign the low, mid, and high frequencies
    low_freq, mid_freq, high_freq = find_target_frequencies(freqs)
    # Check debugg again
    debugg(f'low {low_freq}')
    debugg(f'mid {mid_freq}')
    debugg(f'high {high_freq}')

    # Then we find the position (index) of where the target freqs are located
    # Used np.whereas a condition to find the index in freqs array
    index_of_low = np.where(freqs == low_freq)[0][0]
    index_of_mid = np.where(freqs == mid_freq)[0][0]
    index_of_high = np.where(freqs == high_freq)[0][0]
    debugg(f'index_of_low {index_of_low}')
    debugg(f'index_of_mid {index_of_mid}')
    debugg(f'index_of_high {index_of_high}')

    # After finding the indexes we look for the audio data associated with it.
    # It seems that spectrum, freqs, t, etc, are all connected to each other
    # when plt.specgram was done
    data_for_low = spectrum[index_of_low]
    data_for_mid = spectrum[index_of_mid]
    data_for_high = spectrum[index_of_high]
    debugg(f'data_for_low {data_for_low[:5]}')
    debugg(f'data_for_mid {data_for_mid[:5]}')
    debugg(f'data_for_high {data_for_high[:5]}')

    # After finding the low, mid and, high frequencies,
    # its index positions in spectrum, and data,
    # we convert their data from digital signal to decibles (db)
    data_low_db = 10 * np.log10(data_for_low)
    data_mid_db = 10 * np.log10(data_for_mid)
    data_high_db = 10 * np.log10(data_for_high)
    return data_low_db, data_mid_db, data_high_db


low_in_db, mid_in_db, high_in_db = frequency_check()

# Allows you to create multiple graph pictures.
# Do this everytime you want to graph something separately
plt.figure()
# Plotting the data where x is the time and y is the amplitude (power) in db
# linewidth sets the thickness of the line
# alpha sets the clarity (boldness) of the line. Ranges from 0-1
plt.plot(t, high_in_db, linewidth=1, alpha=0.7, color='#004bc6')
plt.xlabel('Time (s)')
plt.ylabel('Power (dB)')
plt.title('High Frequency Graph')


# Finding the index and value of the maximum decible
# for low, mid, and high
# and plotting it on the graph as a point (only high)
# The last argument specifies that a red (keyword 'r')
# circle (keyword 'o') will be plotted according to the
# left arguments
index_of_max_low = np.argmax(low_in_db)
value_of_max_low = low_in_db[index_of_max_low]

index_of_max_mid = np.argmax(mid_in_db)
value_of_max_mid = mid_in_db[index_of_max_mid]

index_of_max_high = np.argmax(high_in_db)
value_of_max_high = high_in_db[index_of_max_high]

plt.plot(t[index_of_max_high], high_in_db[index_of_max_high], 'ro')

# plt.show() shows all of the figures at once
# plt.show()


# slicing the db arrays so that it starts on the maximum db
sliced_array_low = low_in_db[index_of_max_low:]
sliced_array_mid = mid_in_db[index_of_max_mid:]
sliced_array_high = high_in_db[index_of_max_high:]

# Now we find the maximum value 5 dB down which sets us up to find
# Rt20 which then helps us find Rt60
value_less5_low = value_of_max_low - 5
value_less5_mid = value_of_max_mid - 5
value_less5_high = value_of_max_high - 5
print(f'Max low value {value_of_max_low}')
print(sliced_array_low[:10])
print(f'Low Max - 5 dB = {value_less5_low}')




