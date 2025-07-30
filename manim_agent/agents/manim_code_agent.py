from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import LLMService
import asyncio
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ManimCodeAgent(BaseAgent):
    """Agent responsible for generating Manim animation code"""
    
    def __init__(self, name: str, llm_service: LLMService):
        super().__init__(name)
        self.llm = llm_service
    
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process code generation requests"""
        # First simulate (following CLAUDE.md)
        simulation = self.simulate_algorithm("Generate Manim code")
        
        if message.action == "generate_code":
            content = message.payload.get("content", {})
            visual_design = message.payload.get("visual_design", {})
            topic = message.payload.get("topic", "")
            context = message.payload.get("context", "")
            full_prompt = message.payload.get("full_prompt", topic)
            requirements = message.payload.get("requirements", {})
            duration_minutes = requirements.get("duration", 180) // 60
            
            # Generate Manim code based on content and visual design with context
            manim_code = await self._generate_manim_code(content, visual_design, topic, context, full_prompt, duration_minutes)
            
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                action="code_ready",
                payload={"code": manim_code}
            )
        
        return message
    
    async def _generate_manim_code(self, content: Dict[str, Any], visual_design: Dict[str, Any], topic: str, context: str = "", full_prompt: str = "", duration_minutes: int = 3) -> str:
        """Generate Manim scene code using LLM"""
        # Adjust system prompt based on duration
        if duration_minutes <= 1:
            system_prompt = """You are a Manim expert creating concise educational animations.
            Create CLEAR, FOCUSED animations for a 1-minute video.
            Use simple, direct animations without excessive complexity."""
        elif duration_minutes <= 3:
            system_prompt = """You are a Manim expert creating educational animations.
            Create engaging animations that teach concepts clearly in 2-3 minutes.
            Balance visual appeal with educational clarity."""
        else:
            system_prompt = """You are a Manim expert creating 3Blue1Brown-quality educational animations.
            
            Your code must:
            1. Create SMOOTH, BEAUTIFUL animations that teach concepts intuitively
            2. Use PROGRESSIVE DISCLOSURE - build complexity gradually
            3. Include VISUAL METAPHORS and concrete examples
            4. Implement SMOOTH TRANSITIONS between all elements
            5. Generate AT LEAST 2-3 minutes of engaging content
            
            Key coding principles:
            - Use rate_func=smooth for most animations
        - Chain animations with self.play() for fluid motion
        - Use VGroup for coordinated animations
        - Implement custom animations for unique effects
        - Use updaters for dynamic relationships
        - Apply consistent color schemes
        - Add proper wait times for comprehension
        
        Visual techniques:
        - Start with a hook/question
        - Build equations step by step
        - Use Transform/ReplacementTransform for morphing
        - Animate along paths for smooth motion
        - Use FadeIn/FadeOut sparingly - prefer transformations
        - Implement camera movements for focus
        - Create custom animations for "wow" moments
        
        IMPORTANT: Use modern Manim API:
        - Use Create() instead of ShowCreation()
        - Use Indicate() instead of CircleIndicate()
        - Use Wiggle() instead of WiggleOutThenIn()
        - Avoid any deprecated animations
        
        NEVER just display text or formulas - ALWAYS animate their appearance and relationships!"""
        
        # Prepare context for code generation
        scenes_summary = []
        for scene in visual_design.get("scenes", []):
            scene_desc = {
                "description": scene["description"],
                "duration": scene["duration"],
                "objects": [obj["type"] for obj in scene.get("manim_objects", [])],
                "animations": [anim["type"] for anim in scene.get("animations", [])]
            }
            scenes_summary.append(scene_desc)
        
        # Include context if available
        context_text = f"\n{context}\n" if context else ""
        
        prompt = f"""Generate complete Manim code for this educational video request:

{full_prompt if full_prompt else topic}
{context_text}
        Content Overview:
        Title: {content.get('title', topic)}
        Total Duration: {content.get('total_duration', 180)} seconds
        Key Concepts: {', '.join(content.get('key_concepts', []))}
        
        If this is a refinement request, adjust the code to address the user's specific feedback.
        
        Visual Design:
        Number of Scenes: {len(visual_design.get('scenes', []))}
        Color Scheme: {json.dumps(visual_design.get('color_scheme', {}), indent=2)}
        
        Scene Breakdown:
        {json.dumps(scenes_summary, indent=2)}
        
        CRITICAL REQUIREMENTS:
        1. Video duration: {duration_minutes} minute{'s' if duration_minutes > 1 else ''} (use self.wait() appropriately)
        2. Start with an engaging visual hook ({10 if duration_minutes > 1 else 5}-{15 if duration_minutes > 1 else 10} seconds)
        3. Build concepts progressively - don't show everything at once
        4. Use smooth animations (rate_func=smooth) for all transitions
        5. Include at least {max(5, duration_minutes * 5)} distinct animations
        6. {'Implement visual metaphors to explain abstract concepts' if duration_minutes > 2 else 'Keep animations clear and simple'}
        7. Use color coding consistently to show relationships
        8. {'Add text overlays to reinforce key points' if duration_minutes > 1 else 'Use minimal text'}
        9. {'Create custom animations for important reveals' if duration_minutes > 3 else 'Focus on clarity over complexity'}
        10. End with a visual summary of key concepts
        
        CODE STRUCTURE:
        ```python
        from manim import *
        import numpy as np
        
        class [TopicName]Explainer(Scene):
            def construct(self):
                # Setup colors and styles
                self.setup_colors()
                
                # Scene 1: Hook (10-15 seconds)
                self.play_intro_hook()
                
                # Scene 2-5: Main content (30-40 seconds each)
                self.explain_concept_1()
                self.explain_concept_2()
                self.demonstrate_examples()
                self.show_applications()
                
                # Scene 6: Summary (15-20 seconds)
                self.summarize_key_points()
        ```
        
        EXAMPLE TECHNIQUES:
        - For equations: Build them piece by piece with Write() and Transform()
        - For graphs: Animate drawing axes, then plot functions with Create()
        - For concepts: Start with concrete example, then generalize
        - For transitions: Use ReplacementTransform() to morph between related objects
        - For emphasis: Use Indicate(), Flash(), or color changes
        
        REMEMBER: This is for YouTube! Make it visually stunning and educational!
        """
        
        try:
            # Generate the code with retry logic
            # Don't pass max_tokens to let token optimizer decide
            manim_code = await self.llm.generate_with_retry(
                prompt,
                system_prompt,
                temperature=0.3,  # Lower temperature for code generation
                max_retries=3
            )
            
            # Validate and clean the code
            manim_code = self._validate_and_clean_code(manim_code)
            
            logger.info(f"Generated Manim code for '{topic}' with {len(manim_code.splitlines())} lines")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            # NO FALLBACKS - We need real AI-generated code!
            raise Exception(f"Failed to generate Manim code after retries: {str(e)}")
    
    def _validate_and_clean_code(self, code: str) -> str:
        """Validate and clean generated Manim code"""
        # First check if there's markdown formatting with code blocks
        if "```python" in code:
            # Extract code between ```python and ```
            start_idx = code.find("```python")
            if start_idx != -1:
                start_idx += len("```python")
                end_idx = code.find("```", start_idx)
                if end_idx != -1:
                    code = code[start_idx:end_idx]
        elif "```" in code:
            # Handle plain ``` blocks
            start_idx = code.find("```")
            if start_idx != -1:
                start_idx += 3
                end_idx = code.find("```", start_idx)
                if end_idx != -1:
                    code = code[start_idx:end_idx]
        
        # Clean up the code
        code = code.strip()
        
        # Fix deprecated Manim animations
        deprecated_replacements = {
            "ShowCreation": "Create",
            "ShowIncreasingSubsets": "Create",
            "ShowSubmobjectsOneByOne": "Create",
            "DrawBorderThenFill": "DrawBorderThenFill",  # Still valid
            "ShowCreationThenDestruction": "ShowPassingFlash",
            "ShowCreationThenFadeOut": "lambda x: Succession(Create(x), FadeOut(x))",
            "ShowCreationThenDestructionAround": "ShowPassingFlashAround",
            "ShowCreationThenFadeAround": "lambda x: Succession(Create(x), FadeOut(x))",
            "ShowPassingFlashAround": "ShowPassingFlashAround",  # Still valid
            "ShowPassingFlash": "ShowPassingFlash",  # Still valid
            "WiggleOutThenIn": "Wiggle",
            "TurnInsideOut": "ApplyComplexFunction",
            "PointwiseBecome": "Transform",
            "CircleIndicate": "Indicate",
            "ShowCreationThenDestructionThenCreation": "lambda x: Succession(Create(x), Uncreate(x), Create(x))"
        }
        
        # Replace deprecated animations
        for old_anim, new_anim in deprecated_replacements.items():
            # Handle both direct usage and usage with parentheses
            code = code.replace(f"{old_anim}(", f"{new_anim}(")
            # Handle when used without parentheses (e.g., in lists)
            code = code.replace(f" {old_anim},", f" {new_anim},")
            code = code.replace(f" {old_anim}\n", f" {new_anim}\n")
        
        # Remove any leading text before imports
        lines = code.split('\n')
        cleaned_lines = []
        found_import = False
        
        for line in lines:
            if not found_import:
                if line.strip().startswith('from manim') or line.strip().startswith('import'):
                    found_import = True
                    cleaned_lines.append(line)
                elif line.strip() and not line.strip().startswith('#'):
                    # Skip non-import, non-comment lines before first import
                    continue
                else:
                    # Keep empty lines and comments
                    if found_import or line.strip().startswith('#') or not line.strip():
                        cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        code = '\n'.join(cleaned_lines)
        
        # Ensure required imports
        if "from manim import *" not in code:
            code = "from manim import *\nimport numpy as np\n\n" + code
        
        # Basic validation
        required_elements = ["class", "Scene", "def construct"]
        for element in required_elements:
            if element not in code:
                raise ValueError(f"Generated code missing required element: {element}")
        
        return code.strip()
    
    def _create_fallback_code(self, content: Dict[str, Any], topic: str) -> str:
        """Create fallback Manim code if generation fails"""
        class_name = "".join(word.capitalize() for word in topic.split()[:3]) + "Explainer"
        class_name = "".join(c for c in class_name if c.isalnum())
        
        sections_code = []
        for i, section in enumerate(content.get("sections", [])):
            sections_code.append(f"""
        # Section {i+1}: {section['name']}
        section_title = Text("{section['name']}", font_size=36)
        self.play(Write(section_title))
        self.wait(1)
        self.play(section_title.animate.to_edge(UP))
        
        content_text = Text(
            "{section['content'][:100]}...",
            font_size=24
        ).scale(0.8)
        self.play(FadeIn(content_text))
        self.wait({section.get('duration', 30) - 2})
        self.play(FadeOut(content_text), FadeOut(section_title))
""")
        
        return f"""from manim import *
import numpy as np

class {class_name}(Scene):
    def construct(self):
        # Title Scene
        title = Text("{content.get('title', topic)}", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(title.animate.scale(0.7).to_edge(UP))
        
        # Introduction
        intro_text = Text(
            "Let's explore this topic together",
            font_size=32
        )
        self.play(FadeIn(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text), FadeOut(title))
        
{chr(10).join(sections_code)}
        
        # Conclusion
        conclusion = Text(
            "Thank you for learning with us!",
            font_size=36
        )
        self.play(Write(conclusion))
        self.wait(3)
"""