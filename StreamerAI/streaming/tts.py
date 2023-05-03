import base64
import os
import pygame
import requests
import tempfile
import time
import uuid

from ..settings import TTS_ACCESS_TOKEN


class TextToSpeech:
    """
    A class that provides text-to-speech functionality using the ByteDance OpenSpeech API.

    Attributes:
        voice_type (str): The type of voice to use for the speech synthesis (e.g. 'BV700_streaming').
        style_name (str): The name of the speech style to use (e.g. 'happy').

    Methods:
        play_base64_audio(b64_audio): Plays audio from a base64-encoded audio file.
        tts(text): Generates audio from a given text using the ByteDance OpenSpeech API and plays it.
    """
    
    def __init__(self, voice_type='BV700_streaming', style_name='happy'):
        """
        Initializes the TextToSpeech object with the given voice type and speech style.

        Args:
            voice_type (str): The type of voice to use for the speech synthesis (e.g. 'BV700_streaming').
            style_name (str): The name of the speech style to use (e.g. 'happy').
        """
        self.voice_type = voice_type
        self.style_name = style_name
        pygame.mixer.init()
        
    @staticmethod
    def play_base64_audio(b64_audio):
        """
        Plays audio from a base64-encoded audio file.

        Args:
            b64_audio (str): A base64-encoded audio file.
        """
        file_descriptor, temp_file_path = tempfile.mkstemp(suffix=".mp3")

        with os.fdopen(file_descriptor, "wb") as temp_file:
            temp_file.write(base64.b64decode(b64_audio))
            temp_file.close()

        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        os.remove(temp_file_path)

    def tts(self, text):
        """
        Generates audio from a given text using the ByteDance OpenSpeech API and plays it.

        Args:
            text (str): The text to generate audio from.
        """
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
                'voice_type': self.voice_type,
                'encoding': 'mp3',
                'compression_rate': 1,
                'rate': 24000,
                'bits': 16,
                'channel': 1,
                'speed_ratio': 1.0,
                'volume_ratio': 1.0,
                'pitch_ratio': 1.0,
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
        
        if self.style_name:
            json_data['audio']['style_name'] = self.style_name
        
        start = time.time()
        response = requests.post('https://openspeech.bytedance.com/api/v1/tts', headers=headers, json=json_data)
        response_json = response.json()
        
        b64_audio = response_json['data']
        self.play_base64_audio(b64_audio)
        
        end = time.time()
        
        # audio_length = response_json['addition']['description']
        # print(audio_length)
        
        return end - start