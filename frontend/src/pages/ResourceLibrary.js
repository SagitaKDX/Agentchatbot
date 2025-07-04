import React, { useState } from 'react';
import { Search, Filter, Download, Eye, BookOpen, FileText, Video, Headphones, Bot, Wifi, Cpu } from 'lucide-react';

const ResourceLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  const categories = [
    { id: 'all', name: 'All Categories', icon: null },
    { id: 'ai', name: 'Artificial Intelligence', icon: Bot },
    { id: 'iot', name: 'Internet of Things', icon: Wifi },
    { id: 'chips', name: 'Chip Technology', icon: Cpu },
  ];

  const resourceTypes = [
    { id: 'all', name: 'All Types' },
    { id: 'document', name: 'Documents' },
    { id: 'video', name: 'Videos' },
    { id: 'audio', name: 'Audio' },
    { id: 'interactive', name: 'Interactive' },
  ];

  const resources = [
    {
      id: 1,
      title: 'AI Terminology Glossary',
      category: 'ai',
      type: 'document',
      description: 'Comprehensive glossary of AI and machine learning terms',
      format: 'PDF',
      size: '2.5 MB',
      downloads: 156,
      level: 'All Levels',
      tags: ['vocabulary', 'reference', 'terminology']
    },
    {
      id: 2,
      title: 'IoT Pronunciation Guide',
      category: 'iot',
      type: 'audio',
      description: 'Audio guide for correct pronunciation of IoT technical terms',
      format: 'MP3',
      size: '45 MB',
      downloads: 89,
      level: 'Beginner',
      tags: ['pronunciation', 'speaking', 'audio']
    },
    {
      id: 3,
      title: 'Semiconductor Manufacturing Process',
      category: 'chips',
      type: 'video',
      description: 'Educational video explaining chip manufacturing processes',
      format: 'MP4',
      size: '128 MB',
      downloads: 234,
      level: 'Intermediate',
      tags: ['manufacturing', 'visual learning', 'process']
    },
    {
      id: 4,
      title: 'Interactive AI Ethics Scenarios',
      category: 'ai',
      type: 'interactive',
      description: 'Interactive scenarios for discussing AI ethics and implications',
      format: 'Web App',
      size: '5 MB',
      downloads: 67,
      level: 'Advanced',
      tags: ['ethics', 'discussion', 'scenarios']
    },
    {
      id: 5,
      title: 'IoT Security Vocabulary Worksheets',
      category: 'iot',
      type: 'document',
      description: 'Printable worksheets focusing on IoT security terminology',
      format: 'PDF',
      size: '1.8 MB',
      downloads: 123,
      level: 'Intermediate',
      tags: ['security', 'worksheet', 'practice']
    },
    {
      id: 6,
      title: 'Chip Design Process Infographic',
      category: 'chips',
      type: 'document',
      description: 'Visual guide to semiconductor design and development process',
      format: 'PNG',
      size: '3.2 MB',
      downloads: 198,
      level: 'All Levels',
      tags: ['design', 'visual', 'infographic']
    },
    {
      id: 7,
      title: 'Machine Learning Concepts Explained',
      category: 'ai',
      type: 'video',
      description: 'Video series explaining fundamental ML concepts in simple English',
      format: 'MP4',
      size: '256 MB',
      downloads: 345,
      level: 'Beginner',
      tags: ['machine learning', 'concepts', 'beginner-friendly']
    },
    {
      id: 8,
      title: 'Smart Home IoT Devices Discussion',
      category: 'iot',
      type: 'audio',
      description: 'Podcast-style discussion about common smart home devices',
      format: 'MP3',
      size: '67 MB',
      downloads: 78,
      level: 'Beginner',
      tags: ['smart home', 'devices', 'discussion']
    }
  ];

  const getTypeIcon = (type) => {
    switch (type) {
      case 'document': return FileText;
      case 'video': return Video;
      case 'audio': return Headphones;
      case 'interactive': return BookOpen;
      default: return FileText;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'document': return 'bg-blue-100 text-blue-800';
      case 'video': return 'bg-red-100 text-red-800';
      case 'audio': return 'bg-green-100 text-green-800';
      case 'interactive': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || resource.category === selectedCategory;
    const matchesType = selectedType === 'all' || resource.type === selectedType;
    return matchesSearch && matchesCategory && matchesType;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Resource Library</h1>
        <p className="mt-2 text-gray-600">Curated teaching materials for technical English instruction</p>
      </div>

      <div className="mb-8 space-y-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search resources, tags, or descriptions..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-4">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {resourceTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredResources.map((resource) => {
          const TypeIcon = getTypeIcon(resource.type);
          const categoryData = categories.find(cat => cat.id === resource.category);
          const CategoryIcon = categoryData?.icon;

          return (
            <div key={resource.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    {CategoryIcon && <CategoryIcon className="h-5 w-5 text-primary-600" />}
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(resource.type)}`}>
                      <TypeIcon className="h-3 w-3 inline mr-1" />
                      {resource.format}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">{resource.size}</span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">{resource.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{resource.description}</p>

                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                    <span>Level: {resource.level}</span>
                    <span>{resource.downloads} downloads</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {resource.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center justify-center">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </button>
                  <button className="bg-gray-100 text-gray-700 py-2 px-3 rounded-lg hover:bg-gray-200 transition-colors">
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredResources.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-16 w-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
          <p className="text-gray-600">Try adjusting your search terms or filters.</p>
        </div>
      )}
    </div>
  );
};

export default ResourceLibrary; 