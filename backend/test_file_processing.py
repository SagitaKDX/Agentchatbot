#!/usr/bin/env python3
"""
Test script for file processing functionality
Run this to verify the backend enhancements work correctly
"""

import os
import requests
import time

# Configuration
BASE_URL = 'http://localhost:5000/api/agent'

def test_file_upload():
    """Test file upload functionality"""
    print("🔧 Testing file upload...")
    
    # Create a test file
    test_content = """
    This is a test document about AI and machine learning.
    
    Artificial Intelligence (AI) is a branch of computer science that aims to create 
    intelligent machines. Machine learning is a subset of AI that provides systems 
    the ability to automatically learn and improve from experience.
    
    Key concepts:
    - Neural networks
    - Deep learning
    - Natural language processing
    - Computer vision
    
    Applications include:
    1. Chatbots and virtual assistants
    2. Image recognition
    3. Recommendation systems
    4. Autonomous vehicles
    """
    
    with open('test_ai_document.txt', 'w') as f:
        f.write(test_content)
    
    try:
        # Upload the file
        with open('test_ai_document.txt', 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File upload successful!")
            print(f"   File ID: {data['data'].get('file_id', 'N/A')}")
            print(f"   Words extracted: {data['data'].get('word_count', 0)}")
            print(f"   Keywords: {data['data'].get('keywords', [])}")
            return data['data'].get('file_id')
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists('test_ai_document.txt'):
            os.remove('test_ai_document.txt')

def test_file_listing():
    """Test file listing functionality"""
    print("\n🔧 Testing file listing...")
    
    try:
        response = requests.get(f'{BASE_URL}/files')
        
        if response.status_code == 200:
            data = response.json()
            files = data['data']['files']
            print(f"✅ Found {len(files)} processed files")
            
            for file_info in files[:3]:  # Show first 3 files
                print(f"   📄 {file_info['original_filename']} ({file_info['word_count']} words)")
            
            return True
        else:
            print(f"❌ Listing failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return False

def test_agent_chat_with_context():
    """Test agent chat with file context"""
    print("\n🔧 Testing agent chat with file context...")
    
    try:
        # Test message about AI
        message = "What is machine learning and what are its applications?"
        
        response = requests.post(f'{BASE_URL}/chat', json={
            'message': message
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent chat successful!")
            print(f"   Used file context: {data['data'].get('used_file_context', False)}")
            print(f"   Context files available: {data['data'].get('context_files_count', 0)}")
            print(f"   Response preview: {data['data']['message'][:200]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return False

def test_file_stats():
    """Test file statistics endpoint"""
    print("\n🔧 Testing file statistics...")
    
    try:
        response = requests.get(f'{BASE_URL}/files/stats')
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            print("✅ File statistics retrieved!")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Success rate: {stats['processing_success_rate']}%")
            print(f"   Total words: {stats['total_words']}")
            print(f"   File types: {stats['file_types']}")
            return True
        else:
            print(f"❌ Stats failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return False

def test_file_search():
    """Test file search functionality"""
    print("\n🔧 Testing file search...")
    
    try:
        # Search for AI-related terms
        keywords = ["machine", "learning", "AI"]
        
        response = requests.post(f'{BASE_URL}/files/search', json={
            'keywords': keywords
        })
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['files']
            print(f"✅ Search found {len(results)} matching files")
            
            for result in results[:2]:  # Show first 2 results
                print(f"   📄 {result['original_filename']} (relevance: {result['relevance_score']})")
            
            return True
        else:
            print(f"❌ Search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Backend File Processing Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code != 200:
            print("❌ Backend server not running or health check failed")
            print("   Please start the backend server first: python app.py")
            return
    except:
        print("❌ Cannot connect to backend server")
        print("   Please start the backend server first: python app.py")
        return
    
    print("✅ Backend server is running")
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    if test_file_upload():
        tests_passed += 1
    
    time.sleep(1)  # Brief pause between tests
    
    if test_file_listing():
        tests_passed += 1
    
    if test_agent_chat_with_context():
        tests_passed += 1
    
    if test_file_stats():
        tests_passed += 1
    
    if test_file_search():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Backend file processing is working correctly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 