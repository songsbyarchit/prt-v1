import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get the API key from the .env file
api_key = os.getenv("ELEVENLABS_API_KEY")

try:
    # Fetch the list of voices from ElevenLabs API
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key}
    )
    
    voices = response.json()
    print("Available voices:", voices)

    # Use the voice_id of 'Aria'
    voice_id = 'wFOtYWBAKv6z33WjceQa'  # Example: Aria's voice ID

    # Proceed with generating text-to-speech using the selected voice_id
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": "Hello, this is a test of the ElevenLabs text-to-speech API.",
            "model_id": "eleven_monolingual_v1"
        }
    )

    if response.status_code == 200:
        audio_content = response.content
        with open("test_output.mp3", "wb") as audio_file:
            audio_file.write(audio_content)
        print("Audio response generated successfully. Saved as 'test_output.mp3'.")
    else:
        print("Failed to generate audio. Error:", response.text)

except Exception as e:
    print("Error:", str(e))