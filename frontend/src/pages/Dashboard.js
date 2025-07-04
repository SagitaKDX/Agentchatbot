import React from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, BookOpen, Library, Users, TrendingUp, Clock } from 'lucide-react';

const Dashboard = () => {
  const stats = [
    { label: 'Total Conversations', value: '156', icon: MessageCircle, change: '+12%' },
    { label: 'Active Modules', value: '8', icon: BookOpen, change: '+3%' },
    { label: 'Resources Accessed', value: '45', icon: Library, change: '+8%' },
    { label: 'Students Helped', value: '23', icon: Users, change: '+15%' },
  ];

  const quickActions = [
    {
      title: 'Start AI Chat',
      description: 'Get help with lesson planning and technical vocabulary',
      path: '/chat',
      icon: MessageCircle,
      color: 'bg-blue-500'
    },
    {
      title: 'Browse Topic Modules',
      description: 'Explore structured lessons on AI, IoT, and Chip Technology',
      path: '/modules',
      icon: BookOpen,
      color: 'bg-green-500'
    },
    {
      title: 'Resource Library',
      description: 'Access curated materials and teaching resources',
      path: '/resources',
      icon: Library,
      color: 'bg-purple-500'
    }
  ];

  const recentActivity = [
    { action: 'Completed IoT Vocabulary Module', time: '2 hours ago' },
    { action: 'Started AI Ethics Discussion', time: '4 hours ago' },
    { action: 'Uploaded new reading material', time: '1 day ago' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-8">
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm md:text-base text-gray-600">Welcome to your English AI Agent teaching assistant</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow p-4 md:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-6 w-6 md:h-8 md:w-8 text-gray-400" />
              </div>
              <div className="ml-3 md:ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-xs md:text-sm font-medium text-gray-500 truncate">{stat.label}</dt>
                  <dd className="flex items-baseline">
                    <div className="text-lg md:text-2xl font-semibold text-gray-900">{stat.value}</div>
                    <div className="ml-2 flex items-baseline text-xs md:text-sm font-semibold text-green-600">
                      <TrendingUp className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 mb-6 md:mb-8">
        <div className="lg:col-span-2">
          <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4 md:mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {quickActions.map((action) => (
              <Link
                key={action.title}
                to={action.path}
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-4 md:p-6 group"
              >
                <div className="flex items-center mb-3 md:mb-4">
                  <div className={`${action.color} rounded-lg p-2 md:p-3`}>
                    <action.icon className="h-5 w-5 md:h-6 md:w-6 text-white" />
                  </div>
                </div>
                <h3 className="text-base md:text-lg font-medium text-gray-900 group-hover:text-primary-600">
                  {action.title}
                </h3>
                <p className="text-gray-600 text-xs md:text-sm mt-2">{action.description}</p>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4 md:mb-6">Recent Activity</h2>
          <div className="bg-white rounded-lg shadow">
            {recentActivity.map((activity, index) => (
              <div key={index} className="p-3 md:p-4 border-b border-gray-100 last:border-b-0">
                <div className="flex items-start">
                  <Clock className="h-4 w-4 md:h-5 md:w-5 text-gray-400 mt-0.5" />
                  <div className="ml-2 md:ml-3">
                    <p className="text-xs md:text-sm text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 