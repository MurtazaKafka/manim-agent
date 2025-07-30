"""
Dynamic quality standards for educational content generation
Adapts requirements based on requested video duration
"""

def get_quality_standards(duration_minutes: int) -> dict:
    """Get quality standards appropriate for video duration"""
    
    if duration_minutes <= 1:
        return {
            "min_duration": 50,  # Allow slightly under 1 minute
            "min_sections": 2,
            "min_animations_per_section": 1,  # Reduced for realistic 1-minute videos
            "min_total_animations": 3,  # At least 3 animations for 1 minute
            "hook_duration": (5, 10),
            "section_duration": (20, 30),
            "summary_duration": (5, 10),
            "transition_time": 1
        }
    elif duration_minutes <= 3:
        return {
            "min_duration": duration_minutes * 55,  # Allow 5 seconds variance
            "min_sections": 3,
            "min_animations_per_section": 3,
            "min_total_animations": 10,
            "hook_duration": (10, 15),
            "section_duration": (30, 45),
            "summary_duration": (10, 20),
            "transition_time": 1.5
        }
    elif duration_minutes <= 5:
        return {
            "min_duration": duration_minutes * 55,
            "min_sections": 4,
            "min_animations_per_section": 4,
            "min_total_animations": 20,
            "hook_duration": (15, 20),
            "section_duration": (45, 60),
            "summary_duration": (20, 30),
            "transition_time": 2
        }
    elif duration_minutes <= 10:
        return {
            "min_duration": duration_minutes * 55,
            "min_sections": 6,
            "min_animations_per_section": 5,
            "min_total_animations": 35,
            "hook_duration": (20, 30),
            "section_duration": (60, 90),
            "summary_duration": (30, 45),
            "transition_time": 2.5
        }
    else:  # 10+ minutes
        return {
            "min_duration": duration_minutes * 55,
            "min_sections": 8,
            "min_animations_per_section": 6,
            "min_total_animations": 50,
            "hook_duration": (30, 45),
            "section_duration": (90, 120),
            "summary_duration": (45, 60),
            "transition_time": 3
        }

# Default values for backward compatibility
default_standards = get_quality_standards(3)
MIN_VIDEO_DURATION = default_standards["min_duration"]
MIN_SECTIONS = default_standards["min_sections"]
MIN_ANIMATIONS_PER_SECTION = default_standards["min_animations_per_section"]
MIN_TOTAL_ANIMATIONS = default_standards["min_total_animations"]
CONTENT_REQUIREMENTS = {
    "hook_duration": default_standards["hook_duration"],
    "section_duration": default_standards["section_duration"],
    "summary_duration": default_standards["summary_duration"],
    "transition_time": default_standards["transition_time"]
}

# Visual complexity standards
def get_visual_complexity(duration_minutes: int) -> dict:
    """Get visual complexity requirements for duration"""
    
    if duration_minutes <= 1:
        return {
            "color_palette": 3,  # Maximum colors
            "simultaneous_objects": 3,  # Max objects on screen
            "animation_complexity": "simple",  # Simple transforms only
            "camera_movements": "minimal",  # Minimal camera work
            "text_overlays": "essential"  # Only essential text
        }
    elif duration_minutes <= 3:
        return {
            "color_palette": 5,
            "simultaneous_objects": 5,
            "animation_complexity": "moderate",
            "camera_movements": "occasional",
            "text_overlays": "supportive"
        }
    elif duration_minutes <= 5:
        return {
            "color_palette": 7,
            "simultaneous_objects": 7,
            "animation_complexity": "rich",
            "camera_movements": "strategic",
            "text_overlays": "comprehensive"
        }
    else:  # 5+ minutes
        return {
            "color_palette": 10,
            "simultaneous_objects": 10,
            "animation_complexity": "advanced",
            "camera_movements": "cinematic",
            "text_overlays": "layered"
        }

# Content depth standards
def get_content_depth(duration_minutes: int) -> dict:
    """Get content depth requirements for duration"""
    
    if duration_minutes <= 1:
        return {
            "explanation_depth": "core concept only",
            "examples_required": 1,
            "mathematical_rigor": "intuitive",
            "prerequisite_coverage": "assumed",
            "practice_problems": 0
        }
    elif duration_minutes <= 3:
        return {
            "explanation_depth": "concept with context",
            "examples_required": 2,
            "mathematical_rigor": "balanced",
            "prerequisite_coverage": "brief mention",
            "practice_problems": 1
        }
    elif duration_minutes <= 5:
        return {
            "explanation_depth": "comprehensive understanding",
            "examples_required": 3,
            "mathematical_rigor": "thorough",
            "prerequisite_coverage": "quick review",
            "practice_problems": 2
        }
    else:  # 5+ minutes
        return {
            "explanation_depth": "deep mastery",
            "examples_required": 5,
            "mathematical_rigor": "rigorous",
            "prerequisite_coverage": "detailed foundation",
            "practice_problems": 3
        }

# Validation functions
def validate_content_quality(content: dict, duration_minutes: int) -> tuple[bool, list[str]]:
    """Validate content meets quality standards for duration"""
    standards = get_quality_standards(duration_minutes)
    issues = []
    
    # Check duration
    total_duration = content.get("total_duration", 0)
    if total_duration < standards["min_duration"]:
        issues.append(f"Duration {total_duration}s is below minimum {standards['min_duration']}s")
    
    # Check sections
    sections = content.get("sections", [])
    if len(sections) < standards["min_sections"]:
        issues.append(f"Only {len(sections)} sections, need at least {standards['min_sections']}")
    
    # Note: Animation checks moved to visual validation where they belong
    
    return len(issues) == 0, issues

def validate_visual_quality(visual_design: dict, duration_minutes: int) -> tuple[bool, list[str]]:
    """Validate visual design meets standards for duration"""
    complexity = get_visual_complexity(duration_minutes)
    standards = get_quality_standards(duration_minutes)
    issues = []
    
    # Check scene count
    scenes = visual_design.get("scenes", [])
    if len(scenes) < standards["min_sections"]:
        issues.append(f"Only {len(scenes)} scenes, need at least {standards['min_sections']}")
    
    # Check animation density
    for i, scene in enumerate(scenes):
        animations = scene.get("animations", [])
        if len(animations) < standards["min_animations_per_section"]:
            issues.append(f"Scene {i+1} has only {len(animations)} animations, need at least {standards['min_animations_per_section']}")
    
    return len(issues) == 0, issues

# Recommendation functions
def get_pacing_recommendations(duration_minutes: int) -> dict:
    """Get pacing recommendations for duration"""
    
    if duration_minutes <= 1:
        return {
            "intro_pace": "immediate",
            "concept_introduction": "direct",
            "example_timing": "quick",
            "transition_style": "cut",
            "summary_approach": "bullet points"
        }
    elif duration_minutes <= 3:
        return {
            "intro_pace": "engaging",
            "concept_introduction": "gradual",
            "example_timing": "clear",
            "transition_style": "smooth",
            "summary_approach": "recap"
        }
    else:  # 3+ minutes
        return {
            "intro_pace": "thoughtful",
            "concept_introduction": "layered",
            "example_timing": "thorough",
            "transition_style": "thematic",
            "summary_approach": "synthesis"
        }

# Export convenience function
def get_all_standards(duration_minutes: int) -> dict:
    """Get all quality standards for a given duration"""
    return {
        "quality": get_quality_standards(duration_minutes),
        "visual": get_visual_complexity(duration_minutes),
        "depth": get_content_depth(duration_minutes),
        "pacing": get_pacing_recommendations(duration_minutes)
    }