import os
import pyaudio
import whisper
import wave

class VoiceControl:
    def __init__(self):
        self.model = whisper.load_model("base")

    def recognize_speech(self, file_path):
        try:
            result = self.model.transcribe(file_path)
            return result['text']
        finally:
            print("bbbb")
            # Clean up the WAV file
            if os.path.exists(file_path):
                os.remove(file_path)

# Example usage
if __name__ == "__main__":
    voice_control = VoiceControl()
    while True:
        command = voice_control.recognize_speech()
        if command:
            print(f"Processed command: {command}")