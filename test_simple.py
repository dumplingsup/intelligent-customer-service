#!/usr/bin/env python3
"""Simple test for DeepSeek API configuration."""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("DeepSeek API Configuration Test")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   DEEPSEEK_API_KEY: {'✓ Set' if os.getenv('DEEPSEEK_API_KEY') else '✗ Not Set'}")
print(f"   DEEPSEEK_BASE_URL: {os.getenv('DEEPSEEK_BASE_URL', 'Not Set')}")
print(f"   DEEPSEEK_MODEL: {os.getenv('DEEPSEEK_MODEL', 'Not Set')}")

# Test LLM creation
print("\n2. Testing LLM Creation:")
try:
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0.7,
        max_tokens=100,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )
    print(f"   ✓ LLM Created: {llm.model}")
    print(f"   Base URL: {llm.openai_api_base}")
except Exception as e:
    print(f"   ✗ LLM Creation Failed: {str(e)}")
    sys.exit(1)

# Test API call
print("\n3. Testing API Call:")
try:
    response = llm.invoke("Hello! Reply in 10 words.")
    print(f"   ✓ API Call Successful")
    print(f"   Response: {response.content}")
except Exception as e:
    print(f"   ✗ API Call Failed: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! DeepSeek API is working correctly.")
print("=" * 60)
