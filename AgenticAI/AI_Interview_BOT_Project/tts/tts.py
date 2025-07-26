import time
import pyttsx3
from PyQt5.QtCore import QThread

class TTSThread(QThread):
    def __init__(self, text, movie=None):
        super().__init__()
        self.text = text
        self.movie = movie

    def run(self):
        if self.movie:
            self.movie.start()
        engine = pyttsx3.init()
        engine.say(self.text)
        engine.runAndWait()
        engine.stop()
        if self.movie:
            self.movie.stop()
        time.sleep(0.5)