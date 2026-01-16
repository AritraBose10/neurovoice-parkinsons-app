import requests
import base64
import json
import os

# Create a small dummy wav file
dummy_wav_path = "test_audio_debug.wav"
with open(dummy_wav_path, "wb") as f:
    # Minimal valid WAV header (44 bytes) for a silent file
    # This is just to pass the file existence check, content might fail processing but we want to see the API response structure errors or success
    # Using a slightly real header so librosa doesn't crash immediately
    header = bytes.fromhex('524946462400000057415645666D7420100000000100010044AC000088580100020010006461746100000000')
    f.write(header + b'\x00' * 1000)

with open(dummy_wav_path, "rb") as audio_file:
    audio_content = audio_file.read()
    audio_b64 = base64.b64encode(audio_content).decode('utf-8')

payload = {
    "audio": f"data:audio/wav;base64,{audio_b64}",
    "duration": 1.0
}

try:
    print("Sending request to http://127.0.0.1:5000/api/analyze...")
    response = requests.post("http://127.0.0.1:5000/api/analyze", json=payload)
    
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

if os.path.exists(dummy_wav_path):
    os.remove(dummy_wav_path)
