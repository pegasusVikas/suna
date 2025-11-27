# Memory Module

## Overview

The memory module provides long-term memory capabilities for Suna agents using the [mem0ai](https://mem0.ai/) API. This enables agents to remember context from previous conversations and provide more personalized responses.

## Features

- **Semantic Memory Search**: Retrieve relevant memories based on user queries
- **Automatic Memory Storage**: Conversations are automatically stored after each agent run
- **User & Agent Scoping**: Memories can be filtered by user_id and agent_id
- **Graceful Degradation**: Memory features are optional and won't break the agent if disabled

## Setup

### 1. Install mem0ai Library

The library is already included in the project dependencies. If you need to install it manually:

```bash
pip install mem0ai
# or if using uv
uv pip install mem0ai
```

### 2. Configure API Key

Add your mem0 API key to your `.env` file:

```bash
MEMO_API_KEY=your_api_key_here
```

Get your API key from: https://app.mem0.ai/

### 3. Enable Memory (Automatic)

Memory is automatically enabled when:
- The `mem0ai` library is installed (already in dependencies)
- `MEMO_API_KEY` is configured in the environment

If either condition is not met, the agent will continue to work normally without memory features.

## How It Works

### Memory Search (Retrieval)

When a user sends a message:

1. The latest user message is extracted
2. The memory client searches for relevant memories using semantic similarity
3. Top 5 relevant memories are retrieved
4. Memories are injected into the system prompt for context

```python
# Example: Memory search in build_system_prompt
relevant_memories = await memory_client.search(
    query=latest_user_message,
    user_id=user_id,
    agent_id=agent_id,
    limit=5
)
```

### Memory Storage

After the agent completes its run:

1. Recent messages (last 10) from the conversation are fetched
2. User and assistant messages are extracted and formatted
3. The conversation is stored in the memory system
4. mem0 automatically extracts and stores relevant facts

```python
# Example: Storing conversation
await memory_client.add(
    messages=messages_for_memory,
    user_id=user_id,
    agent_id=agent_id
)
```

## System Prompt Integration

Memories are injected into the system prompt with clear formatting:

```
=== USER MEMORY ===
The following are relevant memories from previous conversations with this user. 
Use these to provide personalized and context-aware responses.

- User prefers detailed technical explanations
- User is working on a Python project
- User's timezone is PST

=== END USER MEMORY ===

IMPORTANT: Use the memories above to personalize your responses and maintain 
context across conversations.
```

## API Reference

### MemoryClient

#### `__init__(api_key: Optional[str] = None)`
Initialize the memory client.

- **api_key**: Optional API key. Uses `MEMO_API_KEY` from config if not provided.

#### `async search(query: str, user_id: Optional[str] = None, agent_id: Optional[str] = None, limit: int = 5)`
Search for relevant memories.

- **query**: The search query (typically the user's message)
- **user_id**: Optional user ID to filter memories
- **agent_id**: Optional agent ID to filter memories  
- **limit**: Maximum number of memories to return (default: 5)
- **Returns**: List of memory dictionaries

#### `async add(messages: List[Dict], user_id: Optional[str] = None, agent_id: Optional[str] = None, metadata: Optional[Dict] = None)`
Add new memories from conversations.

- **messages**: List of message dicts with 'role' and 'content'
- **user_id**: Optional user ID to associate with the memory
- **agent_id**: Optional agent ID to associate with the memory
- **metadata**: Optional additional metadata
- **Returns**: True if successful, False otherwise

#### `async get_all(user_id: Optional[str] = None, agent_id: Optional[str] = None, limit: int = 100)`
Get all memories for a user/agent.

#### `async delete(memory_id: str)`
Delete a specific memory.

### Helper Function

#### `get_memory_client() -> MemoryClient`
Get the global memory client singleton instance.

```python
from core.memory import get_memory_client

memory_client = get_memory_client()
```

## Example Usage

```python
from core.memory import get_memory_client

# Get the memory client
memory_client = get_memory_client()

# Search for relevant memories
memories = await memory_client.search(
    query="What did I work on last week?",
    user_id="user-123"
)

# Add conversation to memory
conversation = [
    {"role": "user", "content": "I'm working on a Python project"},
    {"role": "assistant", "content": "Great! What kind of Python project?"},
    {"role": "user", "content": "A web scraper for e-commerce sites"}
]

await memory_client.add(
    messages=conversation,
    user_id="user-123"
)
```

## Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Memory Search          │
│  (Semantic Similarity)  │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  System Prompt Builder  │
│  + Memory Context       │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│    Agent Execution      │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Memory Storage        │
│   (Auto-extract facts)  │
└─────────────────────────┘
```

## Troubleshooting

### Memory not working

1. **Check if mem0ai is installed**:
   ```bash
   python -c "import mem0; print('mem0ai installed')"
   ```

2. **Check API key**:
   ```bash
   # In Python
   from core.utils.config import config
   print(config.MEMO_API_KEY)
   ```

3. **Check logs**:
   Look for messages like:
   - `✅ Memory client initialized successfully`
   - `Memory features disabled: mem0ai library not installed`
   - `Memory features disabled: MEMO_API_KEY not configured`

### Memory not appearing in responses

- Memories are only searched if a user message is present
- Check debug logs for: `Found X relevant memories for user Y`
- Verify memories exist by checking the mem0 dashboard

## Performance Considerations

- Memory search is asynchronous and won't block the agent
- Search is limited to 5 most relevant memories by default
- Only the last 10 messages are stored after each run
- If memory operations fail, the agent continues normally

## Privacy & Data Management

- Memories are scoped by `user_id` and optionally `agent_id`
- Users can only see their own memories
- Memories can be deleted using the `delete()` method
- Consider implementing user consent and data retention policies

## Future Enhancements

- [ ] Memory management UI for users
- [ ] Configurable memory limits per user
- [ ] Memory export/import functionality
- [ ] Memory statistics and analytics
- [ ] Selective memory deletion (by topic/time range)
- [ ] Memory compression for long-term storage
