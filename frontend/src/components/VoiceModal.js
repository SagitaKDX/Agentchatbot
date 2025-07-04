import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Play, Pause, Volume2, X, Send, Loader } from 'lucide-react';

const VoiceModal = ({ isOpen, onClose, onSendMessage, isLoading }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isGeneratingSpeech, setIsGeneratingSpeech] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);
  const [selectedVoice, setSelectedVoice] = useState('21m00Tcm4TlvDq8ikWAM');
  const [availableVoices, setAvailableVoices] = useState([]);
  const [sttLang, setSttLang] = useState('auto');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const ttsAudioRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchAvailableVoices();
    }
  }, [isOpen]);

  const fetchAvailableVoices = async () => {
    try {
      const response = await fetch('/api/voice/voices');
      const data = await response.json();
      if (data.success) {
        setAvailableVoices(data.data.voices);
      }
    } catch (error) {
      console.error('Error fetching voices:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Error accessing microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;

    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');
      formData.append('language', sttLang);

      const response = await fetch('/api/voice/stt', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        setTranscribedText(data.data.text);
      } else {
        alert('Error transcribing audio: ' + data.error);
      }
    } catch (error) {
      console.error('Error transcribing:', error);
      alert('Error transcribing audio. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const generateSpeech = async (text) => {
    if (!text.trim()) return;

    setIsGeneratingSpeech(true);
    try {
      const response = await fetch('/api/voice/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setTtsAudioUrl(url);
        if (ttsAudioRef.current) {
          ttsAudioRef.current.src = url;
        }
      } else {
        const data = await response.json();
        alert('Error generating speech: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating speech:', error);
      alert('Error generating speech. Please try again.');
    } finally {
      setIsGeneratingSpeech(false);
    }
  };

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const playTTS = () => {
    if (ttsAudioRef.current) {
      ttsAudioRef.current.play();
    }
  };

  const handleSend = () => {
    if (transcribedText.trim()) {
      onSendMessage(transcribedText);
      handleClose();
    }
  };

  const handleClose = () => {
    setTranscribedText('');
    setAudioBlob(null);
    setAudioUrl(null);
    setTtsAudioUrl(null);
    setIsRecording(false);
    setIsPlaying(false);
    setIsTranscribing(false);
    setIsGeneratingSpeech(false);
    onClose();
  };

  const handleTextChange = (e) => {
    setTranscribedText(e.target.value);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Voice Assistant</h2>
            <button
              onClick={handleClose}
              className="p-1 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="space-y-4">
            <div className="text-center">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isTranscribing || isLoading}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                } ${(isTranscribing || isLoading) ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}`}
              >
                {isRecording ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
              </button>
              <p className="text-sm text-gray-600 mt-2">
                {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
              </p>
            </div>

            {audioUrl && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Recorded Audio</span>
                  <button
                    onClick={isPlaying ? pauseAudio : playAudio}
                    className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </button>
                </div>
                <audio ref={audioRef} src={audioUrl} onEnded={() => setIsPlaying(false)} />
                <button
                  onClick={transcribeAudio}
                  disabled={isTranscribing}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isTranscribing ? (
                    <div className="flex items-center justify-center">
                      <Loader className="h-4 w-4 animate-spin mr-2" />
                      Transcribing...
                    </div>
                  ) : (
                    'Transcribe Audio'
                  )}
                </button>
              </div>
            )}

            {transcribedText && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Transcribed Text
                  </label>
                  <textarea
                    value={transcribedText}
                    onChange={handleTextChange}
                    className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Transcribed text will appear here..."
                  />
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => generateSpeech(transcribedText)}
                    disabled={isGeneratingSpeech}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
                  >
                    {isGeneratingSpeech ? (
                      <Loader className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Volume2 className="h-4 w-4 mr-2" />
                    )}
                    {isGeneratingSpeech ? 'Generating...' : 'Listen'}
                  </button>
                  <button
                    onClick={handleSend}
                    disabled={!transcribedText.trim() || isLoading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send
                  </button>
                </div>

                {ttsAudioUrl && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Generated Speech</span>
                      <button
                        onClick={playTTS}
                        className="p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        <Play className="h-4 w-4" />
                      </button>
                    </div>
                    <audio ref={ttsAudioRef} src={ttsAudioUrl} />
                  </div>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Speech Language
                </label>
                                  <select
                    value={sttLang}
                    onChange={(e) => setSttLang(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="auto">Auto Detect</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="ja">日本語</option>
                    <option value="ko">한국어</option>
                    <option value="zh">中文</option>
                  </select>
              </div>

              {availableVoices.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Voice Selection
                  </label>
                  <select
                    value={selectedVoice}
                    onChange={(e) => setSelectedVoice(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {availableVoices.map((voice) => (
                      <option key={voice.voice_id} value={voice.voice_id}>
                        {voice.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceModal; 