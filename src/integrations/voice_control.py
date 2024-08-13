# voice_control.py
import os
import sys
import json
import pyaudio
import vosk
import spacy #NLP
#posterior change to openai

class VoiceControl:
    def __init__(self):
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-en-us-0.22-lgraph'))
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.nlp = spacy.load("en_core_web_sm")

    def recognize_speech(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()
        
        print("Listening...")
        while True:
            try:
                data = stream.read(4096, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = json.loads(result)["text"]
                    return text
            except OSError as e:
                print(f"Error: {e}")
                continue

    def process_command(self, command):
        doc = self.nlp(command)
        return doc

# Example usage
if __name__ == "__main__":
    voice_control = VoiceControl()
    while True:
        command = voice_control.recognize_speech()
        doc = voice_control.process_command(command)
        print(f"Processed command: {doc}")