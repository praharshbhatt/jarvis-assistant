import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.tts = pyttsx3.init()

    def speak(self, text):
        self.tts.say(text)
        self.tts.runAndWait()
        return text