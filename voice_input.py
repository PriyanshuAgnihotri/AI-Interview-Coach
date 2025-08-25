import openai

def transcribe_audio(audio_file):
    """
    Convert speech (mp3/wav) to text using OpenAI Whisper API.
    """
    try:
        with open(audio_file, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript["text"]
    except Exception as e:
        return f"[Whisper Error: {str(e)}]"
