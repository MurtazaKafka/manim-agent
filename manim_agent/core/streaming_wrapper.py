"""
Wrapper for LLM service to add streaming capabilities
"""
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class StreamingLLMWrapper:
    """Wraps LLM service to provide streaming updates"""
    
    def __init__(self, llm_service, stream_callback: Optional[Callable] = None):
        self.llm = llm_service
        self.stream_callback = stream_callback
        self.buffer = ""
        self.chunk_size = 100  # Send updates every 100 characters
        
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate with streaming updates"""
        
        # Create internal callback that buffers and sends chunks
        async def internal_callback(chunk: str):
            self.buffer += chunk
            
            # Send update when buffer reaches chunk size
            if len(self.buffer) >= self.chunk_size and self.stream_callback:
                await self.stream_callback(self.buffer)
                self.buffer = ""
        
        # Call LLM with streaming
        result = await self.llm.generate(
            prompt,
            system_prompt,
            stream_callback=internal_callback if self.stream_callback else None,
            **kwargs
        )
        
        # Send any remaining buffer
        if self.buffer and self.stream_callback:
            await self.stream_callback(self.buffer)
            self.buffer = ""
            
        return result
    
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        """Generate JSON (no streaming for structured output)"""
        return await self.llm.generate_json(prompt, system_prompt, **kwargs)
    
    # Proxy other methods
    def __getattr__(self, name):
        """Proxy other methods to the wrapped LLM service"""
        return getattr(self.llm, name)