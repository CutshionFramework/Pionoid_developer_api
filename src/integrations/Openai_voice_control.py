import os
import pyaudio
import whisper 
import spacy
import wave

class VoiceControl:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.model = whisper.load_model("base")

    def recognize_speech(self, duration=4):
        # Initialize PyAudio and stream
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        print("Listening...")

        # Capture audio data
        frames = [
            stream.read(4096, exception_on_overflow=False)
            for _ in range(int(16000 / 4096 * duration))
        ]
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save audio as WAV file
        wav_path = "temp_audio.wav"
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))

        # Transcribe the WAV file
        try:
            result = self.model.transcribe(wav_path)
            return result['text']
        finally:
            # Clean up the WAV file
            if os.path.exists(wav_path):
                os.remove(wav_path)

    def process_command(self, command):
        return self.nlp(command)

# Example usage
if __name__ == "__main__":
    voice_control = VoiceControl()
    while True:
        command = voice_control.recognize_speech()
        if command:
            doc = voice_control.process_command(command)
            print(f"Processed command: {doc}")
