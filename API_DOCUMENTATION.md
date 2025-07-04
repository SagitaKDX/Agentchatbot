# English AI Agent - API Documentation

This document provides comprehensive documentation for the backend API that powers the English AI Agent application. The backend uses AWS services including Bedrock for AI capabilities and S3 for vector database storage.

## Base URL
```
Production: https://api.english-ai-agent.com
Development: http://localhost:3001
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { ... }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### 1. Chat API

#### Send Message to AI Agent
```http
POST /api/chat
```

**Request Body:**
```json
{
  "message": "How can I explain neural networks to beginner students?",
  "topic": "ai",
  "conversationHistory": [
    {
      "id": 1,
      "text": "Previous message",
      "sender": "user",
      "timestamp": "2024-01-15T10:25:00Z"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Neural networks are like interconnected nodes...",
    "suggestions": [
      "Would you like examples of simple neural network analogies?",
      "How about visual aids for teaching neural networks?"
    ],
    "topic": "ai",
    "confidence": 0.95,
    "sources": ["bedrock_ai", "vector_db"]
  }
}
```

#### Get Conversation History
```http
GET /api/chat/history?limit=50&offset=0
```

**Response:**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_123",
        "messages": [...],
        "topic": "ai",
        "createdAt": "2024-01-15T10:00:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "totalCount": 25,
    "hasMore": false
  }
}
```

#### Get Topic Suggestions
```http
GET /api/chat/suggestions?topic=ai
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      "How to teach machine learning concepts?",
      "Best practices for AI vocabulary instruction",
      "Interactive AI ethics discussion topics"
    ]
  }
}
```

### 2. Modules API

#### Get Learning Modules
```http
GET /api/modules?category=ai&search=neural&level=beginner
```

**Query Parameters:**
- `category`: ai, iot, chips, all (default: all)
- `search`: Search term for module title/description
- `level`: beginner, intermediate, advanced
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "modules": [
      {
        "id": "mod_001",
        "title": "Introduction to AI Vocabulary",
        "description": "Essential AI terms and concepts for beginners",
        "category": "ai",
        "level": "beginner",
        "duration": "45 minutes",
        "lessonsCount": 4,
        "enrolledStudents": 23,
        "rating": 4.8,
        "thumbnailUrl": "https://s3.../thumbnail.jpg",
        "createdAt": "2024-01-01T00:00:00Z"
      }
    ],
    "totalCount": 15,
    "hasMore": true
  }
}
```

#### Get Module Content
```http
GET /api/modules/{moduleId}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "module": {
      "id": "mod_001",
      "title": "Introduction to AI Vocabulary",
      "description": "Essential AI terms and concepts for beginners",
      "lessons": [
        {
          "id": "lesson_001",
          "title": "Machine Learning Basics",
          "content": "...",
          "duration": "10 minutes",
          "resources": ["res_001", "res_002"],
          "quiz": {...}
        }
      ],
      "prerequisites": [],
      "learningObjectives": [...],
      "assessments": [...]
    }
  }
}
```

#### Enroll in Module
```http
POST /api/modules/{moduleId}/enroll
```

**Response:**
```json
{
  "success": true,
  "data": {
    "enrollment": {
      "id": "enroll_001",
      "moduleId": "mod_001",
      "userId": "user_123",
      "progress": 0,
      "enrolledAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Update Module Progress
```http
PATCH /api/modules/{moduleId}/progress
```

**Request Body:**
```json
{
  "lessonId": "lesson_001",
  "completed": true,
  "timeSpent": 600,
  "score": 85,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Resources API

#### Get Teaching Resources
```http
GET /api/resources?category=ai&type=document&search=vocabulary
```

**Query Parameters:**
- `category`: ai, iot, chips, all
- `type`: document, video, audio, interactive, all
- `search`: Search term
- `level`: beginner, intermediate, advanced, all
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "resources": [
      {
        "id": "res_001",
        "title": "AI Terminology Glossary",
        "description": "Comprehensive glossary of AI terms",
        "category": "ai",
        "type": "document",
        "format": "PDF",
        "fileSize": "2.5 MB",
        "downloadUrl": "https://s3.../resource.pdf",
        "thumbnailUrl": "https://s3.../thumbnail.jpg",
        "downloads": 156,
        "rating": 4.7,
        "level": "all",
        "tags": ["vocabulary", "reference", "terminology"],
        "createdAt": "2024-01-01T00:00:00Z"
      }
    ],
    "totalCount": 45,
    "hasMore": true
  }
}
```

#### Download Resource
```http
GET /api/resources/{resourceId}/download
```

**Response:** Binary file data with appropriate Content-Type headers

#### Upload Resource
```http
POST /api/resources/upload
```

**Request:** multipart/form-data
- `file`: The resource file
- `title`: Resource title
- `description`: Resource description
- `category`: Resource category
- `type`: Resource type
- `level`: Difficulty level
- `tags`: Comma-separated tags

#### Get Favorite Resources
```http
GET /api/resources/favorites
```

### 4. Knowledge Base API

#### Search Vector Database
```http
POST /api/knowledge/search
```

**Request Body:**
```json
{
  "query": "semiconductor manufacturing process",
  "topic": "chips",
  "limit": 10,
  "threshold": 0.7,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "kb_001",
        "content": "Semiconductor manufacturing involves...",
        "similarity": 0.95,
        "source": "technical_manual_v2.pdf",
        "metadata": {
          "topic": "chips",
          "level": "advanced",
          "lastUpdated": "2024-01-10T00:00:00Z"
        }
      }
    ],
    "totalFound": 15,
    "searchTime": "0.045s"
  }
}
```

#### Get Related Terms
```http
GET /api/knowledge/related?term=neural network&topic=ai&limit=5
```

**Response:**
```json
{
  "success": true,
  "data": {
    "relatedTerms": [
      {
        "term": "deep learning",
        "similarity": 0.89,
        "definition": "A subset of machine learning..."
      },
      {
        "term": "artificial neuron",
        "similarity": 0.85,
        "definition": "The basic unit of a neural network..."
      }
    ]
  }
}
```

### 5. Analytics API

#### Get Dashboard Statistics
```http
GET /api/analytics/dashboard
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stats": {
      "totalConversations": 156,
      "activeModules": 8,
      "resourcesAccessed": 45,
      "studentsHelped": 23,
      "avgSessionDuration": "12m 34s",
      "popularTopics": ["ai", "iot", "chips"],
      "recentActivity": [
        {
          "action": "Completed IoT Module",
          "timestamp": "2024-01-15T08:30:00Z",
          "user": "teacher_001"
        }
      ]
    },
    "trends": {
      "conversationsGrowth": "+12%",
      "moduleCompletions": "+8%",
      "resourceDownloads": "+15%"
    }
  }
}
```

#### Get Usage Analytics
```http
GET /api/analytics/usage?range=7d&granularity=day
```

**Query Parameters:**
- `range`: 1d, 7d, 30d, 90d
- `granularity`: hour, day, week
- `metric`: conversations, modules, resources, all

**Response:**
```json
{
  "success": true,
  "data": {
    "usage": [
      {
        "date": "2024-01-15",
        "conversations": 25,
        "moduleAccess": 12,
        "resourceDownloads": 8,
        "uniqueUsers": 15
      }
    ],
    "summary": {
      "totalConversations": 175,
      "avgDaily": 25,
      "peakDay": "2024-01-15",
      "trendDirection": "up"
    }
  }
}
```

## AWS Integration Details

### AWS Bedrock Integration

The API integrates with AWS Bedrock for AI capabilities:

**Model Used:** `anthropic.claude-3-sonnet-20240229-v1:0`

**Request to Bedrock:**
```json
{
  "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
  "contentType": "application/json",
  "accept": "application/json",
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
      {
        "role": "user",
        "content": "Enhanced prompt with context..."
      }
    ],
    "system": "You are an English teaching assistant specializing in technical topics..."
  }
}
```

### S3 Vector Database

Vector embeddings are stored in S3 with the following structure:

```
s3://english-ai-agent-resources/
├── vectors/
│   ├── ai/
│   │   ├── embeddings.json
│   │   └── metadata.json
│   ├── iot/
│   └── chips/
├── resources/
│   ├── documents/
│   ├── videos/
│   └── audio/
└── modules/
    ├── content/
    └── assessments/
```

**Vector Search Process:**
1. Query text is embedded using AWS Bedrock
2. Similarity search performed against S3 vectors
3. Top-k results returned with metadata
4. Results used to enhance AI responses

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid or missing authentication token |
| AUTH_002 | Token expired |
| AUTH_003 | Insufficient permissions |
| CHAT_001 | Invalid message format |
| CHAT_002 | Topic not supported |
| CHAT_003 | Conversation history too long |
| MODULE_001 | Module not found |
| MODULE_002 | Already enrolled in module |
| RESOURCE_001 | Resource not found |
| RESOURCE_002 | File too large |
| VECTOR_001 | Search query too short |
| VECTOR_002 | No results found |
| AWS_001 | Bedrock service unavailable |
| AWS_002 | S3 access denied |

## Rate Limiting

- **Chat API**: 60 requests per minute per user
- **Search API**: 30 requests per minute per user
- **Upload API**: 10 requests per minute per user
- **Other APIs**: 100 requests per minute per user

## Webhooks

The API supports webhooks for real-time notifications:

```http
POST /api/webhooks/register
```

**Events:**
- `module.completed`
- `resource.downloaded`
- `chat.session_started`
- `analytics.daily_report`

## SDK Examples

### JavaScript/Node.js
```javascript
const EnglishAIAgent = require('english-ai-agent-sdk');

const client = new EnglishAIAgent({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.english-ai-agent.com'
});

// Send chat message
const response = await client.chat.sendMessage({
  message: 'How to teach AI concepts?',
  topic: 'ai'
});
```

### Python
```python
from english_ai_agent import Client

client = Client(
    api_key='your-api-key',
    base_url='https://api.english-ai-agent.com'
)

# Search knowledge base
results = client.knowledge.search(
    query='semiconductor manufacturing',
    topic='chips'
)
```

## Support

For API support:
- Email: api-support@english-ai-agent.com
- Documentation: https://docs.english-ai-agent.com
- Status Page: https://status.english-ai-agent.com 