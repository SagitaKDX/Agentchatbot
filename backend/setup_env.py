#!/usr/bin/env python3
"""
Interactive script to help set up your .env file for AWS Bedrock.
"""

import os
import shutil

def setup_env_file():
    """Interactive setup for .env file"""
    print("🔧 AWS Bedrock Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Copy from example if it doesn't exist
    if not os.path.exists('env.example'):
        print("❌ env.example file not found!")
        return
    
    print("\nPlease provide your AWS credentials:")
    print("(You can find these in your AWS IAM console)")
    print()
    
    # Get AWS credentials
    aws_access_key = input("AWS Access Key ID: ").strip()
    if not aws_access_key:
        print("❌ AWS Access Key ID is required!")
        return
    
    aws_secret_key = input("AWS Secret Access Key: ").strip()
    if not aws_secret_key:
        print("❌ AWS Secret Access Key is required!")
        return
    
    # Get AWS region
    print("\nAvailable AWS regions for Bedrock:")
    print("1. us-east-1 (N. Virginia) - Recommended")
    print("2. us-west-2 (Oregon)")
    print("3. eu-west-1 (Ireland)")
    print("4. ap-southeast-1 (Singapore)")
    
    region_choice = input("\nSelect region (1-4) or enter custom region: ").strip()
    
    region_map = {
        '1': 'us-east-1',
        '2': 'us-west-2', 
        '3': 'eu-west-1',
        '4': 'ap-southeast-1'
    }
    
    aws_region = region_map.get(region_choice, region_choice)
    if region_choice in ['1', '2', '3', '4']:
        print(f"Selected region: {aws_region}")
    else:
        print(f"Using custom region: {aws_region}")
    
    # Get Bedrock model
    print("\nAvailable Bedrock models:")
    print("1. anthropic.claude-3-haiku-20240307-v1:0 (Fast, cost-effective)")
    print("2. anthropic.claude-3-sonnet-20240229-v1:0 (Balanced performance)")
    print("3. anthropic.claude-3-opus-20240229-v1:0 (Highest performance)")
    
    model_choice = input("\nSelect model (1-3): ").strip()
    
    model_map = {
        '1': 'anthropic.claude-3-haiku-20240307-v1:0',
        '2': 'anthropic.claude-3-sonnet-20240229-v1:0',
        '3': 'anthropic.claude-3-opus-20240229-v1:0'
    }
    
    bedrock_model = model_map.get(model_choice, model_map['1'])
    print(f"Selected model: {bedrock_model}")
    
    # Read env.example template
    with open('env.example', 'r') as f:
        env_content = f.read()
    
    # Replace placeholders
    env_content = env_content.replace('your_access_key_here', aws_access_key)
    env_content = env_content.replace('your_secret_key_here', aws_secret_key)
    env_content = env_content.replace('us-east-1', aws_region)
    env_content = env_content.replace('anthropic.claude-3-haiku-20240307-v1:0', bedrock_model)
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("\nNext steps:")
    print("1. Make sure you have requested access to Bedrock models in AWS Console")
    print("2. Test your connection: python test_bedrock_connection.py")
    print("3. Start your Flask backend: source venv/bin/activate && python app.py")
    
def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if in backend directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the backend directory")
        return False
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found. Please run:")
        print("   python3 -m venv venv")
        return False
    
    # Check if dependencies are installed
    try:
        import boto3
        import flask
        print("✅ Dependencies are installed")
    except ImportError:
        print("❌ Dependencies not installed. Please run:")
        print("   source venv/bin/activate && pip install -r requirements.txt")
        return False
    
    print("✅ All prerequisites met")
    return True

def main():
    """Main setup function"""
    if not check_prerequisites():
        return
    
    setup_env_file()

if __name__ == '__main__':
    main() 