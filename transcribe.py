from faster_whisper import WhisperModel

def transcribe_audio(audio_path):
    model = WhisperModel("base", device="cpu", compute_type="int8")

    segments, info = model.transcribe(audio_path)

    transcript = ""

    for segment in segments:
        transcript += segment.text + " "

    return transcript.strip()


if __name__ == "__main__":
    result = transcribe_audio("uploads/Recording.m4a")
    print("\nTRANSCRIPT:\n")
    print(result)