# Veron English AI Agent - Backend

This is the backend API server for the Veron English AI Agent, providing integration with AWS Bedrock for AI-powered English teaching assistance and AWS S3 for knowledge base file storage.

## Features

- **AWS Bedrock Integration**: Powered by Claude 3 for intelligent English teaching assistance
- **Knowledge Base**: Upload and process PDF/Word documents using AWS S3
- **Document Analysis**: AI-powered analysis of teaching materials
- **Secure File Handling**: Encrypted file storage and processing
- **RESTful API**: Clean API endpoints for frontend integration
- **Error Handling**: Comprehensive error handling and logging

## Prerequisites

- Node.js 16+ and npm
- AWS Account with Bedrock and S3 access
- AWS CLI configured (optional but recommended)

## AWS Setup

### 1. Enable AWS Bedrock Models

1. Go to AWS Bedrock console
2. Navigate to "Model access" 
3. Request access for:
   - Anthropic Claude 3 Haiku
   - Anthropic Claude 3 Sonnet (optional, for better responses)

### 2. Create S3 Bucket

```bash
# Create S3 bucket for knowledge base
aws s3 mb s3://your-veron-knowledge-base-bucket

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-veron-knowledge-base-bucket \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
```

### 3. Create IAM User/Role

Create an IAM user with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-veron-knowledge-base-bucket",
        "arn:aws:s3:::your-veron-knowledge-base-bucket/*"
      ]
    }
  ]
}
```

## Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment setup:**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your AWS credentials
   nano .env
   ```

4. **Configure environment variables:**
   ```env
   # Server Configuration
   PORT=5000
   NODE_ENV=development
   FRONTEND_URL=http://localhost:3000

   # AWS Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here

   # AWS Bedrock Configuration
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

   # AWS S3 Configuration
   AWS_S3_BUCKET=your-veron-knowledge-base-bucket
   AWS_S3_PREFIX=veron-knowledge-base/
   ```

## Running the Server

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check server status

### Chat Endpoints
- `POST /api/chat/message` - Send message to AI
- `POST /api/chat/lesson-plan` - Generate lesson plan
- `GET /api/chat/health` - Check chat service health

### Knowledge Base Endpoints
- `POST /api/knowledge/upload` - Upload files
- `GET /api/knowledge/files` - Get uploaded files
- `DELETE /api/knowledge/files/:id` - Delete file
- `GET /api/knowledge/search` - Search knowledge base
- `GET /api/knowledge/health` - Check knowledge service health

## API Usage Examples

### Send Chat Message
```javascript
const response = await fetch('http://localhost:5000/api/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "How can I explain neural networks to beginners?",
    conversationHistory: [],
    context: ""
  })
});

const data = await response.json();
console.log(data.data.message);
```

### Upload Files
```javascript
const formData = new FormData();
formData.append('files', file);
formData.append('category', 'ai-concepts');

const response = await fetch('http://localhost:5000/api/knowledge/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.data.files);
```

## Project Structure

```
backend/
├── server.js              # Main server file
├── routes/
│   ├── chat.js            # Chat API routes
│   └── knowledge.js       # Knowledge base routes
├── services/
│   ├── bedrockService.js  # AWS Bedrock integration
│   └── s3Service.js       # AWS S3 integration
├── middleware/
│   ├── validation.js      # Request validation
│   └── errorHandler.js    # Error handling
├── uploads/               # Temporary file storage
├── package.json
├── env.example            # Environment template
└── README.md
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human readable error message",
  "details": "Development details (dev mode only)"
}
```

## Security Features

- Rate limiting (100 requests per 15 minutes)
- CORS protection
- Helmet security headers
- File type validation
- File size limits (10MB max)
- Input validation with Joi
- AWS credentials encryption

## Monitoring and Logging

- Console logging for development
- Error tracking for AWS service issues
- Request/response logging
- Health check endpoints

## Deployment

### Environment Variables for Production
```env
NODE_ENV=production
PORT=5000
FRONTEND_URL=https://your-frontend-domain.com
```

### Docker Deployment (Optional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 5000
CMD ["npm", "start"]
```

## Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   - Ensure model access is enabled in AWS Bedrock console
   - Check IAM permissions
   - Verify AWS credentials

2. **S3 Upload Failures**
   - Check bucket permissions
   - Verify bucket name in environment variables
   - Ensure AWS credentials have S3 access

3. **File Processing Errors**
   - Check file format (PDF/Word only)
   - Verify file size (10MB max)
   - Ensure sufficient disk space

4. **Connection Timeouts**
   - Increase timeout values for large files
   - Check AWS region configuration
   - Verify network connectivity

### Debugging

Enable debug logging:
```bash
DEBUG=* npm run dev
```

Check AWS service status:
```bash
curl http://localhost:5000/api/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues related to:
- AWS Bedrock: Check AWS Bedrock documentation
- File uploads: Verify S3 permissions and bucket configuration
- API errors: Check server logs and error responses

## License

MIT License - see LICENSE file for details. 