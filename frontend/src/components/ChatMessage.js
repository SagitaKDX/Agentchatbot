import React from 'react';
import { Bot, User, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message }) => {
  const isAI = message.sender === 'ai';
  const isError = message.isError;

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex ${isAI ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`flex max-w-3xl ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
        <div className={`flex-shrink-0 ${isAI ? 'mr-3' : 'ml-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isAI 
              ? isError 
                ? 'bg-red-100' 
                : 'bg-primary-100' 
              : 'bg-gray-100'
          }`}>
            {isAI ? (
              isError ? (
                <AlertCircle className="h-5 w-5 text-red-600" />
              ) : (
                <Bot className="h-5 w-5 text-primary-600" />
              )
            ) : (
              <User className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        
        <div className={`flex flex-col ${isAI ? 'items-start' : 'items-end'}`}>
          <div className={`rounded-lg px-4 py-2 max-w-full ${
            isAI 
              ? isError
                ? 'bg-red-50 border border-red-200'
                : 'bg-gray-100'
              : 'bg-primary-600 text-white'
          }`}>
            {isAI && !isError ? (
              <ReactMarkdown className="prose prose-sm max-w-none">
                {message.text}
              </ReactMarkdown>
            ) : (
              <p className={`text-sm ${isError ? 'text-red-800' : ''}`}>
                {message.text}
              </p>
            )}
          </div>
          
          {message.suggestions && message.suggestions.length > 0 && (
            <div className="mt-2 space-y-1">
              <p className="text-xs text-gray-500">Suggested follow-ups:</p>
              {message.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="block text-left text-xs text-primary-600 hover:text-primary-800 bg-primary-50 hover:bg-primary-100 px-2 py-1 rounded transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          
          <span className="text-xs text-gray-500 mt-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 