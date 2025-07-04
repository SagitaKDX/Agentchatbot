import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ChatInterface from './pages/ChatInterface';
import KnowledgeBase from './pages/KnowledgeBase';
import Navigation from './components/Navigation';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="/knowledge-base" element={<KnowledgeBase />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 