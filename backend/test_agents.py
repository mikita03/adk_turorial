#!/usr/bin/env python3
"""
Test script to verify agent functionality without requiring OAuth authentication.
This tests the core AI agent logic independently.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.supervisor import SupervisorAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.responder import ResponderAgent
from app.schemas.email import EmailContent

mock_email = EmailContent(
    id="test_email_001",
    from_email="test@example.com",
    to_email=["user@example.com"],
    cc_email=[],
    subject="テスト件名：会議の件について",
    body="お疲れ様です。\n\n来週の会議についてご相談があります。\n日程調整をお願いできますでしょうか。\n\nよろしくお願いいたします。",
    html_body=None,
    date="2025-01-03T10:00:00Z",
    attachments=[]
)

async def test_analyzer_agent():
    """Test the analyzer agent functionality"""
    print("🔍 Testing Analyzer Agent...")
    
    try:
        analyzer = AnalyzerAgent()
        result = await analyzer.analyze_email(mock_email)
        
        print(f"✅ Analysis successful!")
        print(f"   Summary: {result.get('summary', 'N/A')}")
        print(f"   Priority: {result.get('priority', 'N/A')}")
        print(f"   Category: {result.get('category', 'N/A')}")
        print(f"   Entities: {result.get('important_entities', [])}")
        return True
        
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

async def test_responder_agent():
    """Test the responder agent functionality"""
    print("\n📝 Testing Responder Agent...")
    
    try:
        responder = ResponderAgent()
        result = await responder.generate_reply(mock_email)
        
        print(f"✅ Reply generation successful!")
        print(f"   Subject: {result.get('subject', 'N/A')}")
        print(f"   Body preview: {result.get('body', 'N/A')[:100]}...")
        print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Responder test failed: {e}")
        return False

async def test_supervisor_agent():
    """Test the supervisor agent coordination"""
    print("\n🎯 Testing Supervisor Agent...")
    
    try:
        supervisor = SupervisorAgent()
        result = await supervisor.process_email(mock_email)
        
        print(f"✅ Supervisor coordination successful!")
        print(f"   Tasks completed: {len(result.get('completed_tasks', []))}")
        print(f"   Overall success: {result.get('success', False)}")
        return True
        
    except Exception as e:
        print(f"❌ Supervisor test failed: {e}")
        return False

async def main():
    """Run all agent tests"""
    print("🤖 Gmail Secretary Agent - Core Functionality Test")
    print("=" * 50)
    
    analyzer_ok = await test_analyzer_agent()
    responder_ok = await test_responder_agent()
    supervisor_ok = await test_supervisor_agent()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Analyzer Agent: {'✅ PASS' if analyzer_ok else '❌ FAIL'}")
    print(f"   Responder Agent: {'✅ PASS' if responder_ok else '❌ FAIL'}")
    print(f"   Supervisor Agent: {'✅ PASS' if supervisor_ok else '❌ FAIL'}")
    
    all_passed = analyzer_ok and responder_ok and supervisor_ok
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n💡 Note: Some tests failed. This is expected if:")
        print("   - OpenAI API key is not configured")
        print("   - Network connectivity issues")
        print("   - Missing dependencies")
        
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
