from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import LLMService
from .prompt_templates import DynamicPromptGenerator
from ..config.meta_prompt_framework import (
    CHAIN_OF_THOUGHT_PROMPT, 
    PERSONA_PROMPT,
    TREE_OF_THOUGHTS_PROMPT,
    EXEMPLAR_STRUCTURES,
    QUALITY_ENFORCEMENT_PROMPTS
)
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class AdvancedContentAgent(BaseAgent):
    """Advanced agent for creating high-quality educational content of any duration"""
    
    def __init__(self, name: str, llm_service: LLMService):
        super().__init__(name)
        self.llm = llm_service
        
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process content research requests with advanced techniques"""
        # First simulate (following CLAUDE.md)
        simulation = self.simulate_algorithm(message.payload.get("topic", ""))
        
        if message.action == "research" or message.action == "research_topic":
            topic = message.payload.get("topic", "")
            context = message.payload.get("context", "")
            full_prompt = message.payload.get("full_prompt", topic)
            iteration = message.payload.get("iteration", 0)
            # Get dynamic requirements or use defaults
            if "requirements" not in message.payload:
                # Generate requirements based on duration if not provided
                from ..config.meta_prompt_framework import get_minimum_requirements
                duration_minutes = 10  # Default if not specified
                requirements = get_minimum_requirements(duration_minutes)
            else:
                requirements = message.payload.get("requirements", {})
            
            # Generate comprehensive content using advanced techniques
            content = await self._generate_advanced_content(topic, context, full_prompt, iteration, requirements)
            
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                action="content_ready",
                payload={"content": content}
            )
        
        return message
    
    async def _generate_advanced_content(self, topic: str, context: str = "", full_prompt: str = "", iteration: int = 0, requirements: dict = {}) -> dict:
        """Generate educational content using advanced techniques, scaled to requested duration"""
        
        # Get dynamic configuration based on actual requested duration
        duration_minutes = requirements.get("duration", 180) // 60
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        
        # Scale requirements to duration
        duration_text = f"{duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
        
        # Import dynamic prompt functions
        from ..config.meta_prompt_framework import (
            get_persona_prompt,
            get_chain_of_thought_prompt,
            get_tree_of_thoughts_prompt
        )
        
        # Combine all advanced prompting techniques scaled to duration
        system_prompt = f"""{get_persona_prompt(duration_minutes)}

{get_chain_of_thought_prompt(duration_minutes)}

{get_tree_of_thoughts_prompt(duration_minutes)}

{QUALITY_ENFORCEMENT_PROMPTS['depth_check'] if duration_minutes > 5 else ''}
        
You are creating a {duration_text} educational video.
Your content must be:
- APPROPRIATE: {config['style']}
- ENGAGING: Every second counts
- VISUAL: {config['detail_level']}
- STRUCTURED: {config['pacing']}
- FOCUSED: Match depth to available time

REQUIREMENTS FOR {duration_text.upper()}:
- Duration: {duration_minutes * 60} seconds
- Sections: {config['sections']} sections
- Examples: {max(1, config['sections'] // 2)} examples
- Visuals: {duration_minutes * config['animations_per_minute']} animations
- Depth: {config['complexity']}"""
        
        # Use exemplar structure if available
        topic_key = topic.lower()
        exemplar = ""
        for key in EXEMPLAR_STRUCTURES:
            if key in topic_key:
                exemplar = f"\n\nFollow this proven structure:\n{EXEMPLAR_STRUCTURES[key]}"
                break
        
        # Build comprehensive prompt
        request_text = full_prompt if full_prompt else topic
        
        prompt = f"""Create a {duration_text} educational video for: {request_text}

{exemplar}

REQUIREMENTS FOR {duration_text.upper()}:
1. Video duration: {duration_minutes * 60} seconds
2. Number of sections: {config['sections']}
3. Each section: {config['section_duration']} seconds
4. Hook: {config['hook_duration']} seconds
5. Complexity: {config['complexity']}
6. Pacing: {config['pacing']}

CONTENT STRUCTURE:

CONTENT STRUCTURE FOR {duration_text.upper()}:

1. HOOK ({config['hook_duration']} seconds):
   - {'Quick attention grabber' if duration_minutes <= 1 else 'Intriguing question'}
   - {'Core value' if duration_minutes <= 2 else 'Why this matters'}
   
2. MAIN CONTENT ({config['sections']-1} sections, {config['section_duration']} seconds each):
   - {config['detail_level']}
   - {config['complexity']} explanations
   
3. SUMMARY ({config['summary_duration']} seconds):
   - Key takeaways
   - {'Quick recap' if duration_minutes <= 2 else 'Deeper insights'}

For EACH SECTION provide:
- {'Brief explanation' if duration_minutes <= 1 else 'Clear explanation'}
- {f'{config["animations_per_minute"]} animations per minute' if duration_minutes > 1 else 'Essential animations'}
- {'Key formulas only' if duration_minutes <= 3 else 'Mathematical formulas if relevant'}
- {'One example' if duration_minutes <= 2 else 'Examples as needed'}

VISUAL REQUIREMENTS FOR {duration_text.upper()}:
- {config['complexity']} visual complexity
- {duration_minutes * config['animations_per_minute']} total animations
- {'Essential visuals only' if duration_minutes <= 1 else 'Appropriate visual richness'}

{context}

REMEMBER: This is competing with the best educational content on YouTube!
Make it absolutely extraordinary. Take your time. Think deeply."""
        
        schema = {
            "title": "string - compelling, clear title",
            "total_duration": f"number - total seconds ({duration_minutes * 60})",
            "sections": [
                {
                    "name": "string - section name",
                    "content": "string - comprehensive content (multiple paragraphs)",
                    "visual_elements": "string - detailed visual descriptions",
                    "formulas": ["mathematical formulas if applicable"],
                    "examples": ["concrete examples"],
                    "duration": f"number - seconds ({config['section_duration']})"
                }
            ],
            "key_concepts": [f"{config['sections']} core concepts"],
            "prerequisites": ["prerequisite knowledge"],
            "difficulty_progression": {
                "start": "string - starting level",
                "end": "string - ending level",
                "milestones": ["progression milestones"]
            },
            "visual_opportunities": [f"{duration_minutes * config['animations_per_minute']} animation opportunities"],
            "practice_problems": ["problems for viewers to try"],
            "further_exploration": ["advanced topics to explore"],
            "references": ["key papers or resources"]
        }
        
        try:
            # Use higher token limit for comprehensive content
            content = await self.llm.generate_json_with_retry(
                prompt,
                system_prompt,
                schema=schema,
                temperature=0.8,  # Higher for creativity
                max_tokens=None,  # Let token optimizer decide
                max_retries=3
            )
            
            # Validate comprehensive requirements
            validation_result = self._validate_advanced_content(content, requirements)
            
            if not validation_result["valid"]:
                logger.warning(f"Content validation failed: {validation_result['issues']}")
                # Add remediation instructions
                content["needs_expansion"] = validation_result["issues"]
            
            logger.info(f"Generated advanced content: {len(content.get('sections', []))} sections, {content.get('total_duration', 0)}s duration")
            return content
            
        except Exception as e:
            logger.error(f"Error generating advanced content: {e}")
            raise Exception(f"Failed to generate comprehensive content: {str(e)}")
    
    def _validate_advanced_content(self, content: dict, requirements: dict) -> dict:
        """Validate content meets duration requirements"""
        issues = []
        
        # Check duration
        duration = content.get("total_duration", 0)
        if duration < requirements.get("duration", 600):
            issues.append(f"Duration too short: {duration}s < {requirements['duration']}s")
        
        # Check section count
        sections = content.get("sections", [])
        if len(sections) < requirements.get("concepts", 10):
            issues.append(f"Too few sections: {len(sections)} < {requirements['concepts']}")
        
        # Check content depth
        for i, section in enumerate(sections):
            content_length = len(section.get("content", ""))
            if content_length < 300:  # Each section should be detailed
                issues.append(f"Section {i+1} content too brief: {content_length} chars")
            
            # Note: Animations are part of visual design, not content
            
            if not section.get("examples", []):
                issues.append(f"Section {i+1} lacks examples")
        
        # Check visual richness
        visual_count = len(content.get("visual_opportunities", []))
        if visual_count < requirements.get("visuals", 50):
            issues.append(f"Insufficient visuals: {visual_count} < {requirements['visuals']}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "metrics": {
                "duration": duration,
                "sections": len(sections),
                "visuals": visual_count,
                "avg_section_length": sum(len(s.get("content", "")) for s in sections) / max(len(sections), 1)
            }
        }