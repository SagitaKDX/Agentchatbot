import React, { useState } from 'react';
import { Bot, Wifi, Cpu, ChevronRight, Clock, Users, Star } from 'lucide-react';

const TopicModules = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const categories = [
    { id: 'all', name: 'All Topics', icon: null },
    { id: 'ai', name: 'Artificial Intelligence', icon: Bot },
    { id: 'iot', name: 'Internet of Things', icon: Wifi },
    { id: 'chips', name: 'Chip Technology', icon: Cpu },
  ];

  const modules = [
    {
      id: 1,
      title: 'Introduction to AI Vocabulary',
      category: 'ai',
      description: 'Essential AI terms and concepts for beginners',
      duration: '45 minutes',
      level: 'Beginner',
      students: 23,
      rating: 4.8,
      lessons: [
        'Machine Learning Basics',
        'Neural Networks Terminology',
        'AI Ethics Vocabulary',
        'Practical Applications'
      ]
    },
    {
      id: 2,
      title: 'IoT Communication Patterns',
      category: 'iot',
      description: 'Teaching effective communication about IoT systems',
      duration: '60 minutes',
      level: 'Intermediate',
      students: 18,
      rating: 4.7,
      lessons: [
        'Sensor Technology Terms',
        'Network Protocols',
        'Data Flow Concepts',
        'Security Vocabulary'
      ]
    },
    {
      id: 3,
      title: 'Semiconductor Industry English',
      category: 'chips',
      description: 'Technical English for chip design and manufacturing',
      duration: '75 minutes',
      level: 'Advanced',
      students: 15,
      rating: 4.9,
      lessons: [
        'Manufacturing Processes',
        'Design Terminology',
        'Quality Control Language',
        'Industry Standards'
      ]
    },
    {
      id: 4,
      title: 'AI Ethics and Society',
      category: 'ai',
      description: 'Discussing AI impact and ethical considerations',
      duration: '50 minutes',
      level: 'Intermediate',
      students: 31,
      rating: 4.6,
      lessons: [
        'Bias in AI Systems',
        'Privacy Concerns',
        'Future of Work',
        'Regulatory Framework'
      ]
    },
    {
      id: 5,
      title: 'Smart City IoT Solutions',
      category: 'iot',
      description: 'Urban IoT applications and smart city vocabulary',
      duration: '40 minutes',
      level: 'Beginner',
      students: 27,
      rating: 4.5,
      lessons: [
        'Smart Transportation',
        'Energy Management',
        'Waste Management',
        'Public Safety Systems'
      ]
    },
    {
      id: 6,
      title: 'Advanced Chip Architecture',
      category: 'chips',
      description: 'Complex semiconductor concepts and terminology',
      duration: '90 minutes',
      level: 'Advanced',
      students: 12,
      rating: 4.8,
      lessons: [
        'CPU Architecture',
        'GPU Design Principles',
        'Memory Systems',
        'Performance Optimization'
      ]
    }
  ];

  const filteredModules = modules.filter(module => {
    const matchesCategory = selectedCategory === 'all' || module.category === selectedCategory;
    const matchesSearch = module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         module.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getLevelColor = (level) => {
    switch (level) {
      case 'Beginner': return 'bg-green-100 text-green-800';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'Advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category) => {
    const categoryData = categories.find(cat => cat.id === category);
    return categoryData?.icon;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Topic Modules</h1>
        <p className="mt-2 text-gray-600">Structured learning modules for technical English instruction</p>
      </div>

      <div className="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.icon && <category.icon className="h-4 w-4 mr-2" />}
              {category.name}
            </button>
          ))}
        </div>

        <div className="lg:w-80">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search modules..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredModules.map((module) => {
          const CategoryIcon = getCategoryIcon(module.category);
          return (
            <div key={module.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    {CategoryIcon && <CategoryIcon className="h-6 w-6 text-primary-600 mr-2" />}
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLevelColor(module.level)}`}>
                      {module.level}
                    </span>
                  </div>
                  <div className="flex items-center text-yellow-400">
                    <Star className="h-4 w-4 fill-current" />
                    <span className="ml-1 text-sm text-gray-600">{module.rating}</span>
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">{module.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{module.description}</p>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <Clock className="h-4 w-4 mr-2" />
                    {module.duration}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Users className="h-4 w-4 mr-2" />
                    {module.students} students enrolled
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">What you'll learn:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {module.lessons.slice(0, 3).map((lesson, index) => (
                      <li key={index} className="flex items-center">
                        <ChevronRight className="h-3 w-3 mr-2" />
                        {lesson}
                      </li>
                    ))}
                    {module.lessons.length > 3 && (
                      <li className="text-gray-400">+{module.lessons.length - 3} more lessons</li>
                    )}
                  </ul>
                </div>

                <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors font-medium">
                  Start Module
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filteredModules.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Bot className="h-16 w-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No modules found</h3>
          <p className="text-gray-600">Try adjusting your search or category filter.</p>
        </div>
      )}
    </div>
  );
};

export default TopicModules; 