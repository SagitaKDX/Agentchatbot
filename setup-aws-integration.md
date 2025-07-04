# 🚀 Complete Setup Guide: Connect Veron to AWS Bedrock

This guide will help you connect your Veron English AI Agent to AWS Bedrock for real AI-powered responses.

## 📋 Quick Setup Checklist

- [ ] AWS Account with Bedrock access
- [ ] AWS credentials configured
- [ ] S3 bucket created
- [ ] Backend server running
- [ ] Frontend connected to backend

## 🛠️ Step 1: AWS Setup

### 1.1 Enable AWS Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **"Model access"** in the left sidebar
3. Click **"Request model access"**
4. Enable the following models:
   - ✅ **Anthropic Claude 3 Haiku** (Required)
   - ✅ **Anthropic Claude 3 Sonnet** (Optional, for better responses)

### 1.2 Create S3 Bucket

```bash
# Replace 'your-unique-bucket-name' with your actual bucket name
aws s3 mb s3://your-veron-knowledge-base-bucket-12345

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-veron-knowledge-base-bucket-12345 \
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

### 1.3 Create IAM User

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user: **"veron-ai-user"**
3. Attach the following policy:

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
      "Resource": "*"
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
        "arn:aws:s3:::your-veron-knowledge-base-bucket-12345",
        "arn:aws:s3:::your-veron-knowledge-base-bucket-12345/*"
      ]
    }
  ]
}
```

4. Create **Access Keys** and save them securely

## 🔧 Step 2: Backend Configuration

### 2.1 Create Environment File

```bash
cd backend
cp env.example .env
```

### 2.2 Configure .env File

Edit `backend/.env` with your AWS credentials:

```env
# Server Configuration
PORT=5000
NODE_ENV=development
FRONTEND_URL=http://localhost:3000

# AWS Configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key

# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# AWS S3 Configuration
AWS_S3_BUCKET=your-veron-knowledge-base-bucket-12345
AWS_S3_PREFIX=veron-knowledge-base/

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# File Upload Configuration
MAX_FILE_SIZE=10485760
MAX_FILES_PER_UPLOAD=5
```

### 2.3 Install Dependencies & Start Backend

```bash
# From the backend directory
npm install
npm run dev
```

The backend should start on `http://localhost:5000`

## 🌐 Step 3: Frontend Configuration

### 3.1 Update Frontend Environment (Optional)

Create `src/.env.local` if you want to use a different backend URL:

```env
REACT_APP_API_URL=http://localhost:5000
```

### 3.2 Start Frontend

```bash
# From the main project directory
npm start
```

The frontend should start on `http://localhost:3000`

## 🧪 Step 4: Test the Integration

### 4.1 Test Backend Health

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "OK",
  "message": "Veron AI Backend is running",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 4.2 Test Chat API

```bash
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me with teaching English?",
    "conversationHistory": [],
    "context": ""
  }'
```

### 4.3 Test File Upload

```bash
curl -X POST http://localhost:5000/api/knowledge/upload \
  -F "files=@/path/to/your/document.pdf" \
  -F "category=test"
```

## 🎯 Step 5: Use Veron

1. **Open your browser** and go to `http://localhost:3000`
2. **Start a new chat** by clicking the "New chat" button
3. **Ask Veron a question** about teaching English, AI, IoT, or chip technology
4. **Upload documents** in the Knowledge Base section to enhance Veron's knowledge

### Example Questions to Try:

- "How can I explain neural networks to English language learners?"
- "Create a lesson plan for teaching IoT vocabulary to intermediate students"
- "What are the key technical terms students should know about semiconductors?"
- "Help me simplify the concept of machine learning for beginners"

## 🔄 Complete Startup Sequence

### Terminal 1 (Backend):
```bash
cd backend
npm run dev
```

### Terminal 2 (Frontend):
```bash
cd ..
npm start
```

## 🚨 Troubleshooting

### Backend Issues

1. **"Bedrock Access Denied"**
   ```bash
   # Check if model access is enabled
   aws bedrock list-foundation-models --region us-east-1
   ```

2. **"S3 Access Denied"**
   ```bash
   # Test S3 access
   aws s3 ls s3://your-veron-knowledge-base-bucket-12345
   ```

3. **"Invalid AWS credentials"**
   ```bash
   # Verify credentials
   aws sts get-caller-identity
   ```

### Frontend Issues

1. **"Failed to send message"**
   - Check if backend is running on port 5000
   - Verify `.env` configuration
   - Check browser console for detailed errors

2. **"CORS errors"**
   - Ensure `FRONTEND_URL=http://localhost:3000` in backend `.env`

### Common Solutions

```bash
# Restart both servers
pkill -f "npm start"
pkill -f "npm run dev"

# Clear browser cache and localStorage
# In browser console:
localStorage.clear()
location.reload()
```

## 📊 Production Deployment

### Backend Deployment
- Use environment variables for AWS credentials
- Set `NODE_ENV=production`
- Use a process manager like PM2
- Enable logging and monitoring

### Frontend Deployment
- Build with `npm run build`
- Update `REACT_APP_API_URL` to your production backend URL
- Deploy to Netlify, Vercel, or AWS S3/CloudFront

## 🔐 Security Notes

- **Never commit `.env` files** to version control
- **Use IAM roles** instead of access keys in production
- **Enable CloudTrail** for audit logging
- **Use HTTPS** in production
- **Implement authentication** for production use

## 💡 Next Steps

1. **Enhance Knowledge Base**: Upload your teaching materials
2. **Customize Prompts**: Modify system prompts in `bedrockService.js`
3. **Add Vector Search**: Implement semantic search with embeddings
4. **Monitor Usage**: Set up CloudWatch for AWS service monitoring
5. **Scale**: Use Lambda functions for serverless deployment

## 📞 Support

If you encounter issues:

1. Check the backend logs for detailed error messages
2. Verify AWS service status
3. Test individual API endpoints
4. Review AWS CloudTrail logs for permission issues

## 🎉 Success!

Once everything is working, you'll have:
- ✅ Real AI responses powered by AWS Bedrock
- ✅ Knowledge base with document upload/analysis
- ✅ Persistent chat history
- ✅ Professional ChatGPT-like interface
- ✅ Secure file handling with AWS S3

Your Veron English AI Agent is now ready to help teachers with technical English instruction! 🚀 