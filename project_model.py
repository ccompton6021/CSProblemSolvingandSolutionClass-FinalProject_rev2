# import statements
from scipy.io import wavfile
import numpy as np
import librosa
from pydub import AudioSegment
import eyed3

# model class
class Model:
    def __init__(self):
        self.filename = ""
        self.sample_rate = 0
        self.audio_data = None

    def load_file(self, file_path):
        # Load audio file
        self.filename = file_path
        if file_path.lower().endswith(('.wav', '.mp3', '.aac','.m4a')):
            if file_path.lower().endswith(('.mp3', '.aac','.m4a')):
                # convert files to .wav
                self.convert_to_wav(file_path)

            # Load audio using librosa for flexible format support
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None, mono=False, res_type='kaiser_fast')

            # Handle metadata
            if len(self.audio_data.shape) > 1 and self.audio_data.shape[0] > 1:
                self.audio_data = np.mean(self.audio_data, axis=0)

            self.remove_metadata(file_path)

    def convert_to_wav(self, file_path):
        sound = AudioSegment.from_file(file_path)
        wav_path = file_path[:-4] + ".wav"
        sound.export(wav_path, format="wav")

    def remove_metadata(self, file_path):
        audiofile = eyed3.load(file_path)
        if audiofile is not None and audiofile.tag:
            audiofile.tag.frame_set.clear()
            audiofile.tag.save()
