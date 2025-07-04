import os
import requests
import tempfile
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, Response
from marshmallow import Schema, fields, ValidationError
from middleware.error_handler import handle_error, handle_validation_error
from dotenv import load_dotenv

load_dotenv()

voice_bp = Blueprint('voice', __name__)

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "ueSxRO0nLF1bj93J2hVt")

class TTSSchema(Schema):
    text = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 5000)

class STTSchema(Schema):
    audio_data = fields.Str(required=True)

@voice_bp.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        schema = TTSSchema()
        data = schema.load(request.json)
        
        text = data['text']
        
        if not ELEVEN_API_KEY:
            return handle_error('ElevenLabs API key not configured', 500)
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_API_KEY
        }
        body = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            audio_bytes = response.content
            headers = {
                'Content-Type': 'audio/mpeg',
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*'
            }
            return Response(audio_bytes, headers=headers)
        else:
            return handle_error(f'ElevenLabs API error: {response.status_code}', 500)
            
    except ValidationError as e:
        return handle_validation_error(e.messages)
    except Exception as e:
        print(f"TTS error: {e}")
        return handle_error('Failed to generate speech. Please try again.', 500)

@voice_bp.route('/stt', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return handle_error('No audio file provided', 400)
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'auto')  # Default to auto-detect
        
        if not ELEVEN_API_KEY:
            return handle_error('ElevenLabs API key not configured', 500)
        
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {
            "xi-api-key": ELEVEN_API_KEY
        }
        
        files = {
            'audio': (audio_file.filename, audio_file.read(), audio_file.content_type)
        }
        
        # Add language parameter if specified and not auto
        data = {}
        if language and language != 'auto':
            data['language'] = language
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'data': {
                    'text': result.get('text', ''),
                    'language': language,
                    'timestamp': datetime.now().isoformat() + 'Z'
                }
            })
        else:
            return handle_error(f'ElevenLabs STT API error: {response.status_code}', 500)
            
    except Exception as e:
        print(f"STT error: {e}")
        return handle_error('Failed to transcribe speech. Please try again.', 500)

@voice_bp.route('/voices', methods=['GET'])
def get_available_voices():
    try:
        if not ELEVEN_API_KEY:
            return handle_error('ElevenLabs API key not configured', 500)
        
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {
            "xi-api-key": ELEVEN_API_KEY
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            return jsonify({
                'success': True,
                'data': {
                    'voices': voices.get('voices', []),
                    'timestamp': datetime.now().isoformat() + 'Z'
                }
            })
        else:
            return handle_error(f'ElevenLabs API error: {response.status_code}', 500)
            
    except Exception as e:
        print(f"Get voices error: {e}")
        return handle_error('Failed to fetch available voices.', 500)

@voice_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Voice service is healthy',
        'timestamp': datetime.now().isoformat() + 'Z'
    }) 