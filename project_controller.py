# import statements
from project_model import Model
from project_view import View
from tkinter import filedialog

# controller class
class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect GUI buttons to controller methods
        self.view.load_button.config(command=self.load_file)
        self.view.analyze_button.config(command=self.analyze_audio)

    def run(self):
        self.view.root.mainloop()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3;*.aac;*.m4a")])
        if file_path:
            self.model.load_file(file_path)
            self.view.file_label.config(text=f"File: {self.model.filename}")
            self.view.plot_waveform(self.model)

    def analyze_audio(self):
        self.view.analyze_audio(self.model)
