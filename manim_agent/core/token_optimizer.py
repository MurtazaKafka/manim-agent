"""
Token optimization strategies for Manim Agent based on model and duration
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TokenOptimizer:
    """Optimize token usage based on model, duration, and task complexity"""
    
    # Base token limits by model
    MODEL_LIMITS = {
        "opus": {
            "max": 32000,
            "default": 32000,  # Let Opus use its full capacity
            "minimum": 2000
        },
        "sonnet": {
            "max": 64000,  # Sonnet 4 supports up to 64K output tokens
            "default": 32000,  # Generous default for Sonnet 4
            "minimum": 1500
        }
    }
    
    # Duration-based multipliers
    DURATION_MULTIPLIERS = {
        1: 1.0,   # 1 minute: 100% of default (full capacity)
        3: 1.0,   # 3 minutes: 100% of default
        5: 1.0,   # 5 minutes: 100% of default
        10: 1.0,  # 10 minutes: 100% of default
        15: 1.0   # 15+ minutes: 100% of default
    }
    
    # Task-specific limits
    TASK_LIMITS = {
        "content": {
            "base": 1.0,  # 100% of model default
            "per_minute": 1000  # Additional tokens per minute
        },
        "visual": {
            "base": 1.0,  # 100% of model default
            "per_minute": 800
        },
        "code": {
            "base": 1.0,  # 100% of model default - let it generate complete code
            "per_minute": 2000  # More tokens for code generation
        }
    }
    
    @classmethod
    def get_optimal_tokens(cls, 
                         model: str, 
                         duration_minutes: int,
                         task: str = "general",
                         complexity: str = "normal") -> int:
        """
        Calculate optimal token limit based on parameters
        
        Args:
            model: "opus" or "sonnet"
            duration_minutes: Target video duration
            task: "content", "visual", "code", or "general"
            complexity: "simple", "normal", or "complex"
        
        Returns:
            Optimal token limit
        """
        # Get base model limits
        model_config = cls.MODEL_LIMITS.get(model, cls.MODEL_LIMITS["sonnet"])
        base_limit = model_config["default"]
        
        # Apply duration multiplier
        duration_key = min(duration_minutes, 15)
        for minutes, multiplier in sorted(cls.DURATION_MULTIPLIERS.items()):
            if duration_key <= minutes:
                duration_multiplier = multiplier
                break
        else:
            duration_multiplier = cls.DURATION_MULTIPLIERS[15]
        
        # Apply task-specific adjustments
        if task in cls.TASK_LIMITS:
            task_config = cls.TASK_LIMITS[task]
            task_base = base_limit * task_config["base"]
            task_per_minute = task_config["per_minute"] * duration_minutes
            base_limit = int(task_base + task_per_minute)
        
        # Apply duration multiplier
        optimal_tokens = int(base_limit * duration_multiplier)
        
        # Apply complexity adjustments
        if complexity == "simple":
            optimal_tokens = int(optimal_tokens * 0.7)
        elif complexity == "complex":
            optimal_tokens = int(optimal_tokens * 1.3)
        
        # Ensure within model bounds
        optimal_tokens = max(model_config["minimum"], 
                           min(optimal_tokens, model_config["max"]))
        
        logger.info(f"Token optimization: {model} model, {duration_minutes}min, "
                   f"{task} task, {complexity} complexity → {optimal_tokens} tokens")
        
        return optimal_tokens
    
    @classmethod
    def get_requirements_for_duration(cls, duration_minutes: int) -> Dict[str, int]:
        """Get animation requirements based on duration"""
        if duration_minutes <= 1:
            return {
                "scenes": 2,
                "animations": 5,
                "concepts": 1,
                "examples": 1,
                "visuals": 3
            }
        elif duration_minutes <= 3:
            return {
                "scenes": 3,
                "animations": 15,
                "concepts": 2,
                "examples": 2,
                "visuals": 8
            }
        elif duration_minutes <= 5:
            return {
                "scenes": 5,
                "animations": 25,
                "concepts": 3,
                "examples": 3,
                "visuals": 15
            }
        elif duration_minutes <= 10:
            return {
                "scenes": 8,
                "animations": 40,
                "concepts": 5,
                "examples": 5,
                "visuals": 25
            }
        else:  # 15+ minutes
            return {
                "scenes": 12,
                "animations": 60,
                "concepts": 8,
                "examples": 8,
                "visuals": 40
            }
    
    @classmethod
    def optimize_prompt_for_tokens(cls, prompt: str, max_tokens: int) -> str:
        """Optimize prompt to fit within token budget"""
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Truncate intelligently
        sections = prompt.split('\n\n')
        optimized = []
        current_tokens = 0
        
        for section in sections:
            section_tokens = len(section) // 4
            if current_tokens + section_tokens <= max_tokens * 0.9:  # Leave 10% buffer
                optimized.append(section)
                current_tokens += section_tokens
            else:
                # Add truncated version
                remaining = max_tokens - current_tokens - 50  # Buffer
                if remaining > 100:
                    truncated = section[:remaining * 4] + "..."
                    optimized.append(truncated)
                break
        
        return '\n\n'.join(optimized)