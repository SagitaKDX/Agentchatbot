#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock connection and API functionality.
Run this script to ensure your AWS credentials and Bedrock access are working.
"""

import os
import sys
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

def test_aws_credentials():
    """Test if AWS credentials are configured correctly"""
    print("🔍 Testing AWS credentials...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not aws_access_key or not aws_secret_key:
            print("❌ AWS credentials not found in .env file")
            print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file")
            return False
            
        print(f"✅ AWS credentials found")
        print(f"   Region: {aws_region}")
        print(f"   Access Key: {aws_access_key[:8]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False

def test_bedrock_connection():
    """Test connection to AWS Bedrock service"""
    print("\n🔍 Testing Bedrock connection...")
    
    try:
        load_dotenv()
        
        # Create Bedrock client
        client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        print("✅ Bedrock client created successfully")
        return client
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        return None
    except PartialCredentialsError:
        print("❌ Incomplete AWS credentials")
        return None
    except Exception as e:
        print(f"❌ Error creating Bedrock client: {e}")
        return None

def test_model_invocation(client):
    """Test invoking a Bedrock model"""
    print("\n🔍 Testing model invocation...")
    
    try:
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        print(f"   Using model: {model_id}")
        
        # Prepare test request
        test_message = "Hello! Can you respond with a simple greeting to test the connection?"
        
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 100,
            'messages': [
                {
                    'role': 'user',
                    'content': test_message
                }
            ],
            'temperature': 0.7
        }
        
        print(f"   Sending test message: {test_message}")
        
        # Invoke the model
        response = client.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        print("✅ Model invocation successful!")
        print(f"   AI Response: {ai_response}")
        print(f"   Token usage: {response_body.get('usage', {})}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock model")
            print("   Make sure you have requested access to this model in the AWS Bedrock console")
            print("   Go to AWS Console → Bedrock → Model access → Request access")
        elif error_code == 'ValidationException':
            print("❌ Model ID validation error")
            print(f"   Model '{model_id}' might not be available in your region")
        else:
            print(f"❌ AWS Error: {error_code} - {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bedrock_service():
    """Test the Bedrock service from our Flask app"""
    print("\n🔍 Testing Flask Bedrock service...")
    
    try:
        # Import our Bedrock service
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from services.bedrock_service import bedrock_service
        
        # Test message generation
        test_message = "Explain what AWS Bedrock is in simple terms."
        response = bedrock_service.generate_response(test_message)
        
        print("✅ Flask Bedrock service working!")
        print(f"   Response: {response['text'][:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import Bedrock service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Bedrock service: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AWS Bedrock Connection Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create .env file from env.example:")
        print("cp env.example .env")
        print("Then edit .env with your AWS credentials")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: AWS Credentials
    if test_aws_credentials():
        tests_passed += 1
    
    # Test 2: Bedrock Connection
    client = test_bedrock_connection()
    if client:
        tests_passed += 1
        
        # Test 3: Model Invocation
        if test_model_invocation(client):
            tests_passed += 1
    
    # Test 4: Flask Service
    if test_bedrock_service():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your Bedrock connection is ready!")
        print("\nYou can now start your Flask backend:")
        print("source venv/bin/activate && python app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
        if tests_passed < 2:
            print("\n🔧 Quick fixes to try:")
            print("1. Verify your AWS credentials in .env file")
            print("2. Check if you have Bedrock access in your AWS account")
            print("3. Ensure your region supports Bedrock")

if __name__ == '__main__':
    main() 