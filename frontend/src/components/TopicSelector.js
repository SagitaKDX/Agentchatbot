import React from 'react';
import { ChevronDown } from 'lucide-react';

const TopicSelector = ({ topics, selectedTopic, onTopicChange }) => {
  const selectedTopicData = topics.find(topic => topic.id === selectedTopic);

  return (
    <div className="relative">
      <select
        value={selectedTopic}
        onChange={(e) => onTopicChange(e.target.value)}
        className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        {topics.map((topic) => (
          <option key={topic.id} value={topic.id}>
            {topic.name}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
    </div>
  );
};

export default TopicSelector; 