import requests

def text_to_speech_elevenlabs(text, api_key, voice="Rachel"):
    """
    Convert text to speech using ElevenLabs API.
    Returns raw mp3 bytes that can be played in Streamlit.
    """
    if not api_key:
        raise ValueError("Missing ElevenLabs API Key")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.7}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.content  # mp3 bytes
    else:
        raise Exception(f"TTS Error: {response.text}")

