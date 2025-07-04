import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageCircle, BookOpen } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 border-b border-blue-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex items-center space-x-2 md:space-x-3">
              <div className="w-8 h-8 md:w-10 md:h-10 bg-white rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-blue-600 font-bold text-sm md:text-lg">B</span>
              </div>
              <h1 className="text-lg md:text-xl font-bold text-white truncate">Bedrock AI Agent</h1>
            </div>
          </div>
          <div className="flex space-x-1 md:space-x-2">
            <Link
              to="/"
              className={`inline-flex items-center px-2 md:px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition-all duration-200 ${
                isActive('/')
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'text-blue-100 hover:text-white hover:bg-white hover:bg-opacity-20'
              }`}
            >
              <MessageCircle className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
              <span className="hidden sm:inline">Chat</span>
            </Link>
            <Link
              to="/knowledge-base"
              className={`inline-flex items-center px-2 md:px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition-all duration-200 ${
                isActive('/knowledge-base')
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'text-blue-100 hover:text-white hover:bg-white hover:bg-opacity-20'
              }`}
            >
              <BookOpen className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
              <span className="hidden sm:inline">Knowledge Base</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 