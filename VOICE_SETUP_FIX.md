# 🎤 Voice Feature Fix - ElevenLabs Setup

Your application has full voice functionality built-in, but it's missing the **ElevenLabs API key** configuration.

## 🚨 Quick Fix

### Step 1: Get ElevenLabs API Key
1. Go to [ElevenLabs.io](https://elevenlabs.io)
2. Sign up for a free account
3. Go to your profile settings
4. Copy your API key

### Step 2: Add API Key to Environment
Edit your `.env.production` file (or `.env` if running locally) and add:

```env
# ElevenLabs Configuration (for voice features)
ELEVENLABS_API_KEY=your_actual_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### Step 3: Restart Application
```powershell
# Stop the application
docker-compose -f docker-compose.windows.yml down

# Start again with new environment
docker-compose -f docker-compose.windows.yml up -d
```

## 🎯 Voice Features Available

Once configured, your app will have:

### 1. **Auto Text-to-Speech**
- Toggle the speaker icon in the chat interface
- AI responses will be spoken automatically
- High-quality voice synthesis

### 2. **Voice Chat Mode**
- Click the microphone button to open voice chat
- Speak your message, AI responds with voice
- Full conversation in voice mode

### 3. **Speech Recognition**
- Browser-based speech recognition (Chrome/Edge)
- Converts your speech to text
- No additional setup needed

## 🔧 Testing Voice Features

1. **Test TTS (Text-to-Speech)**:
   ```bash
   curl -X POST http://localhost:5000/api/voice/tts \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test"}'
   ```

2. **Check Voice Service**:
   ```bash
   curl http://localhost:5000/api/voice/health
   ```

3. **Get Available Voices**:
   ```bash
   curl http://localhost:5000/api/voice/voices
   ```

## 📱 How to Use Voice Features

### In Chat Interface:
1. **Enable Auto-Speech**: Click the speaker icon in the top-right
2. **Voice Chat**: Click the microphone button to open voice mode
3. **Manual TTS**: Right-click any AI message to hear it spoken

### In Voice Chat Mode:
1. Click the large microphone button
2. Speak your message
3. Click again to stop and send
4. AI will respond with both text and voice

## 🎵 Voice Settings

You can customize voice settings by editing the TTS request in `backend/routes/voice.py`:

```python
"voice_settings": {
    "stability": 0.5,        # 0.0-1.0 (lower = more variable)
    "similarity_boost": 0.75  # 0.0-1.0 (higher = more similar to original)
}
```

## 🆓 ElevenLabs Free Tier

- **10,000 characters/month** free
- No credit card required
- Perfect for testing and light usage
- Upgrade available if needed

## ⚠️ Troubleshooting

### No Voice Output:
1. Check browser console for errors
2. Ensure ElevenLabs API key is valid
3. Check browser allows audio playback
4. Try a different browser (Chrome/Edge recommended)

### Voice Recognition Not Working:
1. Must use Chrome or Edge browser
2. Allow microphone permissions
3. Check microphone hardware

### API Errors:
1. Verify API key is correct
2. Check ElevenLabs account status
3. Ensure internet connection is stable

That's it! Your voice features should work perfectly once the API key is added. 