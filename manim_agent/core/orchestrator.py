import asyncio
from typing import Dict, List, Optional
from ..core.base_agent import BaseAgent, AgentMessage
from ..agents.content_agent import ContentAgent
from ..agents.manim_code_agent import ManimCodeAgent
import time


class ManimExplainerAgent:
    """Main orchestrator for the Manim explainer video system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        self.agents["content"] = ContentAgent("content_agent")
        self.agents["manim_code"] = ManimCodeAgent("manim_code_agent")
        
    async def create_video(self, user_prompt: str) -> str:
        """
        Main entry point - converts user prompt to Manim video
        Following CLAUDE.md: First simulate, then execute
        """
        # Simulate the entire workflow first
        simulation = self._simulate_workflow(user_prompt)
        print(f"Workflow simulation: {simulation}")
        
        # Execute the workflow
        try:
            # Step 1: Process content
            content_msg = AgentMessage(
                sender="orchestrator",
                recipient="content_agent",
                action="research_topic",
                payload={"topic": user_prompt},
                timestamp=time.time()
            )
            content_response = await self.agents["content"].process(content_msg)
            
            # Step 2: Generate Manim code
            manim_msg = AgentMessage(
                sender="orchestrator",
                recipient="manim_code_agent",
                action="generate_code",
                payload={
                    "content": content_response.payload,
                    "topic": user_prompt
                },
                timestamp=time.time()
            )
            manim_response = await self.agents["manim_code"].process(manim_msg)
            
            return manim_response.payload.get("code", "")
            
        except Exception as e:
            print(f"Error in orchestrator: {e}")
            return ""
    
    def _simulate_workflow(self, user_prompt: str) -> Dict:
        """Mentally simulate the entire workflow before execution"""
        return {
            "input": user_prompt,
            "steps": [
                "Parse user request",
                "Content agent researches topic",
                "Visual agent designs animations",
                "Code agent generates Manim code",
                "Render video"
            ],
            "expected_output": "Manim video file",
            "potential_issues": [
                "Complex mathematical concepts",
                "Rendering errors",
                "Timing synchronization"
            ]
        }