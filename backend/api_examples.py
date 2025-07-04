#!/usr/bin/env python3
"""
Examples of how to use the AWS Bedrock API through your Flask backend.
These examples show how to interact with your English AI Agent.
"""

import requests
import json

# Backend URL
BASE_URL = "http://localhost:5000/api"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_message():
    """Test sending a chat message to Bedrock AI"""
    print("\n🔍 Testing chat message...")
    
    payload = {
        "message": "Hello! I'm a teacher and I need help explaining artificial intelligence to my students. Can you give me a simple explanation?",
        "conversationHistory": [],
        "context": ""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/message", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ Chat message successful!")
            print(f"AI Response: {result['data']['message'][:200]}...")
            print(f"Usage: {result['data']['usage']}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_lesson_plan_generation():
    """Test generating a lesson plan"""
    print("\n🔍 Testing lesson plan generation...")
    
    payload = {
        "topic": "Introduction to Machine Learning",
        "level": "intermediate",
        "duration": 45
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/lesson-plan", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ Lesson plan generation successful!")
            print(f"Topic: {result['data']['topic']}")
            print(f"Level: {result['data']['level']}")
            print(f"Duration: {result['data']['duration']} minutes")
            print(f"Lesson Plan: {result['data']['lessonPlan'][:300]}...")
        else:
            print(f"❌ Error: {result.get('error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_with_history():
    """Test a conversation with history"""
    print("\n🔍 Testing conversation with history...")
    
    # First message
    conversation_history = []
    
    # Message 1
    payload1 = {
        "message": "What is IoT?",
        "conversationHistory": conversation_history,
        "context": ""
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/chat/message", json=payload1)
        result1 = response1.json()
        
        if result1.get('success'):
            # Add to conversation history
            conversation_history.extend([
                {
                    "id": 1,
                    "text": payload1["message"],
                    "sender": "user",
                    "timestamp": result1['data']['timestamp']
                },
                {
                    "id": 2,
                    "text": result1['data']['message'],
                    "sender": "ai",
                    "timestamp": result1['data']['timestamp']
                }
            ])
            
            # Message 2 with history
            payload2 = {
                "message": "Can you give me some real-world examples that students would understand?",
                "conversationHistory": conversation_history,
                "context": ""
            }
            
            response2 = requests.post(f"{BASE_URL}/chat/message", json=payload2)
            result2 = response2.json()
            
            if result2.get('success'):
                print("✅ Conversation with history successful!")
                print(f"First response: {result1['data']['message'][:100]}...")
                print(f"Follow-up response: {result2['data']['message'][:100]}...")
                return True
            else:
                print(f"❌ Second message error: {result2.get('error')}")
        else:
            print(f"❌ First message error: {result1.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_knowledge_base_upload():
    """Test file upload to knowledge base"""
    print("\n🔍 Testing knowledge base file upload...")
    
    # Create a sample text file
    sample_content = """
    # Introduction to Artificial Intelligence
    
    Artificial Intelligence (AI) is the simulation of human intelligence in machines.
    Key concepts include:
    - Machine Learning
    - Neural Networks
    - Deep Learning
    - Natural Language Processing
    
    Applications in education:
    - Personalized learning
    - Automated grading
    - Intelligent tutoring systems
    """
    
    try:
        # Create temporary file
        with open('sample_ai_content.txt', 'w') as f:
            f.write(sample_content)
        
        # Upload file
        with open('sample_ai_content.txt', 'rb') as f:
            files = {'files': ('sample_ai_content.txt', f, 'text/plain')}
            data = {
                'category': 'ai-education',
                'description': 'Sample AI educational content'
            }
            
            response = requests.post(f"{BASE_URL}/knowledge/upload", files=files, data=data)
            result = response.json()
            
            if result.get('success'):
                print("✅ File upload successful!")
                print(f"Files processed: {len(result['data']['files'])}")
                for file_info in result['data']['files']:
                    if file_info.get('status') == 'processed':
                        print(f"   ✅ {file_info['originalName']}")
                        print(f"      Analysis: {file_info.get('analysis', 'N/A')[:100]}...")
            else:
                print(f"❌ Upload error: {result.get('error')}")
        
        # Clean up
        import os
        os.remove('sample_ai_content.txt')
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API examples"""
    print("🚀 AWS Bedrock API Examples")
    print("=" * 50)
    print("Make sure your Flask backend is running on localhost:5000")
    print()
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Chat Message", test_chat_message),
        ("Lesson Plan Generation", test_lesson_plan_generation),
        ("Conversation with History", test_conversation_with_history),
        ("Knowledge Base Upload", test_knowledge_base_upload)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API endpoints are working correctly!")
    else:
        print("⚠️  Some tests failed. Make sure:")
        print("1. Flask backend is running (python app.py)")
        print("2. AWS credentials are configured")
        print("3. Bedrock model access is enabled")

if __name__ == '__main__':
    main() 