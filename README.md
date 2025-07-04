# English AI Agent

A full-stack application for the English AI Agent, designed to assist English teachers in delivering both general and academic English instruction with an emphasis on chip technology, artificial intelligence (AI), and the Internet of Things (IoT).

## Project Structure

```
EnglishAgent/
├── frontend/           # React.js frontend application
│   ├── src/           # React components and pages
│   ├── public/        # Static assets
│   ├── node_modules/  # Frontend dependencies
│   └── package.json   # Frontend dependencies config
├── backend/           # Python Flask backend with AWS Bedrock (Boto3)
│   ├── routes/        # Flask API blueprints
│   ├── services/      # Business logic and AWS Bedrock integration
│   ├── middleware/    # Flask middleware
│   ├── venv/          # Python virtual environment
│   ├── requirements.txt # Python dependencies
│   └── app.py         # Main Flask application
└── README.md          # This file
```

## Features

### 🤖 AI Chat Interface
- Real-time conversation with AI agent specialized in technical English
- Topic-specific assistance (AI, IoT, Chip Technology)
- Contextual suggestions and follow-up questions
- Message history and conversation management

### 📚 Topic Modules
- Structured learning modules for technical English topics
- Progressive difficulty levels (Beginner, Intermediate, Advanced)
- Interactive lessons with vocabulary, reading comprehension, and writing support
- Progress tracking and enrollment management

### 📖 Resource Library
- Curated teaching materials and resources
- Multiple format support (PDF, Video, Audio, Interactive)
- Advanced search and filtering capabilities
- Download and favorite management

### 📊 Teacher Dashboard
- Usage analytics and student progress tracking
- Recent activity monitoring
- Quick action buttons for common tasks
- Performance metrics and insights

## Technology Stack

### Frontend
- **Framework**: React 18, React Router DOM
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Markdown**: React Markdown
- **Animations**: Framer Motion

### Backend
- **Framework**: Python Flask
- **AWS Integration**: Boto3 (AWS SDK for Python)
- **AI Models**: AWS Bedrock (Anthropic Claude)
- **Document Processing**: PyPDF2, python-docx
- **Validation**: Marshmallow
- **Rate Limiting**: Flask-Limiter

## Prerequisites

- **Frontend**: Node.js (version 16 or higher), npm or yarn package manager
- **Backend**: Python 3.8 or higher, pip package manager
- **AWS**: Valid AWS credentials with Bedrock access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EnglishAgent
```

2. Setup Python backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your AWS credentials and configuration
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

## Development

### Start the Backend Server
```bash
cd backend
source venv/bin/activate
python app.py
```
Or simply:
```bash
cd backend
source venv/bin/activate && python app.py
```
The backend API will be available at `http://localhost:5000`.

### Start the Frontend Development Server
```bash
cd frontend
npm start
```
The frontend application will be available at `http://localhost:3000`.

## Build

Create a production build of the frontend:
```bash
cd frontend
npm run build
```

## API Integration

The frontend integrates with a backend API that uses:

### AWS Services
- **AWS Bedrock**: For AI/LLM capabilities
- **Amazon S3**: Vector database for knowledge storage
- **AWS Lambda**: Serverless backend functions
- **Amazon API Gateway**: API management

### API Endpoints

#### Chat API
- `POST /api/chat` - Send message to AI agent
- `GET /api/chat/history` - Retrieve conversation history
- `GET /api/chat/suggestions` - Get topic-specific suggestions

#### Modules API
- `GET /api/modules` - Retrieve learning modules
- `GET /api/modules/{id}` - Get specific module content
- `POST /api/modules/{id}/enroll` - Enroll in a module
- `PATCH /api/modules/{id}/progress` - Update learning progress

#### Resources API
- `GET /api/resources` - Retrieve teaching resources
- `GET /api/resources/{id}/download` - Download resource file
- `POST /api/resources/upload` - Upload new resource
- `GET /api/resources/favorites` - Get user's favorite resources

#### Knowledge Base API
- `POST /api/knowledge/search` - Search vector database
- `GET /api/knowledge/related` - Get related terms

#### Analytics API
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/usage` - Usage analytics

## Detailed Frontend Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.js       # Navigation header
│   │   ├── ChatMessage.js  # Chat message component
│   │   └── TopicSelector.js # Topic selection dropdown
│   ├── pages/              # Main application pages
│   │   ├── Dashboard.js    # Teacher dashboard
│   │   ├── ChatInterface.js # AI chat interface
│   │   ├── TopicModules.js # Learning modules
│   │   └── ResourceLibrary.js # Teaching resources
│   ├── services/           # API service layer
│   │   └── api.js         # API client and endpoints
│   ├── App.js             # Main application component
│   ├── index.js           # Application entry point
│   └── index.css          # Global styles
├── public/                 # Static assets
├── package.json           # Frontend dependencies
└── tailwind.config.js     # Tailwind CSS configuration
```

## Key Features Explained

### Chat Interface
The chat interface provides real-time communication with the AI agent. Teachers can:
- Ask questions about lesson planning
- Get help with technical vocabulary explanations
- Receive suggestions for teaching methods
- Access topic-specific guidance

### Topic Modules
Structured learning modules covering:
- **AI Topics**: Machine learning, neural networks, AI ethics
- **IoT Topics**: Sensor technology, smart cities, security
- **Chip Technology**: Semiconductor design, manufacturing processes

### Resource Management
The resource library offers:
- Searchable content by category, type, and keywords
- Multiple file formats support
- Download tracking and analytics
- User favorites and collections

## Responsive Design

The application is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile devices

## Accessibility

The application follows WCAG guidelines for:
- Keyboard navigation
- Screen reader compatibility
- Color contrast standards
- Focus management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository. 