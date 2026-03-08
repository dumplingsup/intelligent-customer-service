#!/usr/bin/env python3
"""Test DeepSeek API configuration for Customer Service."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent_core.agent import CustomerServiceAgent

# Skip vector database import for now
# from vector_database import get_or_create_vectorstore


def test_agent_creation():
    """Test Agent creation."""
    print("=" * 60)
    print("TEST 1: Customer Service Agent Creation")
    print("=" * 60)
    
    try:
        agent = CustomerServiceAgent(
            model="deepseek-chat",
            temperature=0.7
        )
        print(f"✓ Agent Created Successfully")
        print(f"  Model: {agent.model_name}")
        print(f"  Temperature: {agent.temperature}")
        return True
    except Exception as e:
        print(f"✗ Agent Creation Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_query():
    """Test agent query with DeepSeek API."""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Query Test")
    print("=" * 60)
    
    try:
        agent = CustomerServiceAgent(
            model="deepseek-chat",
            temperature=0.7
        )
        
        # Simple test query (no tools, no RAG context)
        response = agent.query(
            question="Hello! Are you working?",
            session_id="test_session_001"
        )
        
        print(f"✓ Agent Query Successful")
        print(f"  Response: {response['answer'][:100]}")
        return True
        
    except Exception as e:
        print(f"✗ Agent Query Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_database():
    """Test vector database initialization."""
    print("\n" + "=" * 60)
    print("TEST 3: Vector Database Test")
    print("=" * 60)
    
    try:
        # Import inside function to avoid path issues
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from vector_database.store import get_or_create_vectorstore
        
        vectorstore = get_or_create_vectorstore()
        print(f"✓ Vector Database Initialized")
        print(f"  Type: {type(vectorstore).__name__}")
        return True
    except Exception as e:
        print(f"✗ Vector Database Test Failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n🧪 DeepSeek API Configuration Tests - Customer Service")
    print("=" * 60)
    
    results = []
    
    # Test 1: Agent Creation
    results.append(test_agent_creation())
    
    # Test 2: Agent Query
    results.append(test_agent_query())
    
    # Test 3: Vector Database
    results.append(test_vector_database())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! DeepSeek API is configured correctly for Customer Service.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
