import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import asyncio
import logging
from .token_optimizer import TokenOptimizer

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMService(ABC):
    """Abstract base class for LLM integration"""
    
    def __init__(self):
        self.duration_minutes = 3  # Default duration
        self.task_type = "general"  # Default task type
    
    def set_context(self, duration_minutes: int, task_type: str = "general"):
        """Set context for token optimization"""
        self.duration_minutes = duration_minutes
        self.task_type = task_type
    
    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """Generate response from LLM with optional streaming"""
        pass
    
    @abstractmethod
    async def generate_json(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          schema: Optional[Dict[str, Any]] = None,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Generate JSON response from LLM"""
        pass
    
    async def generate_with_retry(self, 
                                prompt: str,
                                system_prompt: Optional[str] = None,
                                max_retries: int = 3,
                                stream_callback: Optional[Callable[[str], None]] = None,
                                **kwargs) -> str:
        """Generate with retry logic for production reliability"""
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, system_prompt, stream_callback=stream_callback, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def generate_json_with_retry(self,
                                     prompt: str,
                                     system_prompt: Optional[str] = None,
                                     max_retries: int = 3,
                                     **kwargs) -> Dict[str, Any]:
        """Generate JSON with retry logic"""
        for attempt in range(max_retries):
            try:
                return await self.generate_json(prompt, system_prompt, **kwargs)
            except Exception as e:
                logger.warning(f"LLM JSON generation attempt {attempt + 1} failed: {e}")
                
                # On last attempt, try raw text generation with JSON extraction
                if attempt == max_retries - 1:
                    logger.info("Falling back to raw text generation for JSON")
                    try:
                        # Use regular generate method
                        json_system = system_prompt or "You are a helpful AI assistant."
                        json_system += "\n\nRespond with valid JSON."
                        
                        # Remove 'schema' from kwargs as generate() doesn't accept it
                        kwargs_copy = kwargs.copy()
                        kwargs_copy.pop('schema', None)
                        
                        response = await self.generate(prompt, json_system, **kwargs_copy)
                        
                        # Try to extract JSON from response
                        import re
                        json_match = re.search(r'(\{[\s\S]*\})', response)
                        if json_match:
                            return json.loads(json_match.group(1))
                        else:
                            # Try parsing the whole response
                            return json.loads(response)
                    except Exception as e2:
                        logger.error(f"Fallback JSON extraction also failed: {e2}")
                        raise e
                
                await asyncio.sleep(2 ** attempt)


class OpenAIService(LLMService):
    """OpenAI API integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        super().__init__()
        try:
            import openai
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
            
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        self.model = model
    
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """Generate response using OpenAI API"""
        # Use token optimizer if max_tokens not specified
        if not max_tokens:
            max_tokens = TokenOptimizer.get_optimal_tokens(
                "gpt4",  # Map to similar model
                self.duration_minutes,
                self.task_type
            )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def generate_json(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          schema: Optional[Dict[str, Any]] = None,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Generate JSON response using OpenAI API with JSON mode"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        if schema:
            json_prompt += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"
        
        messages.append({"role": "user", "content": json_prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)


class AnthropicService(LLMService):
    """Anthropic Claude API integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022", use_opus: bool = False):
        super().__init__()
        try:
            import anthropic
        except ImportError:
            raise ImportError("Please install anthropic: pip install anthropic")
            
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        # Use explicit use_opus parameter if provided, otherwise check environment
        if use_opus:
            self.model = "claude-opus-4-20250514"  # Claude Opus 4 - latest 2025 version
            self.use_opus = True
            self.model_type = "opus"
            logger.info("Using Claude Opus 4 for highest quality content generation")
        else:
            # Use latest Sonnet 4 model (2025 version)
            self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4 - released May 2025
            self.use_opus = False
            self.model_type = "sonnet"
            logger.info(f"Using Claude Sonnet 4 ({self.model}) for efficient content generation")
    
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """Generate response using Anthropic API"""
        # Use token optimizer for smart limits
        if not max_tokens:
            max_tokens = TokenOptimizer.get_optimal_tokens(
                self.model_type,
                self.duration_minutes,
                self.task_type
            )
            logger.info(f"Token optimization: {self.model_type} model, {self.duration_minutes}min, {self.task_type} task → {max_tokens} tokens")
        
        # Log the actual max_tokens being used
        logger.debug(f"Anthropic API call: model={self.model}, max_tokens={max_tokens}")
        
        # Use streaming for high token requests or when callback provided
        if max_tokens > 4000 or stream_callback:
            # Stream the response for long operations
            stream = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Collect the streamed response
            response_text = ""
            async for event in stream:
                if event.type == "content_block_delta":
                    chunk = event.delta.text
                    response_text += chunk
                    # Call the streaming callback if provided
                    if stream_callback:
                        # Check if callback is async
                        if asyncio.iscoroutinefunction(stream_callback):
                            await stream_callback(chunk)
                        else:
                            stream_callback(chunk)
                elif event.type == "message_stop":
                    break
            
            return response_text
        else:
            # Non-streaming for other models
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
    
    async def generate_json(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          schema: Optional[Dict[str, Any]] = None,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Generate JSON response using Anthropic API"""
        json_system = system_prompt or "You are a helpful AI assistant."
        
        # Special handling for Claude Sonnet 4 which has different behavior
        if "sonnet-4" in self.model:
            json_system += "\n\nYou must output valid JSON and nothing else. Do not use markdown code blocks. Do not add any explanatory text before or after the JSON. Ensure all strings are properly quoted and escaped."
            json_prompt = f"Generate a JSON response for the following request. Output only the JSON object, nothing else.\n\n{prompt}"
        else:
            json_system += "\n\nIMPORTANT: You MUST respond with valid JSON only. No markdown formatting, no code blocks, no explanations before or after. Just pure, valid JSON that can be parsed by json.loads()."
            json_prompt = prompt
        
        if schema:
            json_prompt += f"\n\nThe JSON must follow this exact schema:\n{json.dumps(schema, indent=2)}"
        
        # For Sonnet 4, be even more explicit
        if "sonnet-4" in self.model:
            json_prompt += "\n\nStart your response with { and end with }. No other text."
        
        # Use optimized token limits
        if not max_tokens:
            max_tokens = TokenOptimizer.get_optimal_tokens(
                self.model_type,
                self.duration_minutes,
                self.task_type
            )
        
        response = await self.generate(
            json_prompt,
            json_system,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Log raw response for debugging Sonnet 4 issues
        if "sonnet-4" in self.model:
            logger.debug(f"Raw JSON response from Sonnet 4: {response[:200]}...")
        
        # Clean response (remove markdown if any)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        # Additional cleaning for common issues
        response = response.strip()
        
        # Try to parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Log the error and a snippet of the problematic JSON
            logger.error(f"JSON decode error: {e}")
            logger.error(f"JSON snippet around error: {response[max(0, e.pos-50):e.pos+50]}")
            
            # Try to fix common JSON issues
            import re
            
            # Remove any trailing commas before closing braces/brackets
            response = re.sub(r',\s*}', '}', response)
            response = re.sub(r',\s*]', ']', response)
            
            # Fix strings that might contain unescaped newlines or quotes
            # This is a more sophisticated approach to handle malformed JSON strings
            
            # First, try to identify string boundaries and escape newlines within them
            # Look for patterns like "key": "value with
            # newline" and fix them
            def fix_json_strings(json_str):
                # State machine to track if we're inside a string
                fixed = []
                in_string = False
                escape_next = False
                i = 0
                
                while i < len(json_str):
                    char = json_str[i]
                    
                    if escape_next:
                        fixed.append(char)
                        escape_next = False
                        i += 1
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        fixed.append(char)
                        i += 1
                        continue
                    
                    if char == '"':
                        # Check if this quote is part of a JSON structure
                        # Look back to see if it's after a : or , or { or [
                        if in_string:
                            # We're ending a string
                            in_string = False
                            fixed.append(char)
                        else:
                            # We're starting a string
                            in_string = True
                            fixed.append(char)
                        i += 1
                        continue
                    
                    if in_string:
                        # We're inside a string, escape special characters
                        if char == '\n':
                            fixed.append('\\n')
                        elif char == '\r':
                            fixed.append('\\r')
                        elif char == '\t':
                            fixed.append('\\t')
                        else:
                            fixed.append(char)
                    else:
                        fixed.append(char)
                    
                    i += 1
                
                # If we ended while still in a string, close it
                if in_string:
                    fixed.append('"')
                
                return ''.join(fixed)
            
            try:
                response = fix_json_strings(response)
            except:
                # If our fix fails, continue with original response
                pass
            
            # Try parsing again
            try:
                return json.loads(response)
            except json.JSONDecodeError as e2:
                logger.error(f"Still failed after fixes: {e2}")
                
                # Try one more aggressive fix for common Sonnet 4 issues
                if "Expecting property name" in str(e2):
                    # Fix missing quotes around property names
                    # Replace patterns like { property: "value" } with { "property": "value" }
                    response = re.sub(r'{\s*([a-zA-Z_]\w*)\s*:', r'{ "\1":', response)
                    response = re.sub(r',\s*([a-zA-Z_]\w*)\s*:', r', "\1":', response)
                    try:
                        return json.loads(response)
                    except:
                        pass
                
                # As a last resort, try to extract JSON from the response
                # Look for JSON-like structure
                json_match = re.search(r'(\{[\s\S]*\})', response)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except:
                        pass
                raise e2


def create_llm_service(provider: LLMProvider = LLMProvider.OPENAI, use_opus: bool = True, **kwargs) -> LLMService:
    """Factory function to create LLM service"""
    if provider == LLMProvider.OPENAI:
        return OpenAIService(**kwargs)
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicService(use_opus=use_opus, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")