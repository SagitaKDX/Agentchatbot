import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, X, Loader, MessageSquare, Waves, Sparkles } from 'lucide-react';

const VoiceChat = ({ isOpen, onClose, onSendMessage, isLoading }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isGeneratingSpeech, setIsGeneratingSpeech] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('21m00Tcm4TlvDq8ikWAM');
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isManuallyStopped, setIsManuallyStopped] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sttLang, setSttLang] = useState('en-US');

  const mediaRecorderRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);
  const ttsAudioRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchAvailableVoices();
      initializeSpeechRecognition();
      // Create a new session when chat opens
      fetch('/api/agent/session/new', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data.session_id) {
            setSessionId(data.data.session_id);
          }
        })
        .catch(err => console.error('Error creating session:', err));
    }
    return () => {
      stopListening();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isOpen]);

  // Reinitialize speech recognition when language changes
  useEffect(() => {
    if (isOpen && recognitionRef.current) {
      initializeSpeechRecognition();
    }
  }, [sttLang]);

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

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = sttLang;
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setIsTranscribing(true);
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        const currentText = finalTranscript + interimTranscript;
        setTranscribedText(currentText);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setIsTranscribing(false);
        // No auto-restart here
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
        setIsTranscribing(false);
        // No auto-restart here
        setTimeout(() => {
          const finalText = transcribedText.trim();
          if (finalText && !isGeneratingSpeech && !isManuallyStopped) {
            handleVoiceMessage(finalText);
          }
        }, 200);
      };
    } else {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
    }
  };

  const startListening = async () => {
    try {
      setIsManuallyStopped(false);
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } catch (error) {
      console.error('Error starting speech recognition:', error);
    }
  };

  const stopListening = () => {
    try {
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
        recognitionRef.current.abort();
      }
    } catch (error) {
      console.error('Error stopping recognition:', error);
    } finally {
      setIsListening(false);
      setIsTranscribing(false);
    }
  };

  const handleVoiceMessage = async (text) => {
    if (!text.trim()) return;

    console.log('Handling voice message:', text);
    stopListening();
    const userMessage = {
      id: Date.now(),
      text: text,
      sender: 'user',
      timestamp: new Date(),
      type: 'voice'
    };
    setConversationHistory(prev => [...prev, userMessage]);
    setTranscribedText('');
    setIsManuallyStopped(false);
    try {
      const response = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          session_id: sessionId
        }),
      });
      const data = await response.json();
      if (data.success) {
        const aiMessage = {
          id: Date.now() + 1,
          text: data.data.message,
          sender: 'ai',
          timestamp: new Date(),
          type: 'voice'
        };
        // Trigger TTS immediately without waiting for UI update
        generateAndPlaySpeech(data.data.message);
        // Update UI after TTS is triggered
        setConversationHistory(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Error sending voice message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        sender: 'ai',
        timestamp: new Date(),
        type: 'voice',
        isError: true
      };
      setConversationHistory(prev => [...prev, errorMessage]);
    } finally {
      // Don't auto-restart - let user manually start next recording
    }
  };

  const generateAndPlaySpeech = async (text) => {
    if (!text.trim()) return;

    setIsGeneratingSpeech(true);
    console.log('VoiceChat: Generating speech for:', text.substring(0, 50) + '...');
    
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
        
        console.log('VoiceChat: Audio blob created, size:', blob.size);
        
        if (ttsAudioRef.current) {
          // Reset audio element
          ttsAudioRef.current.pause();
          ttsAudioRef.current.currentTime = 0;
          
          ttsAudioRef.current.onloadeddata = () => {
            console.log('VoiceChat: Audio loaded, attempting to play...');
            setIsSpeaking(true);
            ttsAudioRef.current.play()
              .then(() => {
                console.log('VoiceChat: Audio playing successfully');
              })
              .catch(err => {
                console.error('VoiceChat: Audio play error:', err);
                setIsSpeaking(false);
                alert('Audio play failed. Click anywhere on the page first to enable audio.');
              });
          };
          
          ttsAudioRef.current.onended = () => {
            console.log('VoiceChat: Audio playback ended');
            setIsSpeaking(false);
            URL.revokeObjectURL(url);
          };
          
          ttsAudioRef.current.onerror = (e) => {
            console.error('VoiceChat: Audio playback error:', e);
            setIsSpeaking(false);
            URL.revokeObjectURL(url);
          };
          
          ttsAudioRef.current.oncanplay = () => {
            console.log('VoiceChat: Audio can play');
          };
          
          // Set source and load
          ttsAudioRef.current.src = url;
          ttsAudioRef.current.load();
        }
      } else {
        console.error('VoiceChat: TTS API error:', response.status, await response.text());
      }
    } catch (error) {
      console.error('VoiceChat: Error generating speech:', error);
    } finally {
      setIsGeneratingSpeech(false);
    }
  };

  const handleToggleListening = () => {
    if (isListening) {
      console.log('Stopping voice recognition...');
      // Stop recording and send message if there's text
      if (transcribedText.trim()) {
        handleVoiceMessage(transcribedText);
      } else {
        forceStopListening();
      }
    } else {
      console.log('Starting voice recognition...');
      startListening();
    }
  };

  const forceStopListening = () => {
    try {
      setIsManuallyStopped(true);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current.abort();
      }
    } catch (error) {
      console.error('Error force stopping recognition:', error);
    }
    setIsListening(false);
    setIsTranscribing(false);
    setTranscribedText('');
  };

  const startContinuousListening = () => {
    startListening();
  };

  const handleClose = () => {
    forceStopListening();
    setTranscribedText('');
    setConversationHistory([]);
    setIsListening(false);
    setIsSpeaking(false);
    setIsTranscribing(false);
    setIsGeneratingSpeech(false);
    setIsManuallyStopped(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[95vh] overflow-hidden border border-gray-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-purple-700 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <Waves className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Voice Conversation</h2>
                <p className="text-purple-100 text-sm">Talk naturally with your AI assistant</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-white/20 rounded-full transition-all duration-200 hover:scale-110"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        <div className="flex flex-col h-[calc(95vh-88px)]">
          {/* Conversation Area */}
          <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-gray-50 to-white voice-chat-scrollbar">
            <div className="max-w-3xl mx-auto space-y-4">
              {conversationHistory.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                    <Sparkles className="h-10 w-10 text-purple-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-3">
                    Start Your Voice Journey
                  </h3>
                  <p className="text-gray-600 text-lg mb-6 max-w-md mx-auto">
                    Click the microphone below and start talking naturally. Your AI assistant will respond with voice.
                  </p>
                  <div className="flex items-center justify-center space-x-2 text-purple-600">
                    <Mic className="h-5 w-5" />
                    <span className="font-medium">Voice conversation ready</span>
                  </div>
                </div>
              ) : (
                conversationHistory.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} message-bubble`}
                  >
                    <div className={`max-w-[85%] ${message.sender === 'user' ? 'text-right' : 'text-left'}`}>
                      <div className={`inline-block p-4 rounded-2xl shadow-lg backdrop-blur-sm ${
                        message.sender === 'user'
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                          : message.isError
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : 'bg-white text-gray-800 border border-gray-100'
                      }`}>
                        <p className="text-sm leading-relaxed">{message.text}</p>
                        {message.type === 'voice' && (
                          <div className="flex items-center mt-2 text-xs opacity-75">
                            {message.sender === 'user' ? (
                              <>
                                <Mic className="h-3 w-3 mr-1" />
                                You spoke
                              </>
                            ) : (
                              <>
                                <Volume2 className="h-3 w-3 mr-1" />
                                AI spoke
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Voice Control Area */}
          <div className="border-t border-gray-200 bg-white p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Live Transcription */}
              {transcribedText && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-4 border border-blue-100 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-blue-700">Live Transcription</span>
                    </div>
                    <button
                      onClick={() => handleVoiceMessage(transcribedText)}
                      disabled={isGeneratingSpeech || isLoading}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-full text-xs font-medium transition-colors disabled:opacity-50"
                    >
                      Send Now
                    </button>
                  </div>
                  <p className="text-blue-800 text-sm leading-relaxed">{transcribedText}</p>
                </div>
              )}

              {/* Voice Control Center */}
              <div className="flex flex-col items-center space-y-4">
                {/* Main Mic Button */}
                <div className="relative">
                  <button
                    onClick={handleToggleListening}
                    disabled={isGeneratingSpeech || isLoading}
                    className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 shadow-2xl voice-button-hover ${
                      isListening
                        ? 'bg-gradient-to-r from-red-500 to-red-600 text-white scale-110 recording-pulse'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:scale-105'
                    } ${(isGeneratingSpeech || isLoading) ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-xl'}`}
                  >
                    {isListening ? <MicOff className="h-8 w-8" /> : <Mic className="h-8 w-8" />}
                  </button>
                  
                  {/* Animated rings when listening */}
                  {isListening && (
                    <>
                      <div className="absolute inset-0 w-20 h-20 rounded-full border-2 border-red-400 animate-ping"></div>
                      <div className="absolute inset-0 w-20 h-20 rounded-full border-2 border-red-300 animate-ping" style={{animationDelay: '0.5s'}}></div>
                    </>
                  )}
                </div>

                {/* Status Indicators */}
                <div className="flex items-center justify-center space-x-6">
                  {isTranscribing && (
                    <div className="flex items-center space-x-2 text-blue-600 bg-blue-50 px-3 py-2 rounded-full">
                      <Loader className="h-4 w-4 animate-spin" />
                      <span className="text-sm font-medium">Listening...</span>
                    </div>
                  )}

                  {isGeneratingSpeech && (
                    <div className="flex items-center space-x-2 text-purple-600 bg-purple-50 px-3 py-2 rounded-full">
                      <Loader className="h-4 w-4 animate-spin" />
                      <span className="text-sm font-medium">AI is thinking...</span>
                    </div>
                  )}

                  {isSpeaking && (
                    <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-3 py-2 rounded-full">
                      <Volume2 className="h-4 w-4" />
                      <span className="text-sm font-medium">AI speaking</span>
                    </div>
                  )}
                </div>

                {/* Instructions */}
                <div className="text-center">
                  <p className="text-sm text-gray-600 font-medium">
                    {isListening 
                      ? '🎤 Click again to stop and send message' 
                      : '🎤 Click to start recording'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {isListening 
                      ? 'Speak your message, then click the button to send' 
                      : 'Record your voice message manually'}
                  </p>
                </div>

                {/* Language Selector */}
                <div className="flex items-center justify-center space-x-2 mt-4">
                  <span className="text-sm text-gray-600">Language:</span>
                  <select
                    value={sttLang}
                    onChange={(e) => setSttLang(e.target.value)}
                    className="p-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="vi-VN">Tiếng Việt</option>
                    <option value="es-ES">Español</option>
                    <option value="fr-FR">Français</option>
                    <option value="de-DE">Deutsch</option>
                    <option value="ja-JP">日本語</option>
                    <option value="ko-KR">한국어</option>
                    <option value="zh-CN">中文</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <audio ref={ttsAudioRef} preload="auto" crossOrigin="anonymous" />
      </div>
    </div>
  );
};

export default VoiceChat; 