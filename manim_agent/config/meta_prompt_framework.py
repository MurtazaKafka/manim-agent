"""
Dynamic Meta-Prompt Framework for Educational Videos
Adapts to any requested video duration
"""

# Dynamic prompting based on video length
def get_chain_of_thought_prompt(duration_minutes: int) -> str:
    """Get appropriate chain of thought prompt for duration"""
    if duration_minutes <= 2:
        return """
Think through the educational approach:
1. What's the ONE key concept to convey?
2. What's the simplest explanation?
3. What visual will make it click?
"""
    elif duration_minutes <= 5:
        return """
Think step-by-step through the educational journey:
1. What misconceptions should we address?
2. How can we build understanding incrementally?
3. What examples best demonstrate the concept?
"""
    else:
        return """
Think step-by-step through the comprehensive educational journey:
1. What misconceptions do learners typically have?
2. What foundational knowledge is required?
3. How can we build understanding incrementally?
4. What real-world applications demonstrate the concept?
5. What exercises reinforce understanding?
"""

# Default prompts for backward compatibility
CHAIN_OF_THOUGHT_PROMPT = get_chain_of_thought_prompt(5)

def get_persona_prompt(duration_minutes: int) -> str:
    """Get appropriate persona for duration"""
    if duration_minutes <= 2:
        return """
You are a skilled educator creating a focused explanation.
Your audience expects:
- Clear, direct explanations
- Essential visuals only
- Quick understanding
"""
    elif duration_minutes <= 5:
        return """
You are an engaging educator creating clear explanations.
Your audience expects:
- Well-paced explanations
- Helpful visualizations
- Practical understanding
"""
    else:
        return """
You are creating an in-depth educational video.
Your audience expects:
- Detailed explanations with visual insights
- Building intuition before formalism
- Connecting concepts to applications
- Thoughtful pacing for understanding
"""

PERSONA_PROMPT = get_persona_prompt(5)

def get_tree_of_thoughts_prompt(duration_minutes: int) -> str:
    """Get appropriate exploration depth for duration"""
    if duration_minutes <= 2:
        return """
For the concept, focus on:
└── Core Path: The essential explanation with one clear visual
"""
    elif duration_minutes <= 5:
        return """
For each concept, explore:
├── Intuitive Path: Visual metaphors and examples
└── Applied Path: Practical uses
"""
    else:
        return """
For each concept, explore multiple explanation paths:
├── Intuitive Path: Visual metaphors and everyday examples
├── Mathematical Path: Rigorous derivations and proofs
├── Historical Path: How the concept was discovered
├── Applied Path: Real-world uses and implementations
└── Connections Path: Links to other concepts
"""

TREE_OF_THOUGHTS_PROMPT = get_tree_of_thoughts_prompt(5)

# Dynamic requirements that scale with duration
def get_minimum_requirements(duration_minutes: int) -> dict:
    """Get scaled requirements for video duration"""
    if duration_minutes <= 1:
        return {
            "duration": 60,
            "scenes": 2,
            "animations": 3,  # Reduced for realistic 1-minute videos
            "concepts": 1,
            "examples": 1,
            "visuals": 3
        }
    elif duration_minutes <= 3:
        return {
            "duration": duration_minutes * 60,
            "scenes": 3,
            "animations": 15,
            "concepts": 2,
            "examples": 2,
            "visuals": 10
        }
    elif duration_minutes <= 5:
        return {
            "duration": duration_minutes * 60,
            "scenes": 5,
            "animations": 30,
            "concepts": 3,
            "examples": 3,
            "visuals": 20
        }
    elif duration_minutes <= 10:
        return {
            "duration": duration_minutes * 60,
            "scenes": 8,
            "animations": 50,
            "concepts": 5,
            "examples": 5,
            "visuals": 35
        }
    else:
        return {
            "duration": duration_minutes * 60,
            "scenes": 10,
            "animations": 70,
            "concepts": 8,
            "examples": 8,
            "visuals": 50
        }

# Default for backward compatibility
MINIMUM_REQUIREMENTS = get_minimum_requirements(10)

# Quality enforcement that scales with duration
QUALITY_ENFORCEMENT_PROMPTS = {
    "depth_check": """
    Evaluate content depth appropriate to duration:
    - 1 minute: Core concept clearly explained
    - 3 minutes: Concept with examples
    - 5 minutes: Multiple perspectives
    - 10+ minutes: Comprehensive coverage
    
    Match depth to available time.
    """,
    
    "engagement_check": """
    Ensure engagement matches video length:
    - Short videos: Every second counts
    - Medium videos: Steady pacing
    - Long videos: Varied pacing with breaks
    """,
    
    "visual_check": """
    Visual richness appropriate to duration:
    - Short: Essential visuals only
    - Medium: Clear supporting visuals
    - Long: Rich visual storytelling
    """
}

# Simplified exemplar structures
EXEMPLAR_STRUCTURES = {
    "derivative": """
    1. Hook: Rate of change in real life
    2. Visual: Position graph animation
    3. Core: Limiting process
    4. Application: Real use case
    """,
    
    "matrix": """
    1. Hook: Transformations we see daily
    2. Visual: Grid transformations
    3. Core: Matrix operations
    4. Application: Computer graphics
    """,
    
    "probability": """
    1. Hook: Counterintuitive example
    2. Visual: Probability trees
    3. Core: Mathematical foundation
    4. Application: Real decisions
    """
}

# Dynamic meta-prompt generator
def get_meta_prompt_template(duration_minutes: int) -> str:
    """Generate appropriate meta-prompt for duration"""
    if duration_minutes <= 2:
        return f"""
## GOAL
Create a {duration_minutes}-minute focused explanation.

## REQUIREMENTS
1. **Hook** (5-10 seconds)
   - Quick attention grabber
   
2. **Core Concept** ({duration_minutes * 40} seconds)
   - Essential explanation
   - One clear visual
   
3. **Summary** (10 seconds)
   - Key takeaway

## VISUAL REQUIREMENTS
- {duration_minutes * 5} essential animations
- Clear and simple
- Direct communication
"""
    else:
        sections = max(3, min(duration_minutes, 10))
        return f"""
## GOAL
Create a {duration_minutes}-minute educational video.

## CONTENT STRUCTURE
1. **Hook** ({min(20, duration_minutes * 10)} seconds)
   - Engaging opening
   
2. **Main Content** ({sections-2} sections)
   - Clear explanations
   - Appropriate depth
   
3. **Summary** ({min(30, duration_minutes * 10)} seconds)
   - Key insights

## VISUAL REQUIREMENTS
- {duration_minutes * 8} animations
- Appropriate complexity
- Clear storytelling
"""

# Export dynamic meta-prompt
META_PROMPT_TEMPLATE = get_meta_prompt_template(10)

# Refinement prompts for iterative improvement
REFINEMENT_PROMPTS = {
    "expand": """
    Expand the content with:
    - More detailed explanations
    - Additional examples
    - Deeper mathematical insights
    """,
    
    "deepen": """
    Deepen the content by:
    - Adding prerequisite explanations
    - Including derivations
    - Showing multiple perspectives
    """,
    
    "visualize": """
    Enhance visualizations with:
    - More animation variety
    - Smoother transitions
    - Clearer visual metaphors
    - Better color usage
    """
}