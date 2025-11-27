"""
Memory client for long-term agent memory storage and retrieval.

This module integrates with the OpenMemory API (mem0) to provide persistent 
memory capabilities for agents, allowing them to remember context across 
conversations.

Usage:
    from core.memory.memory_client import MemoryClient
    
    memory_client = MemoryClient()
    
    # Search for relevant memories
    memories = await memory_client.search("user query", user_id="user-123")
    
    # Add new memories from conversation
    await memory_client.add(messages, user_id="user-123")
"""

import os
import logging
from typing import List, Dict, Any, Optional
from core.utils.config import config

logger = logging.getLogger(__name__)

try:
    from mem0 import MemoryClient as Mem0Client
    MEM0_AVAILABLE = True
except ImportError:
    logger.warning("mem0ai library not installed. Memory features will be disabled. Install with: pip install mem0ai")
    MEM0_AVAILABLE = False


class MemoryClient:
    """
    Client for managing long-term agent memories using OpenMemory (mem0).
    
    Provides search and storage capabilities for agent conversations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the memory client.
        
        Args:
            api_key: Optional API key. If not provided, will use MEMO_API_KEY from config.
        """
        self.api_key = api_key or config.MEMO_API_KEY
        self.enabled = MEM0_AVAILABLE and bool(self.api_key)
        
        if not self.enabled:
            if not MEM0_AVAILABLE:
                logger.info("Memory features disabled: mem0ai library not installed")
            elif not self.api_key:
                logger.info("Memory features disabled: MEMO_API_KEY not configured")
            self.client = None
        else:
            try:
                self.client = Mem0Client(api_key=self.api_key)
                logger.info("✅ Memory client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize memory client: {e}")
                self.enabled = False
                self.client = None
    
    async def search(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories based on a query.
        
        Args:
            query: The search query (typically the user's message)
            user_id: Optional user ID to filter memories
            agent_id: Optional agent ID to filter memories
            limit: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries with 'memory' and metadata fields
        """
        if not self.enabled:
            return []
        
        try:
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            if agent_id:
                filters["agent_id"] = agent_id
            
            # Call mem0 search synchronously (it doesn't have async support yet)
            result = self.client.search(query=query, agent_id=agent_id, top_k=limit, filters = {"user_id": user_id})
            
            # Extract results - mem0 returns dict with 'results' key
            memories = result.get("results", []) if isinstance(result, dict) else []
            
            logger.debug(f"Found {len(memories)} relevant memories for query: {query[:50]}...")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def add(
        self,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add new memories from a conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: Optional user ID to associate with the memory
            agent_id: Optional agent ID to associate with the memory
            metadata: Optional additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Build filters/metadata
            add_metadata = metadata or {}
            if agent_id:
                add_metadata["agent_id"] = agent_id
            
            # Call mem0 add - it extracts memories from the conversation
            self.client.add(messages, user_id=user_id, metadata=add_metadata)
            
            logger.debug(f"Added memories from {len(messages)} messages")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memories: {e}")
            return False
    
    async def get_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a user/agent.
        
        Args:
            user_id: Optional user ID to filter memories
            agent_id: Optional agent ID to filter memories
            limit: Maximum number of memories to return
            
        Returns:
            List of all memories
        """
        if not self.enabled:
            return []
        
        try:
            filters = {}
            if agent_id:
                filters["agent_id"] = agent_id
            
            result = self.client.get_all(user_id=user_id, limit=limit)
            memories = result if isinstance(result, list) else []
            
            logger.debug(f"Retrieved {len(memories)} total memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return []
    
    async def delete(
        self,
        memory_id: str
    ) -> bool:
        """
        Delete a specific memory.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.client.delete(memory_id=memory_id)
            logger.debug(f"Deleted memory: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False


# Global singleton instance
_memory_client: Optional[MemoryClient] = None


def get_memory_client() -> MemoryClient:
    """
    Get the global memory client instance.
    
    Returns:
        MemoryClient instance (singleton)
    """
    global _memory_client
    if _memory_client is None:
        _memory_client = MemoryClient()
    return _memory_client
