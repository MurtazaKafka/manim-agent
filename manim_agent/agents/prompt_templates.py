"""
Dynamic prompt templates that adapt to requested video duration
"""
from typing import Dict, Any

class DynamicPromptGenerator:
    """Generate prompts that dynamically adapt to video duration"""
    
    @staticmethod
    def get_duration_config(duration_minutes: int) -> Dict[str, Any]:
        """Get configuration based on video duration"""
        
        if duration_minutes <= 1:
            return {
                "style": "concise and focused",
                "sections": 2,
                "section_range": "2",
                "section_duration": "20-30",
                "hook_duration": "5-10",
                "summary_duration": "10",
                "animations_per_minute": 3,  # Reduced for realistic 1-minute videos
                "complexity": "simple",
                "detail_level": "essential points only",
                "pacing": "quick and direct"
            }
        elif duration_minutes <= 3:
            return {
                "style": "clear and engaging",
                "sections": 3,
                "section_range": "3-4",
                "section_duration": "30-45",
                "hook_duration": "10-15",
                "summary_duration": "15-20",
                "animations_per_minute": 8,
                "complexity": "moderate",
                "detail_level": "main concepts with examples",
                "pacing": "steady and clear"
            }
        elif duration_minutes <= 5:
            return {
                "style": "comprehensive and educational",
                "sections": 4,
                "section_range": "4-5",
                "section_duration": "45-60",
                "hook_duration": "15-20",
                "summary_duration": "20-30",
                "animations_per_minute": 10,
                "complexity": "detailed",
                "detail_level": "thorough explanations with multiple examples",
                "pacing": "measured with time for understanding"
            }
        elif duration_minutes <= 10:
            return {
                "style": "in-depth and exploratory",
                "sections": 6,
                "section_range": "5-7",
                "section_duration": "60-90",
                "hook_duration": "20-30",
                "summary_duration": "30-45",
                "animations_per_minute": 12,
                "complexity": "comprehensive",
                "detail_level": "deep dive with nuanced explanations",
                "pacing": "deliberate with pauses for reflection"
            }
        else:  # 10+ minutes
            return {
                "style": "masterclass-level depth",
                "sections": 8,
                "section_range": "7-10",
                "section_duration": "90-120",
                "hook_duration": "30-45",
                "summary_duration": "45-60",
                "animations_per_minute": 15,
                "complexity": "expert",
                "detail_level": "exhaustive coverage with advanced topics",
                "pacing": "varied with multiple arcs"
            }
    
    @staticmethod
    def get_content_system_prompt(duration_minutes: int) -> str:
        """Generate dynamic system prompt for content agent"""
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        
        return f"""You are an educational content creator specializing in {config['style']} explanations.
        
        For this {duration_minutes}-minute video, you should:
        - Create {config['detail_level']}
        - Use {config['pacing']} pacing
        - Include {config['sections']} main sections
        - Keep complexity {config['complexity']}
        
        Your content should be perfectly tailored for a {duration_minutes}-minute video."""
    
    @staticmethod
    def get_content_requirements(duration_minutes: int) -> str:
        """Generate dynamic content requirements"""
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        total_seconds = duration_minutes * 60
        
        return f"""REQUIREMENTS for {duration_minutes}-minute video:
        - Total duration: {total_seconds} seconds
        - Number of sections: {config['section_range']}
        - Section duration: {config['section_duration']} seconds each
        - Hook duration: {config['hook_duration']} seconds
        - Summary duration: {config['summary_duration']} seconds
        - Style: {config['style']}
        - Pacing: {config['pacing']}"""
    
    @staticmethod
    def get_visual_requirements(duration_minutes: int) -> str:
        """Generate dynamic visual design requirements"""
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        total_animations = duration_minutes * config['animations_per_minute']
        
        return f"""VISUAL REQUIREMENTS for {duration_minutes}-minute video:
        - Total animations: {total_animations} (approximately {config['animations_per_minute']} per minute)
        - Animation complexity: {config['complexity']}
        - Hook animation: {config['hook_duration']} seconds
        - Transitions: {'Simple' if duration_minutes <= 3 else 'Smooth and varied'}
        - Visual style: {'Clean and direct' if duration_minutes <= 2 else 'Rich and engaging'}"""
    
    @staticmethod
    def get_manim_code_requirements(duration_minutes: int) -> str:
        """Generate dynamic Manim code requirements"""
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        
        return f"""CODE REQUIREMENTS for {duration_minutes}-minute video:
        1. Video duration: {duration_minutes} minute{'s' if duration_minutes > 1 else ''} ({duration_minutes * 60} seconds)
        2. Hook: {config['hook_duration']} seconds of engaging introduction
        3. Main content: {config['sections']} sections, {config['section_duration']} seconds each
        4. Animations: At least {duration_minutes * config['animations_per_minute']} distinct animations
        5. Complexity: {config['complexity']} - {'minimize complexity' if duration_minutes <= 2 else 'rich animations'}
        6. Pacing: Use self.wait() to achieve {config['pacing']} pacing
        7. Summary: {config['summary_duration']} seconds to reinforce key points"""
    
    @staticmethod
    def get_scene_structure(duration_minutes: int) -> str:
        """Generate dynamic scene structure"""
        config = DynamicPromptGenerator.get_duration_config(duration_minutes)
        
        structure = f"""
class [TopicName]Explainer(Scene):
    def construct(self):
        # Setup ({duration_minutes}-minute video)
        self.camera.background_color = "#1a1a1a"
        
        # Hook ({config['hook_duration']} seconds)
        self.play_hook()
        """
        
        # Add main sections
        for i in range(config['sections']):
            structure += f"""
        
        # Section {i+1} ({config['section_duration']} seconds)
        self.section_{i+1}()"""
        
        structure += f"""
        
        # Summary ({config['summary_duration']} seconds)
        self.play_summary()
"""
        return structure