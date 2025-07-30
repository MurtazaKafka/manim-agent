from ..core.base_agent import BaseAgent, AgentMessage
from ..core.llm_service import LLMService
from .prompt_templates import DynamicPromptGenerator
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class VisualDesignAgent(BaseAgent):
    """Agent responsible for designing visual elements and animation sequences"""
    
    def __init__(self, name: str, llm_service: LLMService):
        super().__init__(name)
        self.llm = llm_service
        
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process visual design requests"""
        # First simulate (following CLAUDE.md)
        simulation = self.simulate_algorithm("Design visual elements")
        
        if message.action == "design" or message.action == "design_visuals":
            content = message.payload.get("content", {})
            topic = message.payload.get("topic", "")
            context = message.payload.get("context", "")
            full_prompt = message.payload.get("full_prompt", topic)
            requirements = message.payload.get("requirements", {})
            
            # Generate visual design using LLM with context
            visual_design = await self._generate_visual_design(content, topic, context, full_prompt, requirements)
            
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                action="design_ready",
                payload={"design": visual_design}
            )
        
        return message
    
    async def _generate_visual_design(self, content: Dict[str, Any], topic: str, context: str = "", full_prompt: str = "", requirements: Dict = None) -> Dict[str, Any]:
        """Generate visual design plan using LLM"""
        # Get duration from requirements
        duration_minutes = requirements.get("duration", 180) // 60 if requirements else 3
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        
        system_prompt = """You are a visual designer creating 3Blue1Brown-quality educational animations.
        
        Your animations are characterized by:
        - SMOOTH, BEAUTIFUL TRANSITIONS that guide the eye
        - CLEAR VISUAL METAPHORS that make abstract concepts tangible
        - THOUGHTFUL COLOR CODING to highlight relationships
        - PROGRESSIVE DISCLOSURE - build complexity gradually
        - SYNCHRONIZED motion that tells a story
        
        Key principles:
        1. Every animation should TEACH, not just display
        2. Use motion to show RELATIONSHIPS and TRANSFORMATIONS
        3. Build from CONCRETE examples to ABSTRACT concepts
        4. Create "AHA!" moments through clever visual reveals
        5. Maintain visual continuity - objects should transform, not just appear/disappear
        
        Manim capabilities you should leverage:
        - Smooth morphing between shapes and equations
        - Camera movements to focus attention
        - Color gradients and highlights
        - Synchronized multi-object animations
        - Graph animations with moving points
        - Text that transforms into mathematical objects"""
        
        # Prepare content summary for the LLM
        sections_summary = []
        for section in content.get("sections", []):
            sections_summary.append({
                "name": section["name"],
                "content": section["content"],
                "duration": section["duration"],
                "visual_elements": section.get("visual_elements", "")
            })
        
        # Include context if available
        context_text = f"\n{context}\n" if context else ""
        
        prompt = f"""Design a complete visual animation plan for this request:

{full_prompt if full_prompt else topic}
{context_text}
        Content Structure:
        Title: {content.get('title', topic)}
        Sections: {len(content.get('sections', []))} sections
        Total Duration: {content.get('total_duration', 180)} seconds
        Key Concepts: {', '.join(content.get('key_concepts', []))}
        
        Section Details:
        {sections_summary}
        
        If this is a refinement request, adjust the visual design accordingly to address the user's feedback.
        
        Create a DETAILED 3Blue1Brown-style visual design:
        
        For EACH SCENE (one per content section):
        1. OPENING: How does the scene start? What's on screen?
        2. MAIN ANIMATIONS: Step-by-step animation sequence
           - List each animation in order (minimum 3-4 per scene)
           - Specify exact timing and smooth transitions
           - Include mathematical transformations
        3. KEY VISUALS: Specific Manim objects with details
           - MathTex equations with LaTeX formatting
           - Axes with ranges and labels
           - Geometric shapes with exact properties
           - Text overlays with positioning
        4. TRANSITIONS: Smooth morphing to next scene
        
        MANDATORY VISUAL ELEMENTS:
        - Opening hook animation ({config['hook_duration']} seconds)
        - {config['detail_level'].capitalize()}
        - Approximately {duration_minutes * config['animations_per_minute']} total animations
        - {'Essential visuals only' if duration_minutes <= 1 else 'Rich visual metaphors'}
        - {'Simple color scheme' if duration_minutes <= 2 else 'Strategic color coding'}
        - {'Minimal camera movement' if duration_minutes <= 1 else 'Smooth camera movements for focus'}
        - Summary visualization ({config['summary_duration']} seconds)
        
        Example for Stochastic Gradient Descent:
        - Start with a hiker on a foggy mountain (visual metaphor)
        - Morph to 3D loss surface
        - Animate gradient vectors at different points
        - Show batch vs full gradient comparison
        - Animate the optimization path
        - Display learning rate effects
        - Show convergence behavior
        
        REMEMBER: Every animation should TEACH something!"""
        
        schema = {
            "scenes": [
                {
                    "scene_number": "number",
                    "description": "string - what happens in this scene",
                    "duration": "number - seconds",
                    "manim_objects": [
                        {
                            "type": "string - e.g., Text, MathTex, Circle, Axes, etc.",
                            "name": "string - identifier for the object",
                            "properties": "object - specific properties like text, formula, size, position",
                            "initial_state": "string - how it appears initially"
                        }
                    ],
                    "animations": [
                        {
                            "type": "string - e.g., Write, Create, Transform, FadeIn, etc.",
                            "target": "string - which object(s) to animate",
                            "duration": "number - animation duration in seconds",
                            "properties": "object - animation-specific properties"
                        }
                    ],
                    "camera_movements": "string - any camera changes"
                }
            ],
            "color_scheme": {
                "primary": "string - main color hex",
                "secondary": "string - secondary color hex",
                "accent": "string - accent color hex",
                "background": "string - background color hex",
                "text": "string - text color hex",
                "mathematical": "string - color for math objects"
            },
            "style_guidelines": {
                "font_size": "object - sizes for different text types",
                "spacing": "string - general spacing approach",
                "transitions": "string - transition style between scenes"
            },
            "special_effects": ["list of special visual effects or techniques"]
        }
        
        try:
            # For Claude Sonnet 4, use XML approach then convert to JSON
            if hasattr(self.llm, 'model') and 'sonnet-4' in getattr(self.llm, 'model', ''):
                # Use XML approach for Sonnet 4 to avoid JSON issues
                xml_prompt = f"""{prompt}

Provide your response in this XML format:
<visual_design>
    <title>Title here</title>
    <scenes>
        <scene>
            <name>Scene name</name>
            <description>What happens</description>
            <duration>30</duration>
            <animations>Write, FadeIn, Transform, Create, FadeOut</animations>
        </scene>
        <!-- Add more scenes as needed -->
    </scenes>
    <color_scheme>
        <primary>#1E1E1E</primary>
        <secondary>#FFFFFE</secondary>
        <accent>#58C4DD</accent>
        <background>#000000</background>
        <text>#FFFFFF</text>
        <mathematical>#E11D48</mathematical>
    </color_scheme>
    <animation_style>smooth</animation_style>
    <special_effects>3D camera movements, smooth morphing</special_effects>
</visual_design>"""
                
                try:
                    # Get XML response
                    xml_response = await self.llm.generate(
                        xml_prompt,
                        system_prompt + "\n\nRespond with only the XML structure, no other text.",
                        temperature=0.7
                    )
                    
                    # Convert XML to JSON
                    visual_design = self._convert_xml_to_json(xml_response)
                except Exception as e:
                    logger.warning(f"XML approach failed, falling back to JSON: {e}")
                    # Fallback to JSON approach
                    simple_prompt = f"{prompt}\n\nProvide your response as a JSON object with these fields: title, scenes (array), color_scheme, animation_style, special_effects."
                    visual_design = await self.llm.generate_json_with_retry(
                        simple_prompt,
                        system_prompt,
                        temperature=0.7,
                        max_retries=3
                    )
            else:
                visual_design = await self.llm.generate_json_with_retry(
                    prompt,
                    system_prompt,
                    schema=schema,
                    temperature=0.8,  # Slightly higher for creativity
                    max_retries=3
                )
            
            # Validate and enhance the design
            visual_design = self._validate_and_enhance_design(visual_design, content)
            
            # Double-check critical fields exist
            if 'scenes' not in visual_design:
                visual_design['scenes'] = []
            
            # Ensure each scene has required fields
            for i, scene in enumerate(visual_design.get('scenes', [])):
                if 'description' not in scene:
                    scene['description'] = f"Scene {i+1}"
                if 'animations' not in scene:
                    scene['animations'] = []
            
            logger.info(f"Generated visual design with {len(visual_design['scenes'])} scenes")
            return visual_design
            
        except Exception as e:
            logger.error(f"Error generating visual design: {e}")
            # NO FALLBACKS - We need real AI-generated designs!
            raise Exception(f"Failed to generate visual design after retries: {str(e)}")
    
    def _convert_xml_to_json(self, xml_response: str) -> Dict[str, Any]:
        """Convert XML response to JSON format"""
        import re
        
        # Extract visual design content
        design = {}
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', xml_response, re.DOTALL)
        design['title'] = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract scenes
        scenes = []
        scene_matches = re.findall(r'<scene>(.*?)</scene>', xml_response, re.DOTALL)
        for i, scene_xml in enumerate(scene_matches):
            scene: Dict[str, Any] = {'scene_number': i + 1}
            
            # Extract scene fields
            name_match = re.search(r'<name>(.*?)</name>', scene_xml)
            scene['name'] = name_match.group(1).strip() if name_match else "Scene"
            
            desc_match = re.search(r'<description>(.*?)</description>', scene_xml)
            scene['description'] = desc_match.group(1).strip() if desc_match else "Scene description"
            
            duration_match = re.search(r'<duration>(.*?)</duration>', scene_xml)
            scene['duration'] = int(duration_match.group(1).strip()) if duration_match else 30
            
            # Extract animations with more detail
            anim_match = re.search(r'<animations>(.*?)</animations>', scene_xml)
            if anim_match:
                animations = [a.strip() for a in anim_match.group(1).split(',') if a.strip()]
                scene['animations'] = []
                for anim in animations:
                    # Create proper animation object with duration
                    animation_obj = {
                        "type": anim,
                        "target": "object",
                        "duration": 2.0,  # Default duration
                        "properties": {}
                    }
                    scene['animations'].append(animation_obj)
            else:
                scene['animations'] = []
            
            # Also add manim_objects for proper scene structure
            scene['manim_objects'] = [
                {
                    "type": "Text",
                    "name": "object",
                    "properties": {"text": scene.get('name', 'Scene')},
                    "initial_state": "centered"
                }
            ]
            
            scenes.append(scene)
        
        design['scenes'] = scenes
        
        # Extract color scheme
        color_scheme = {}
        primary_match = re.search(r'<primary>(.*?)</primary>', xml_response)
        color_scheme['primary'] = primary_match.group(1).strip() if primary_match else "#1E1E1E"
        
        secondary_match = re.search(r'<secondary>(.*?)</secondary>', xml_response)
        color_scheme['secondary'] = secondary_match.group(1).strip() if secondary_match else "#FFFFFE"
        
        accent_match = re.search(r'<accent>(.*?)</accent>', xml_response)
        color_scheme['accent'] = accent_match.group(1).strip() if accent_match else "#58C4DD"
        
        background_match = re.search(r'<background>(.*?)</background>', xml_response)
        color_scheme['background'] = background_match.group(1).strip() if background_match else "#000000"
        
        text_match = re.search(r'<text>(.*?)</text>', xml_response)
        color_scheme['text'] = text_match.group(1).strip() if text_match else "#FFFFFF"
        
        mathematical_match = re.search(r'<mathematical>(.*?)</mathematical>', xml_response)
        color_scheme['mathematical'] = mathematical_match.group(1).strip() if mathematical_match else "#E11D48"
        
        design['color_scheme'] = color_scheme
        
        # Extract animation style
        style_match = re.search(r'<animation_style>(.*?)</animation_style>', xml_response)
        design['animation_style'] = style_match.group(1).strip() if style_match else "smooth"
        
        # Extract special effects
        effects_match = re.search(r'<special_effects>(.*?)</special_effects>', xml_response)
        if effects_match:
            effects = [e.strip() for e in effects_match.group(1).split(',')]
            design['special_effects'] = effects
        else:
            design['special_effects'] = []
        
        # Add style guidelines for completeness
        design['style_guidelines'] = {
            "font_size": {"title": 48, "heading": 36, "body": 24},
            "spacing": "balanced",
            "transitions": "smooth"
        }
        
        return design
    
    def _validate_and_enhance_design(self, design: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the visual design"""
        # Ensure all required fields exist
        if "scenes" not in design:
            design["scenes"] = []
        
        if "color_scheme" not in design:
            design["color_scheme"] = {
                "primary": "#3B82F6",
                "secondary": "#10B981", 
                "accent": "#F59E0B",
                "background": "#000000",
                "text": "#FFFFFF",
                "mathematical": "#E11D48"
            }
        
        # Ensure scene durations match content sections
        content_sections = content.get("sections", [])
        if len(design["scenes"]) < len(content_sections):
            # Add missing scenes
            for i in range(len(design["scenes"]), len(content_sections)):
                section = content_sections[i]
                design["scenes"].append({
                    "scene_number": i + 1,
                    "description": section["name"],
                    "duration": section["duration"],
                    "manim_objects": [],
                    "animations": []
                })
        
        return design
    
    def _create_fallback_design(self, content: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Create a basic fallback design"""
        scenes = []
        
        # Title scene
        scenes.append({
            "scene_number": 1,
            "description": "Title introduction",
            "duration": 5,
            "manim_objects": [
                {
                    "type": "Text",
                    "name": "title",
                    "properties": {"text": content.get("title", topic), "font_size": 48},
                    "initial_state": "centered"
                }
            ],
            "animations": [
                {
                    "type": "Write",
                    "target": "title",
                    "duration": 2,
                    "properties": {}
                }
            ]
        })
        
        # Content scenes
        for i, section in enumerate(content.get("sections", [])):
            scenes.append({
                "scene_number": i + 2,
                "description": section["name"],
                "duration": section["duration"],
                "manim_objects": [
                    {
                        "type": "Text",
                        "name": f"section_{i}_title",
                        "properties": {"text": section["name"], "font_size": 36},
                        "initial_state": "top"
                    },
                    {
                        "type": "Text", 
                        "name": f"section_{i}_content",
                        "properties": {"text": section["content"], "font_size": 24},
                        "initial_state": "center"
                    }
                ],
                "animations": [
                    {
                        "type": "FadeIn",
                        "target": f"section_{i}_title",
                        "duration": 1,
                        "properties": {}
                    },
                    {
                        "type": "Write",
                        "target": f"section_{i}_content",
                        "duration": 3,
                        "properties": {}
                    }
                ]
            })
        
        return {
            "scenes": scenes,
            "color_scheme": {
                "primary": "#3B82F6",
                "secondary": "#10B981",
                "accent": "#F59E0B", 
                "background": "#000000",
                "text": "#FFFFFF",
                "mathematical": "#E11D48"
            },
            "style_guidelines": {
                "font_size": {"title": 48, "heading": 36, "body": 24},
                "spacing": "balanced",
                "transitions": "smooth"
            },
            "special_effects": []
        }