# -*- coding: utf-8 -*-
"""final_project_practice.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FBuCB6xFoQB2hOcB-9vtRBXSJcYsNXBm

Needed imports:
scipy.io -> reading audio file,
numpy -> for math computations(like cmath),
matplotib.pyplot -> for graphing results
"""

# Commented out IPython magic to ensure Python compatibility.
from scipy.io import wavfile
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

'''
Reading the file using wavfile.read
Returns tuple with first element being the sample rate (in Hz),
second being the actual audio data (what makes the waves),
and third being the type (which we ignore)

Then we create a spectrogram which returns a tuple and we assign those
values appropriately

'''
sample_rate, data = wavfile.read('16bit1chan.wav')
spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, \
      NFFT=1024, cmap=plt.get_cmap('autumn_r'))

# simple debugg function
# uncomment pass to disable calls
def debugg(string):
  # print(string)
   pass

# Want to establish the range of frequencies that
# we are going to work with by finding the max
# mid-range frequency (the target frequency)
def find_target_frequency(freqs):
  for x in freqs:
    if x > 1000:
      break
    return x

def frequency_check():

  # Using debugg function to check intermediate calculations
  debugg(f'freqs {freqs[:5]}')
  # Assign the mid range frequency as our target_frequency
  target_frequency = find_target_frequency(freqs)
  # Check debugg again
  debugg(f'target_frequency {target_frequency}')

  # Then we find the position (index) of where target_frequency is located
  # Used np.where as a condition to find the index in freqs array
  index_of_frequency = np.where(freqs == target_frequency)[0][0]
  debugg(f'index_of_frequency {index_of_frequency}')

  # After finding the index we look for the audio data associated with it
  # It seems that spectrum, freqs, t, etc, are all connected to each other
  # when plt.specgram was done
  data_for_frequency = spectrum[index_of_frequency]
  debugg(f'data_for_frequency {data_for_frequency}')

  # After finding the mid frequency, its index position in spectrum, and data
  # we convert its data from digital signal to decibles (db)
  data_in_db_fun = 10 * np.log10(data_for_frequency)
  return data_in_db_fun

"""Finding the -5dB"""

# Assigning the decible data into data_in_db
data_in_db = frequency_check()
plt.figure()

