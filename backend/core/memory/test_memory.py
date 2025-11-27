"""
Test script for memory functionality.

This script demonstrates and tests the memory client integration.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.memory.memory_client import get_memory_client
from core.utils.logger import logger


async def test_memory_client():
    """Test the memory client functionality."""
    
    print("=" * 60)
    print("Testing Memory Client")
    print("=" * 60)
    
    # Get the memory client
    memory_client = get_memory_client()
    
    # Check if memory is enabled
    if not memory_client.enabled:
        print("\n❌ Memory client is NOT enabled")
        print("Reasons:")
        print(f"  - mem0 library installed: {memory_client.enabled}")
        print(f"  - API key configured: {'Yes' if memory_client.api_key else 'No'}")
        print("\nTo enable memory:")
        print("  1. Install mem0: pip install mem0")
        print("  2. Set MEMO_API_KEY in your .env file")
        return
    
    print("\n✅ Memory client is enabled")
    
    # Test user/agent IDs
    test_user_id = "test-user-12345"
    test_agent_id = "test-agent-67890"
    
    # Test 1: Add a sample conversation
    print("\n" + "-" * 60)
    print("Test 1: Adding a sample conversation to memory")
    print("-" * 60)
    
    sample_conversation = [
        {"role": "user", "content": "Hi, my name is Alice and I love Python programming"},
        {"role": "assistant", "content": "Hello Alice! It's great to meet a fellow Python enthusiast. What kind of Python projects do you enjoy working on?"},
        {"role": "user", "content": "I mainly work on web scraping and data analysis projects"},
        {"role": "assistant", "content": "Excellent! Web scraping and data analysis are powerful applications of Python. Libraries like BeautifulSoup, Scrapy, and Pandas are very useful for those tasks."}
    ]
    
    success = await memory_client.add(
        messages=sample_conversation,
        user_id=test_user_id,
        agent_id=test_agent_id,
        metadata={"test": True, "timestamp": "2024-01-01"}
    )
    
    if success:
        print("✅ Successfully added conversation to memory")
    else:
        print("❌ Failed to add conversation to memory")
        return
    
    # Wait a moment for the memory to be indexed
    print("\nWaiting 3 seconds for indexing...")
    await asyncio.sleep(3)
    
    # Test 2: Search for memories
    print("\n" + "-" * 60)
    print("Test 2: Searching for relevant memories")
    print("-" * 60)
    
    search_queries = [
        "What's my name?",
        "What programming language do I like?",
        "What projects do I work on?",
        "Tell me about data science"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Query: '{query}'")
        memories = await memory_client.search(
            query=query,
            user_id=test_user_id,
            agent_id=test_agent_id,
            limit=3
        )
        
        if memories:
            print(f"   Found {len(memories)} relevant memories:")
            for i, memory in enumerate(memories, 1):
                memory_text = memory.get('memory', memory)
                print(f"   {i}. {memory_text}")
        else:
            print("   No memories found")
    
    # Test 3: Get all memories
    print("\n" + "-" * 60)
    print("Test 3: Retrieving all memories for user")
    print("-" * 60)
    
    all_memories = await memory_client.get_all(
        user_id=test_user_id,
        agent_id=test_agent_id,
        limit=10
    )
    
    print(f"\n📝 Total memories for user: {len(all_memories)}")
    if all_memories:
        print("\nAll memories:")
        for i, memory in enumerate(all_memories, 1):
            memory_text = memory.get('memory', str(memory))
            print(f"  {i}. {memory_text}")
    
    # Test 4: Test with different user (should return empty)
    print("\n" + "-" * 60)
    print("Test 4: Searching with different user (should be empty)")
    print("-" * 60)
    
    other_user_memories = await memory_client.search(
        query="What's my name?",
        user_id="different-user-99999",
        limit=5
    )
    
    print(f"\n🔍 Memories for different user: {len(other_user_memories)}")
    if other_user_memories:
        print("   (Unexpected - should be empty for different user)")
    else:
        print("   ✅ Correctly returned no memories for different user")
    
    print("\n" + "=" * 60)
    print("Memory Client Testing Complete!")
    print("=" * 60)


def main():
    """Main entry point."""
    try:
        asyncio.run(test_memory_client())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
