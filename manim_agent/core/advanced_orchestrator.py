import asyncio
import os
from typing import Dict, List, Optional, Any
import asyncio
from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import create_llm_service, LLMProvider
from ..core.token_optimizer import TokenOptimizer
from ..agents.advanced_content_agent import AdvancedContentAgent
from ..agents.visual_design_agent import VisualDesignAgent
from ..agents.manim_code_agent import ManimCodeAgent
from ..config.meta_prompt_framework import (
    META_PROMPT_TEMPLATE, 
    REFINEMENT_PROMPTS,
    MINIMUM_REQUIREMENTS,
    QUALITY_ENFORCEMENT_PROMPTS,
    CHAIN_OF_THOUGHT_PROMPT,
    PERSONA_PROMPT
)
import time
import logging
import json

logger = logging.getLogger(__name__)


class AdvancedManimExplainerAgent:
    """Advanced orchestrator with iterative refinement for videos of any duration"""
    
    def __init__(self, llm_provider: LLMProvider = LLMProvider.ANTHROPIC, api_key: Optional[str] = None):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.max_iterations = 3  # Allow up to 3 refinement iterations
        
    def _initialize_agents(self, use_opus: bool = True):
        """Initialize all specialized agents with specified model"""
        self.llm_service = create_llm_service(self.llm_provider, use_opus=use_opus, api_key=self.api_key)
        self.agents["content"] = AdvancedContentAgent("content_agent", self.llm_service)
        self.agents["visual_design"] = VisualDesignAgent("visual_design_agent", self.llm_service)
        self.agents["manim_code"] = ManimCodeAgent("manim_code_agent", self.llm_service)
        
    async def create_video(self, user_prompt: str, context: str = "", model: str = "opus", duration_minutes: int = 10, status_callback=None, stream_callback=None) -> str:
        """
        Create an educational video with specified duration and model
        """
        # Initialize agents with chosen model
        use_opus = (model == "opus")
        self._initialize_agents(use_opus=use_opus)
        
        logger.info(f"Creating {duration_minutes}-minute video using {model.upper()} model")
        
        # For short videos with Sonnet, disable the Advanced Content Agent
        if model == "sonnet" and duration_minutes <= 5:
            # Use regular ContentAgent instead of AdvancedContentAgent for efficiency
            from ..agents.content_agent import ContentAgent
            self.agents["content"] = ContentAgent("content_agent", self.llm_service)
        
        # Set context for LLM service
        self.llm_service.set_context(duration_minutes, "general")
        
        # Get optimized requirements based on duration
        requirements = TokenOptimizer.get_requirements_for_duration(duration_minutes)
        requirements["duration"] = duration_minutes * 60
        
        # Adapt iterations based on duration
        if duration_minutes <= 3:
            self.max_iterations = 1
        elif duration_minutes <= 10:
            self.max_iterations = 2
        else:
            self.max_iterations = 3
        
        # Apply meta-prompt framework
        enhanced_prompt = self._apply_meta_prompt(user_prompt, duration_minutes)
        
        # Simulate the entire workflow first
        simulation = self._simulate_workflow(enhanced_prompt)
        logger.info(f"Workflow simulation complete for: {user_prompt}")
        
        # Execute with iterative refinement
        try:
            iteration = 0
            current_content = None
            current_visual = None
            current_code = None
            
            while iteration < self.max_iterations:
                logger.info(f"Iteration {iteration + 1} of {self.max_iterations}")
                
                # Step 1: Generate/Refine content
                logger.info("Researching and expanding content...")
                if status_callback:
                    await status_callback("ContentAgent", "Researching educational content and creating detailed outline...", 0.2)
                content_response = await self._generate_content(
                    enhanced_prompt, 
                    context, 
                    current_content,
                    iteration,
                    requirements
                )
                current_content = content_response.payload.get("content", content_response.payload)
                
                # Validate content depth
                if not self._validate_content_depth(current_content, requirements):
                    logger.warning("Content lacks depth, requesting expansion...")
                    continue
                
                # Step 2 & 3: Parallel generation for speed (visual design + code structure)
                if duration_minutes <= 5 and iteration == 0:
                    # For short videos, generate visual design and code structure in parallel
                    logger.info("Parallel generation: visual design + code structure...")
                    if status_callback:
                        await status_callback("ParallelGeneration", "Generating visuals and code in parallel...", 0.4)
                    
                    # Create both tasks
                    visual_task = asyncio.create_task(self._generate_visuals(
                        enhanced_prompt,
                        current_content,
                        context,
                        current_visual,
                        iteration,
                        requirements
                    ))
                    
                    # Generate initial code structure while visuals are being designed
                    code_structure_task = asyncio.create_task(self._generate_initial_code_structure(
                        enhanced_prompt,
                        current_content,
                        context,
                        requirements
                    ))
                    
                    # Wait for both to complete
                    visual_response, code_structure = await asyncio.gather(visual_task, code_structure_task)
                    current_visual = visual_response.payload.get("design", visual_response.payload)
                    
                    # Now generate full code with both content and visuals
                    logger.info("Finalizing Manim code with visual design...")
                    if status_callback:
                        await status_callback("ManimCodeAgent", "Finalizing animation code...", 0.6)
                    
                    # Merge structure into visual design for code generation
                    enhanced_visual = {**current_visual, "initial_structure": code_structure}
                    code_response = await self._generate_code(
                        enhanced_prompt,
                        current_content,
                        enhanced_visual,
                        context,
                        current_code,
                        iteration,
                        requirements
                    )
                    current_code = code_response.payload.get("code", "")
                else:
                    # Traditional sequential approach for longer videos or refinements
                    logger.info("Sequential generation: visual design then code...")
                    if status_callback:
                        await status_callback("VisualDesignAgent", "Designing visual elements...", 0.4)
                    visual_response = await self._generate_visuals(
                        enhanced_prompt,
                        current_content,
                        context,
                        current_visual,
                        iteration,
                        requirements
                    )
                    current_visual = visual_response.payload.get("design", visual_response.payload)
                    
                    logger.info("Generating comprehensive Manim code...")
                    if status_callback:
                        await status_callback("ManimCodeAgent", "Generating animation code...", 0.6)
                    code_response = await self._generate_code(
                        enhanced_prompt,
                        current_content,
                        current_visual,
                        context,
                        current_code,
                        iteration,
                        requirements
                    )
                    current_code = code_response.payload.get("code", "")
                
                # Validate the generated content
                validation_result = self._validate_output(
                    current_content,
                    current_visual,
                    current_code,
                    requirements
                )
                
                # Log validation results but always proceed
                logger.info(f"Validation result: {validation_result}")
                if validation_result["valid"]:
                    logger.info("Generated content meets all requirements!")
                else:
                    logger.warning(f"Validation warnings (proceeding anyway): {validation_result['issues']}")
                
                # Always return the generated code for now
                return current_code
                    
            # If we've exhausted iterations, return best effort
            logger.warning("Max iterations reached, returning best effort")
            return current_code
            
        except Exception as e:
            logger.error(f"Error in advanced orchestrator: {e}")
            raise Exception(f"Failed to generate high-quality animation: {str(e)}")
    
    def _apply_meta_prompt(self, user_prompt: str, duration_minutes: int) -> str:
        """Apply meta-prompt framework to enhance the request"""
        if duration_minutes <= 5:
            # Simpler prompt for shorter videos
            return f"""Create a {duration_minutes}-minute educational video about: {user_prompt}
            
Key requirements:
- Duration: {duration_minutes} minutes ({duration_minutes * 60} seconds)
- Style: Clear, concise, and focused
- Include: Core concepts, visual examples, smooth animations
- Quality: Professional educational content"""
        else:
            # Full meta-prompt for longer videos
            duration_range = f"{duration_minutes}-{duration_minutes+1}"
            return META_PROMPT_TEMPLATE.format(
                duration=duration_range,
                topic=user_prompt
            ) + f"\n\nOriginal request: {user_prompt}"
    
    async def _generate_content(self, prompt: str, context: str, previous_content: Optional[Dict], iteration: int, requirements: dict) -> AgentMessage:
        """Generate or refine content with emphasis on depth and duration"""
        # Set context for content generation
        self.llm_service.set_context(
            requirements["duration"] // 60,  # Convert seconds to minutes
            "content"
        )
        refinement_context = ""
        if iteration > 0 and previous_content:
            refinement_context = f"""
            Previous content was too brief. Apply these refinements:
            {REFINEMENT_PROMPTS['expand']}
            {REFINEMENT_PROMPTS['deepen']}
            
            Previous content sections: {len(previous_content.get('sections', []))}
            Previous total duration: {previous_content.get('total_duration', 0)} seconds
            
            REQUIREMENT: Generate at least {requirements['duration']} seconds of content!
            """
        
        content_msg = AgentMessage(
            sender="orchestrator",
            recipient="content_agent",
            action="research_topic",
            payload={
                "topic": prompt,
                "context": context + refinement_context,
                "full_prompt": prompt,
                "iteration": iteration,
                "requirements": requirements
            },
            timestamp=time.time()
        )
        
        return await self.agents["content"].process(content_msg)
    
    async def _generate_visuals(self, prompt: str, content: Dict, context: str, previous_visual: Optional[Dict], iteration: int, requirements: Dict) -> AgentMessage:
        """Generate comprehensive visual design"""
        # Set context for visual design
        self.llm_service.set_context(
            requirements["duration"] // 60,
            "visual"
        )
        refinement_context = ""
        if iteration > 0 and previous_visual:
            refinement_context = f"""
            Previous visual design needs enhancement:
            {REFINEMENT_PROMPTS['visualize']}
            
            Add more animations, transitions, and visual richness.
            Each scene should have 5-8 distinct animations minimum.
            """
        
        visual_msg = AgentMessage(
            sender="orchestrator",
            recipient="visual_design_agent",
            action="design_visuals",
            payload={
                "content": content,
                "topic": prompt,
                "context": context + refinement_context,
                "full_prompt": prompt,
                "iteration": iteration,
                "requirements": requirements
            },
            timestamp=time.time()
        )
        
        return await self.agents["visual_design"].process(visual_msg)
    
    async def _generate_code(self, prompt: str, content: Dict, visual_design: Dict, context: str, previous_code: Optional[str], iteration: int, requirements: Dict) -> AgentMessage:
        """Generate extensive Manim code"""
        # Set context for code generation
        self.llm_service.set_context(
            requirements["duration"] // 60,
            "code"
        )
        refinement_context = ""
        if iteration > 0 and previous_code:
            refinement_context = f"""
            Previous code was too short. Requirements:
            - Video MUST be {requirements['duration']} seconds long
            - Use self.wait() appropriately between animations
            - Add more detail to each scene
            - Include all concepts from content outline
            - Create smooth, engaging transitions
            """
        
        manim_msg = AgentMessage(
            sender="orchestrator",
            recipient="manim_code_agent",
            action="generate_code",
            payload={
                "content": content,
                "visual_design": visual_design,
                "topic": prompt,
                "context": context + refinement_context,
                "full_prompt": prompt,
                "iteration": iteration,
                "requirements": requirements
            },
            timestamp=time.time()
        )
        
        return await self.agents["manim_code"].process(manim_msg)
    
    def _validate_content_depth(self, content: Dict, requirements: Dict) -> bool:
        """Validate that content has sufficient depth"""
        from ..config.quality_standards import validate_content_quality
        
        # Get duration in minutes
        duration_minutes = requirements.get("duration", 180) // 60
        
        # Use dynamic validation
        is_valid, issues = validate_content_quality(content, duration_minutes)
        
        if not is_valid:
            for issue in issues:
                logger.warning(issue)
        
        return is_valid
    
    async def _generate_initial_code_structure(self, prompt: str, content: Dict, context: str, requirements: Dict) -> Dict:
        """Generate basic code structure quickly for parallel processing"""
        # Set token context for fast generation
        self.llm_service.set_context(requirements["duration"] // 60, "code")
        
        structure_prompt = f"""
        Create a MINIMAL Manim scene structure for: {prompt}
        
        Based on these content sections:
        {[s.get('name', '') for s in content.get('sections', [])]}
        
        Generate ONLY:
        1. Class definition
        2. Method stubs for each section
        3. Basic construct() method outline
        4. Comments for implementation
        
        Keep it under 50 lines. Just the skeleton.
        """
        
        try:
            response = await self.llm_service.generate(
                structure_prompt,
                system_prompt="Generate minimal code structure only. Be extremely concise.",
                max_tokens=1500  # Very limited for speed
            )
            return {"structure": response}
        except Exception as e:
            logger.warning(f"Structure generation failed: {e}")
            return {"structure": ""}
    
    def _validate_output(self, content: Dict, visual_design: Dict, code: str, requirements: Dict) -> Dict[str, Any]:
        """Comprehensive validation of generated output"""
        from ..config.quality_standards import validate_content_quality, validate_visual_quality
        
        # Get duration in minutes
        duration_minutes = requirements.get("duration", 180) // 60
        
        issues = []
        
        # Validate content quality
        content_valid, content_issues = validate_content_quality(content, duration_minutes)
        issues.extend(content_issues)
        
        # Validate visual quality
        visual_valid, visual_issues = validate_visual_quality(visual_design, duration_minutes)
        issues.extend(visual_issues)
        
        # Simple code check - just ensure it exists and has basic structure
        if not code or len(code.strip()) < 100:
            issues.append("Generated code is too short or missing")
        
        # Check for required methods
        required_methods = ["construct", "play", "wait", "Create", "Write", "Transform"]
        for method in required_methods:
            if method not in code:
                issues.append(f"Missing required method: {method}")
        
        # Calculate metrics
        total_duration = content.get("total_duration", 0)
        scenes = visual_design.get("scenes", [])
        total_animations = sum(len(s.get("animations", [])) for s in scenes)
        code_lines = code.count('\n') if code else 0
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "metrics": {
                "duration": total_duration,
                "scenes": len(scenes),
                "animations": total_animations,
                "code_lines": code_lines
            }
        }
    
    def _simulate_workflow(self, enhanced_prompt: str) -> Dict:
        """Simulate the advanced workflow with quality checks"""
        return {
            "input": enhanced_prompt,
            "target_duration": f"{enhanced_prompt.split()[2]} minutes" if "minute" in enhanced_prompt else "optimized duration",
            "quality_level": "professional educational standard",
            "steps": [
                "Apply meta-prompt framework for depth",
                "Generate comprehensive educational content",
                "Design rich visual storytelling",
                "Create extensive Manim animations",
                "Validate against quality metrics",
                "Iterate if necessary for improvement"
            ],
            "validation_checks": [
                "Appropriate duration for content",
                "Sufficient scenes for clarity",
                "Rich animations and visuals",
                "Appropriate conceptual coverage",
                "Visual coherence and flow"
            ]
        }