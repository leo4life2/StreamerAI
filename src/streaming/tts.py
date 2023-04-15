import requests
import base64
import time
import pygame
import tempfile
from .settings import TTS_ACCESS_TOKEN
import uuid

pygame.mixer.init()  # Initialize the mixer once at the beginning

def play_base64_audio(b64_audio):
    audio_data = base64.b64decode(b64_audio)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_audio_file:
        temp_audio_file.write(audio_data)
        temp_audio_file.flush()

        pygame.mixer.music.load(temp_audio_file.name)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()


def tts(text, voice_type='BV700_streaming', style_name='happy'):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer;{TTS_ACCESS_TOKEN}',
    }

    json_data = {
        'app': {
            'appid': '6802422088',
            'token': "default_token",
            'cluster': 'volcano_tts',
        },
        'user': {
            'uid': '2100423545',
        },
        'audio': {
            'voice': 'other',
            'voice_type': voice_type,
            'encoding': 'mp3',
            'compression_rate': 1,
            'rate': 24000,
            'bits': 16,
            'channel': 1,
            'speed_ratio': 1.0,
            'volume_ratio': 1.0,
            'pitch_ratio': 1.0,
            'style_name': style_name,
        },
        'request': {
            'reqid': uuid.uuid4().hex, # unique for each request, could use for caching later on.
            'text': text,
            'text_type': 'plain',
            'operation': 'query',
            'silence_duration': '125',
            'with_frontend': '1',
            'frontend_type': 'unitTson',
        },
    }
    
    start = time.time()
    response = requests.post('https://openspeech.bytedance.com/api/v1/tts', headers=headers, json=json_data)
    response_json = response.json()
    
    b64_audio = response_json['data']
    play_base64_audio(b64_audio)
    
    end = time.time()
    
    # audio_length = response_json['addition']['description']
    # print(audio_length)
    
    return end - start