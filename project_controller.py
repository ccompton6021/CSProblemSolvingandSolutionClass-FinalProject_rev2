# import statements
from project_model import Model
from project_view import View

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
        file_path = self.view.ask_open_filename(filetypes=[("Audio files", "*.wav;*.mp3;*.aac")])
        if file_path:
            self.model.load_file(file_path)
            self.view.file_label.config(text=f"File: {self.model.filename}")
            self.view.plot_waveform()

    def analyze_audio(self):
        self.view.analyze_audio()