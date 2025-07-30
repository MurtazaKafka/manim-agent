import asyncio
import os
from typing import Dict, List, Optional
from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import create_llm_service, LLMProvider
from ..agents.content_agent import ContentAgent
from ..agents.visual_design_agent import VisualDesignAgent
from ..agents.manim_code_agent import ManimCodeAgent
import time
import logging

logger = logging.getLogger(__name__)


class ManimExplainerAgent:
    """Main orchestrator for the Manim explainer video system"""
    
    def __init__(self, llm_provider: LLMProvider = LLMProvider.OPENAI, api_key: Optional[str] = None):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_service = create_llm_service(llm_provider, api_key=api_key)
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        self.agents["content"] = ContentAgent("content_agent", self.llm_service)
        self.agents["visual_design"] = VisualDesignAgent("visual_design_agent", self.llm_service)
        self.agents["manim_code"] = ManimCodeAgent("manim_code_agent", self.llm_service)
        
    async def create_video(self, user_prompt: str, context: str = "", model: str = "sonnet", duration_minutes: int = 3, status_callback=None, stream_callback=None) -> str:
        """
        Main entry point - converts user prompt to Manim video
        Following CLAUDE.md: First simulate, then execute
        
        Args:
            user_prompt: The topic/prompt for the video
            context: Additional context (e.g., conversation history)
            model: "opus" or "sonnet"
            duration_minutes: Target video duration in minutes
            status_callback: Optional callback for status updates
            stream_callback: Optional callback for streaming responses
        """
        # Simulate the entire workflow first
        simulation = self._simulate_workflow(user_prompt)
        logger.info(f"Workflow simulation complete for: {user_prompt}")
        
        # Execute the workflow
        try:
            # Step 1: Process content
            logger.info("Step 1: Researching content...")
            content_msg = AgentMessage(
                sender="orchestrator",
                recipient="content_agent",
                action="research_topic",
                payload={"topic": user_prompt},
                timestamp=time.time()
            )
            content_response = await self.agents["content"].process(content_msg)
            
            # Step 2: Design visuals
            logger.info("Step 2: Designing visual elements...")
            visual_msg = AgentMessage(
                sender="orchestrator",
                recipient="visual_design_agent",
                action="design_visuals",
                payload={
                    "content": content_response.payload,
                    "topic": user_prompt
                },
                timestamp=time.time()
            )
            visual_response = await self.agents["visual_design"].process(visual_msg)
            
            # Step 3: Generate Manim code
            logger.info("Step 3: Generating Manim code...")
            manim_msg = AgentMessage(
                sender="orchestrator",
                recipient="manim_code_agent",
                action="generate_code",
                payload={
                    "content": content_response.payload,
                    "visual_design": visual_response.payload,
                    "topic": user_prompt
                },
                timestamp=time.time()
            )
            manim_response = await self.agents["manim_code"].process(manim_msg)
            
            manim_code = manim_response.payload.get("code", "")
            
            if manim_code:
                logger.info("Successfully generated Manim code")
                return manim_code
            else:
                logger.error("No Manim code generated")
                return ""
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            # NO FALLBACKS - This is production code for YC!
            raise Exception(f"Failed to generate animation: {str(e)}")
    
    def _simulate_workflow(self, user_prompt: str) -> Dict:
        """Mentally simulate the entire workflow before execution"""
        return {
            "input": user_prompt,
            "steps": [
                "Parse user request for topic and requirements",
                "Content agent researches and structures educational content",
                "Visual design agent plans animations and visual flow",
                "Manim code agent generates executable Python code",
                "Validate and prepare for rendering"
            ],
            "expected_output": "Complete Manim Python code ready for rendering",
            "potential_issues": [
                "Complex mathematical concepts requiring special handling",
                "LLM API failures or rate limits",
                "Invalid code generation requiring fallbacks",
                "Timing synchronization between content and visuals"
            ],
            "mitigation_strategies": [
                "Implement retry logic for API calls",
                "Provide fallback templates for common topics",
                "Validate generated code before returning",
                "Use conservative timing estimates"
            ]
        }
    
    def _generate_error_fallback(self, topic: str, error: str) -> str:
        """Generate a simple fallback Manim code when errors occur"""
        logger.warning(f"Generating fallback code due to error: {error}")
        
        class_name = "".join(word.capitalize() for word in topic.split()[:3]) + "Explainer"
        class_name = "".join(c for c in class_name if c.isalnum()) or "TopicExplainer"
        
        return f"""from manim import *

class {class_name}(Scene):
    def construct(self):
        # Title
        title = Text("{topic}", font_size=48)
        self.play(Write(title))
        self.wait(2)
        
        # Error message (can be removed in production)
        error_text = Text(
            "Content is being generated...",
            font_size=24,
            color=YELLOW
        )
        error_text.next_to(title, DOWN, buff=1)
        self.play(FadeIn(error_text))
        self.wait(2)
        
        # Basic animation
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=2, color=GREEN)
        
        self.play(Create(circle))
        self.wait(1)
        self.play(Transform(circle, square))
        self.wait(1)
        
        # Conclusion
        conclusion = Text(
            "Thank you for watching!",
            font_size=36
        )
        self.play(
            FadeOut(title),
            FadeOut(error_text),
            FadeOut(circle),
            Write(conclusion)
        )
        self.wait(2)
"""