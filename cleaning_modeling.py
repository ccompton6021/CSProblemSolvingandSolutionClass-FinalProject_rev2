from scipy.io import wavfile
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from pydub import AudioSegment

# Function that converts audio file to wav
# First we check if the file is not in .wav
# if no then we check if the file extension is in .m4a
# if yes then we create a .mp4 object and convert to uncleaned .wav

# if the original file was a .wav in the first place,
# we simply create a .wav object to represent it
# After all of this, we pass it to cleaning function
def convert_audio_to_wav(audio_file_path, file_name):
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

# Cleaning function only checks to see if there are 2 or more channels and adjusts the .wav accordingly
# we created a new audio file if the original had 2 or more channels with the added '_mono.wav'
def clean_audio(wav_audio_file, file_name, full_file_name, audio_file_path):
    channels = wav_audio_file.channels
    if channels >= 2:
        mono_wav = wav_audio_file.set_channels(1)
        mono_wav.export(f'{file_name}_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file(f'{file_name}_mono.wav', format='wav')
        return mono_wav_audio, f'{file_name}_mono.wav'
    else:
        # wav_audio_file.export(f'{file_name}_mono.wav', format='wav')
        mono_wav_audio = AudioSegment.from_file(audio_file_path, format='wav')
        return mono_wav_audio, full_file_name


# simple debugg function
# uncomment pass to disable calls
def debugg(string):
    print(string)
    # pass


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


# frequency_check takes the low, mid, and high frequencies and finds the
# audio data for each which it then converts over to db
def frequency_check(freqs, spectrum):
    # Using debugg function to check intermediate calculations
    # debugg(f'freqs {freqs[:5]}')
    # Assign the low, mid, and high frequencies
    low_freq, mid_freq, high_freq = find_target_frequencies(freqs)

    # Then we find the position (index) of where the target freqs are located
    # Used np.whereas a condition to find the index in freqs array
    index_of_low = np.where(freqs == low_freq)[0][0]
    index_of_mid = np.where(freqs == mid_freq)[0][0]
    index_of_high = np.where(freqs == high_freq)[0][0]

    # After finding the indexes we look for the audio data associated with it.
    # It seems that spectrum, freqs, t, etc, are all connected to each other
    # when plt.specgram was done
    data_for_low = spectrum[index_of_low]
    data_for_mid = spectrum[index_of_mid]
    data_for_high = spectrum[index_of_high]

    # After finding the low, mid and, high frequencies,
    # its index positions in spectrum, and data,
    # we convert their data from digital signal to decibles (db)
    data_low_db = 10 * np.log10(data_for_low)
    data_mid_db = 10 * np.log10(data_for_mid)
    data_high_db = 10 * np.log10(data_for_high)
    return data_low_db, data_mid_db, data_high_db


# Function that returns a tuple of the max value and its index
# in accordance with the db array (low, mid, and high)
def find_max_values_and_indexes(frequency_data_collection, key):
    # Finding the index and value of the maximum decible
    # for low, mid, and high
    index_of_max = np.argmax(frequency_data_collection[key]['Data in dB'])
    value_of_max = frequency_data_collection[key]['Data in dB'][index_of_max]
    data = (value_of_max, index_of_max)
    return data


# Function that creates dB array starting at the maximum dB value
def array_slicing(frequency_data_collection, key):
    value_max, index_max = frequency_data_collection[key]['Max Value and Index']
    sliced_array = frequency_data_collection[key]['Data in dB'][index_max:]
    return sliced_array

# np.asarray just converts whatever you pass it into an array
# np.argmin returns the index of the minimum value.
def find_nearest_value(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


# Now we find the nearest values of the low, mid,
# and high frequencies along with their indexes in the non_sliced
# array. In this case, we have to functions for finding the -5 dB
# and -25 dB. Both work very similar
def find_5_dB(frequency_data_collection, key, sliced_arrays):
    # We are now working with the sliced array which starts on the most
    # maximum db value. Now we take that array and subtract the desired db
    # amount to get the true index and db value from sliced array(not data_in_db)
    # Remember that data_in_db contains all db values including the ones
    # before the maximum.

    # Now we find the maximum value 5 dB down which sets us up to find
    # Rt20 which then helps us find Rt60
    value_max, index_max = frequency_data_collection[key]['Max Value and Index']

    value_less5 = value_max - 5
    value_less5 = find_nearest_value(sliced_arrays[key]['Sliced Data in dB'], value_less5)
    index_less5 = np.where(frequency_data_collection[key]["Data in dB"] == value_less5)
    return value_less5, index_less5


def find_25_dB(frequency_data_collection, key, sliced_arrays):
    value_max, index_max = frequency_data_collection[key]['Max Value and Index']

    value_less25 = value_max - 25
    value_less25 = find_nearest_value(sliced_arrays[key]['Sliced Data in dB'], value_less25)
    index_less25 = np.where(frequency_data_collection[key]["Data in dB"] == value_less25)
    return value_less25, index_less25


# Function for finding the rt_60
def find_rt60(frequency_data_collection, key, time):
    max_value_less5, index_less5 = frequency_data_collection[key]['-5 dB Value and Index']
    max_value_less25, index_less25 = frequency_data_collection[key]['-25 dB Value and Index']

    # rt20 is the reverberation time (time it takes for sound to die down)
    # between the -5dB and -25dB
    rt_20 = (time[index_less5] - time[index_less25])[0]
    rt_60 = 3 * rt_20
    return rt_60

### RT60 OF LOW ###
# rt20 is the reverberation time (time it takes for sound to die down)
# between the -5dB and -25dB
# rt20_low = (t[index_less5_low] - t[index_less25_low])[0]
# rt60_low = 3 * rt20_low

### RT60 OF MID ###
# rt20_mid = (t[index_less5_mid] - t[index_less25_mid])[0]
# rt60_mid = 3 * rt20_mid

### RT60 OF HIGH ###
# rt20_high = (t[index_less5_high] - t[index_less25_high])[0]
# rt60_high = 3 * rt20_high


# Graphing function that takes each of the frequencies and plots their wave form
# along with the max, -5, and -25 dB values
def graph_frequencies(frequency_data_collection, key, time):
    # Grabbing the value and indexes from dictionary
    max_value, max_index = frequency_data_collection[key]['Max Value and Index']
    value_less5, index_less5 = frequency_data_collection[key]['-5 dB Value and Index']
    value_less25, index_less25 = frequency_data_collection[key]['-25 dB Value and Index']

    # figure() allows you to create multiple graph pictures.
    # Do this everytime you want to graph something separately
    plt.figure()

    # Plotting the line
    # Plotting the data where x is the time and y is the amplitude (power) in db
    # linewidth sets the thickness of the line
    # alpha sets the clarity (boldness) of the line. Ranges from 0-1
    plt.plot(time, frequency_data_collection[key]['Data in dB'], linewidth=1, alpha=0.7, color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB')
    plt.title(f'{key} Graph')

    # Plotting the points and adding a legend
    plt.plot(time[max_index], frequency_data_collection[key]['Data in dB'][max_index],
             'ro', label='Max dB')
    plt.plot(time[index_less5], frequency_data_collection[key]['Data in dB'][index_less5],
             'yo', label='-5 dB')
    plt.plot(time[index_less25], frequency_data_collection[key]['Data in dB'][index_less25],
             'go', label='-25 dB')
    plt.legend(loc='upper right')


# Wrapper function that connects everything together

    """
    The idea behind this program is to start by creating a dictionary which will house 
    all of the frequency data from the audio file. There are three categories: Low
    Frequency, Mid Frequency, and High Frequency in which things like the data in dB, 
    max values/indexes, -5 db values/indexes, and -25 db values/indexes will be stored inside
    of one nested dictionary for easy access. No need to scramble around looking for low, mid, or
    high frequency values. 

    The functions are designed to take the dictionary along with the keys (low, mid, and high categories)
    to create and manipulate from its values. Now there is no need to hard code values for each of the categories

    This main function shows the executing logic
    """


def main():
    # Assuming we already have user input
    # Obtaining the file name with and without extension (file_name and full_file_name)
    #audio_file_path = Path(r'C:\Users\amseb_7f4cpmk\Documents\Python_Files\COP2080\final_project\16bit1chan.wav')
    audio_file_path = Path(r'Audio_Clap_AulaMagna.m4a')
    file_name = audio_file_path.stem
    full_file_name = audio_file_path.name

    # Calling the convert audio function to check if the audio file is in .wav
    # The function creates a new audio file if not in .wav
    wav_file = convert_audio_to_wav(audio_file_path, file_name)

    # Grabbing the cleaned wav file along with its name so that they can be used to create a
    # spectrogram
    wav_file_mono, f_name = clean_audio(wav_file, file_name, full_file_name, audio_file_path)

    # Creating the spectrogram
    # Reading the file using wavfile.read
    # Returns tuple with first element being the sample rate (in Hz),
    # second being the actual audio data (what makes the waves),
    # and third being the type (which we ignore)
    # Then we create a spectrogram which returns a tuple and we assign those
    # values appropriately
    sample_rate, data = wavfile.read(f_name)
    spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate,
                                          NFFT=1024, cmap=plt.get_cmap('autumn_r'))

    # Creating the dictionary which houses most of the values used throughout the program.
    # We instantiate most of the keys
    frequency_data_collection = {
        'Low Frequency': {'Max Value and Index': (), '-5 dB Value and Index': (), '-25 dB Value and Index': ()},
        'Mid Frequency': {'Max Value and Index': (), '-5 dB Value and Index': (), '-25 dB Value and Index': ()},
        'High Frequency': {'Max Value and Index': (), '-5 dB Value and Index': (), '-25 dB Value and Index': ()}}

    # Finding the dB arrays for the low, mid, and high frequencies and creating new keys
    # within the data collection to represent them
    low_in_db, mid_in_db, high_in_db = frequency_check(freqs, spectrum)
    frequency_data_collection['Low Frequency']['Data in dB'] = low_in_db
    frequency_data_collection['Mid Frequency']['Data in dB'] = mid_in_db
    frequency_data_collection['High Frequency']['Data in dB'] = high_in_db

    # Loops are created so that each of the main categories in the dictionary
    # (low, mid, and high) are all iterated through. No need to repeat the same code
    # for each category. This loop calls the max values and frequencies to find the max values
    # within Data in dB
    for key in frequency_data_collection.keys():
        data = find_max_values_and_indexes(frequency_data_collection, key)
        frequency_data_collection[key]['Max Value and Index'] = data

    # slicing the db arrays so that it starts on the maximum db
    # A new dictionary is created just to house the sliced Data in dB arrays from each of
    # the categories
    sliced_arrays = {'Low Frequency': {}, 'Mid Frequency': {}, 'High Frequency': {}}
    for key in frequency_data_collection.keys():
        array = array_slicing(frequency_data_collection, key)
        sliced_arrays[key]['Sliced Data in dB'] = array

    # Now we find the maximum value 5 and 25 dB down which sets us up to find
    # Rt20 which then helps us find Rt60
    # Finding the -5 dB values
    for key in frequency_data_collection.keys():
        data = find_5_dB(frequency_data_collection, key, sliced_arrays)
        frequency_data_collection[key]['-5 dB Value and Index'] = data

    # Finding the -25 dB values
    for key in frequency_data_collection.keys():
        data = find_25_dB(frequency_data_collection, key, sliced_arrays)
        frequency_data_collection[key]['-25 dB Value and Index'] = data

    # Loop for assigning the RT 60 for each of the categories
    for key in frequency_data_collection.keys():
        rt_60 = find_rt60(frequency_data_collection, key, t)
        frequency_data_collection[key]['RT60'] = rt_60

    # Finally we take the complete data dictionary and its main keys
    # to create three graphs: Low Frequency, Mid-Frequency, and High Frequency
    for key in frequency_data_collection.keys():
        graph_frequencies(frequency_data_collection, key, t)

    # Then, we show all the graphs
    # plt.show() shows all of the figures at once
    plt.show()


# Executing the whole program
main()
