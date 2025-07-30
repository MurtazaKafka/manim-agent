from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import LLMService
from .prompt_templates import DynamicPromptGenerator
import asyncio
import logging

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """Agent responsible for researching and structuring educational content"""
    
    def __init__(self, name: str, llm_service: LLMService):
        super().__init__(name)
        self.llm = llm_service
        
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process content research requests"""
        # First simulate (following CLAUDE.md)
        simulation = self.simulate_algorithm(message.payload.get("topic", ""))
        
        if message.action == "research" or message.action == "research_topic":
            topic = message.payload.get("topic", "")
            context = message.payload.get("context", "")
            full_prompt = message.payload.get("full_prompt", topic)
            requirements = message.payload.get("requirements", {})
            duration_minutes = requirements.get("duration", 180) // 60  # Convert to minutes
            
            # Generate content using LLM with context
            content = await self._generate_content(topic, context, full_prompt, duration_minutes)
            
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                action="content_ready",
                payload={"content": content}
            )
        
        return message
    
    async def _generate_content(self, topic: str, context: str = "", full_prompt: str = "", duration_minutes: int = 3) -> dict:
        """Generate educational content structure using LLM"""
        # Get dynamic system prompt based on duration
        system_prompt = DynamicPromptGenerator.get_content_system_prompt(duration_minutes)
        
        # Use full prompt if available (includes context), otherwise just topic
        request_text = full_prompt if full_prompt else topic
        
        # Get dynamic requirements based on duration
        requirements = DynamicPromptGenerator.get_content_requirements(duration_minutes)
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
            
        prompt = f"""Create an educational video script for: {request_text}

        {requirements}
        
        Structure your response as:
        
        1. TITLE: Engaging, clear title
        
        2. HOOK ({config['hook_duration']} seconds): 
           - {'Quick attention grabber' if duration_minutes <= 1 else 'Intriguing question or surprising fact'}
           - {'Core value proposition' if duration_minutes <= 2 else 'Show why this concept matters'}
           - {'Brief preview' if duration_minutes <= 1 else 'Preview what viewers will learn'}
        
        3. SECTIONS ({config['section_range']} sections, {config['section_duration']} seconds each):
           For each section provide:
           - Section name
           - Explanation appropriate for the duration
           - Specific visual elements to animate
           - Mathematical formulas or examples
           - Transitions to next section
        
        4. KEY CONCEPTS: List {max(2, config['sections'])} core ideas being taught
        
        5. VISUAL ELEMENTS: Specific Manim objects needed
           - Graphs, equations, geometric shapes
           - Transformations and animations
           - Color coding for clarity
        
        Example for "Derivative": Don't just show the formula. Start with rate of change in real life, 
        animate a car's position graph, zoom into smaller time intervals, show the limiting process, 
        derive the formula visually, then show applications.
        
        REMEMBER: Create content that's {config['style']} and matches the {duration_minutes}-minute duration."""
        
        schema = {
            "title": "string - engaging title for the video",
            "sections": [
                {
                    "name": "string - section name",
                    "content": "string - detailed content to cover",
                    "visual_elements": "string - what to show visually",
                    "duration": "number - seconds for this section"
                }
            ],
            "key_concepts": ["list of key concepts"],
            "prerequisites": ["list of prerequisite knowledge"],
            "difficulty": "string - beginner/intermediate/advanced",
            "visual_opportunities": ["list of opportunities for animation"],
            "common_misconceptions": ["list of misconceptions to address"]
        }
        
        try:
            content = await self.llm.generate_json_with_retry(
                prompt,
                system_prompt,
                schema=schema,
                temperature=0.7 if duration_minutes > 3 else 0.5,  # Less creative for short videos
                max_retries=2 if duration_minutes <= 3 else 3
            )
            
            # Validate response has required fields
            required_fields = ["title", "sections", "key_concepts", "difficulty"]
            for field in required_fields:
                if field not in content:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure sections have duration and enforce minimum video length
            total_duration = 0
            # Adjust minimum sections based on duration
            if duration_minutes <= 1:
                min_sections = 2  # 2 sections for 1-minute videos
            elif duration_minutes <= 3:
                min_sections = 3  # 3 sections for 2-3 minute videos
            else:
                min_sections = 4  # 4+ sections for longer videos
            
            # Ensure we have enough sections
            if len(content.get("sections", [])) < min_sections:
                logger.warning(f"Only {len(content.get('sections', []))} sections generated, minimum is {min_sections}")
                raise ValueError(f"Content too short: need at least {min_sections} sections for a {duration_minutes}-minute video")
            
            for section in content.get("sections", []):
                if "duration" not in section:
                    # Default duration based on video length and section count
                    num_sections = len(content.get("sections", []))
                    default_duration = (duration_minutes * 60) // num_sections
                    section["duration"] = max(15, min(default_duration, 45))  # Between 15-45 seconds
                total_duration += section["duration"]
            
            # Enforce duration to match requested length
            target_duration = duration_minutes * 60  # Convert to seconds
            # Allow 10% variance for short videos, 5% for longer
            tolerance = 0.1 if duration_minutes <= 3 else 0.05
            min_duration = int(target_duration * (1 - tolerance))
            max_duration = int(target_duration * (1 + tolerance))
            
            if total_duration < min_duration or total_duration > max_duration:
                # Scale durations to fit target
                scale_factor = target_duration / total_duration
                for section in content.get("sections", []):
                    section["duration"] = int(section["duration"] * scale_factor)
                total_duration = sum(s["duration"] for s in content.get("sections", []))
            
            # Add total duration
            content["total_duration"] = total_duration
            
            logger.info(f"Generated content for '{topic}' with {len(content['sections'])} sections, total duration: {total_duration}s")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content for '{topic}': {e}")
            # NO FALLBACKS - This is for YC!
            raise Exception(f"Failed to generate content after retries: {str(e)}")