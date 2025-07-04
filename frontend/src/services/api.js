import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
    }
    return Promise.reject(error);
  }
);

export const chatAPI = {
  sendMessage: async (message, conversationHistory = [], context = '') => {
    try {
      const response = await api.post('/api/chat/message', {
        message,
        conversationHistory: conversationHistory.slice(-10),
        context,
        timestamp: new Date().toISOString()
      });
      
      if (response.data.success) {
        return {
          text: response.data.data.message,
          timestamp: response.data.data.timestamp,
          usage: response.data.data.usage
        };
      } else {
        throw new Error(response.data.error || 'Failed to send message');
      }
    } catch (error) {
      console.error('Chat API error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to send message. Please try again.');
    }
  },

  generateLessonPlan: async (topic, level, duration) => {
    try {
      const response = await api.post('/api/chat/lesson-plan', {
        topic,
        level,
        duration
      });
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to generate lesson plan');
      }
    } catch (error) {
      console.error('Lesson plan API error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to generate lesson plan. Please try again.');
    }
  },

  checkHealth: async () => {
    try {
      const response = await api.get('/api/chat/health');
      return response.data;
    } catch (error) {
      console.error('Chat health check error:', error);
      throw new Error('Chat service is unavailable');
    }
  }
};

export const knowledgeBaseAPI = {
  uploadFiles: async (files, category = 'general', description = '') => {
    try {
      const formData = new FormData();
      
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });
      
      formData.append('category', category);
      formData.append('description', description);

      const response = await api.post('/api/knowledge/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000,
      });
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to upload files');
      }
    } catch (error) {
      console.error('File upload error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to upload files. Please try again.');
    }
  },

  getFiles: async () => {
    try {
      const response = await api.get('/api/knowledge/files');
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to fetch files');
      }
    } catch (error) {
      console.error('Get files error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to fetch files');
    }
  },

  deleteFile: async (fileId) => {
    try {
      const response = await api.delete(`/api/knowledge/files/${fileId}`);
      
      if (response.data.success) {
        return response.data;
      } else {
        throw new Error(response.data.error || 'Failed to delete file');
      }
    } catch (error) {
      console.error('Delete file error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to delete file');
    }
  },

  searchFiles: async (query, category = '') => {
    try {
      const response = await api.get('/api/knowledge/search', {
        params: { query, category }
      });
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Search failed');
      }
    } catch (error) {
      console.error('Search files error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Search failed');
    }
  },

  checkHealth: async () => {
    try {
      const response = await api.get('/api/knowledge/health');
      return response.data;
    } catch (error) {
      console.error('Knowledge base health check error:', error);
      throw new Error('Knowledge base service is unavailable');
    }
  }
};

export const agentAPI = {
  sendMessage: async (message, sessionId = null) => {
    try {
      const response = await api.post('/api/agent/chat', {
        message,
        session_id: sessionId
      });
      
      if (response.data.success) {
        return {
          message: response.data.data.message,
          sessionId: response.data.data.session_id,
          timestamp: response.data.data.timestamp,
          traceInfo: response.data.data.trace_info
        };
      } else {
        throw new Error(response.data.error || 'Failed to send message to agent');
      }
    } catch (error) {
      console.error('Agent API error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to send message to agent. Please try again.');
    }
  },

  createSession: async () => {
    try {
      const response = await api.post('/api/agent/session/new');
      
      if (response.data.success) {
        return {
          sessionId: response.data.data.session_id,
          createdAt: response.data.data.created_at,
          message: response.data.data.message
        };
      } else {
        throw new Error(response.data.error || 'Failed to create session');
      }
    } catch (error) {
      console.error('Create session error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to create session. Please try again.');
    }
  },

  getSessionInfo: async (sessionId) => {
    try {
      const response = await api.get(`/api/agent/session/${sessionId}`);
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to get session info');
      }
    } catch (error) {
      console.error('Get session info error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to get session info');
    }
  },

  listActiveSessions: async () => {
    try {
      const response = await api.get('/api/agent/sessions');
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to list sessions');
      }
    } catch (error) {
      console.error('List sessions error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to list sessions');
    }
  },

  cleanupSessions: async () => {
    try {
      const response = await api.post('/api/agent/sessions/cleanup');
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to cleanup sessions');
      }
    } catch (error) {
      console.error('Cleanup sessions error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to cleanup sessions');
    }
  },

  checkHealth: async () => {
    try {
      const response = await api.get('/api/agent/health');
      return response.data;
    } catch (error) {
      console.error('Agent health check error:', error);
      throw new Error('Agent service is unavailable');
    }
  },

  getSystemPrompt: async () => {
    try {
      const response = await api.get('/api/agent/system-prompt');
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to get system prompt');
      }
    } catch (error) {
      console.error('Get system prompt error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to get system prompt');
    }
  },

  updateSystemPrompt: async (prompt) => {
    try {
      const response = await api.put('/api/agent/system-prompt', {
        prompt: prompt
      });
      
      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to update system prompt');
      }
    } catch (error) {
      console.error('Update system prompt error:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to update system prompt');
    }
  }
};

export const systemAPI = {
  checkHealth: async () => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('System health check error:', error);
      throw new Error('Backend service is unavailable');
    }
  }
};

export default api; 