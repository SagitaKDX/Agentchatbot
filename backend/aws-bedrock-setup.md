# AWS Bedrock Setup Guide

## Step 1: Create IAM User for Bedrock Access

1. **Go to IAM Console** → Users → Create User
2. **User name**: `bedrock-api-user` (or your preferred name)
3. **Select**: "Attach policies directly"
4. **Attach these policies**:
   - `AmazonBedrockFullAccess` (for full access)
   - Or create custom policy for minimal permissions (see below)

### Custom Minimal Bedrock Policy (Recommended)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## Step 2: Get Access Keys

1. **Select your user** → Security credentials tab
2. **Create access key** → Choose "Application running outside AWS"
3. **Save the credentials**:
   - Access Key ID
   - Secret Access Key

## Step 3: Available Bedrock Models

### Anthropic Claude Models
- `anthropic.claude-3-haiku-20240307-v1:0` (Fast, cost-effective)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Balanced performance)
- `anthropic.claude-3-opus-20240229-v1:0` (Highest performance)

### Amazon Titan Models
- `amazon.titan-text-express-v1`
- `amazon.titan-text-lite-v1`

### Cohere Models
- `cohere.command-text-v14`
- `cohere.command-light-text-v14`

## Step 4: Regional Availability

Make sure to use a region where Bedrock is available:
- `us-east-1` (N. Virginia) - Recommended
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)

## Step 5: Pricing Information

### Claude 3 Haiku (Most Cost-Effective)
- Input tokens: $0.25 per 1M tokens
- Output tokens: $1.25 per 1M tokens

### Claude 3 Sonnet
- Input tokens: $3.00 per 1M tokens  
- Output tokens: $15.00 per 1M tokens

*Check AWS Bedrock pricing page for latest rates* 