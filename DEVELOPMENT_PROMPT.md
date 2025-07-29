# Manim Explainer Video Agent - Development Prompt

## Project Overview
Develop an AI agent system that transforms user prompts into high-quality Manim explainer videos. The system should handle educational content requests and produce clear, visually engaging mathematical animations.

## Core Architecture

### Main Orchestrator Agent
**Purpose**: Central coordinator that manages the entire pipeline
**Responsibilities**:
- Parse and validate user requests
- Determine topic complexity and requirements
- Coordinate sub-agents in proper sequence
- Monitor progress and handle errors
- Deliver final video output

### Specialized Sub-Agents

#### 1. Content Research Agent
- Extract key concepts from the topic
- Research mathematical/scientific accuracy
- Structure content pedagogically
- Identify prerequisite knowledge
- Generate learning objectives

#### 2. Script Writing Agent
- Create engaging narration script
- Time scenes appropriately (typically 3-5 minutes)
- Ensure clarity for target audience
- Add hooks and transitions
- Structure: Introduction → Core Concepts → Examples → Applications → Summary

#### 3. Visual Design Agent
- Design mathematical visualizations
- Plan animation sequences
- Choose color schemes and styles
- Create visual metaphors
- Storyboard each scene

#### 4. Manim Code Generation Agent
- Translate designs into Manim Python code
- Implement mathematical objects and animations
- Handle text displays and equations
- Create smooth transitions
- Optimize rendering performance

#### 5. Rendering Agent
- Execute Manim code safely
- Handle dependencies and environment
- Monitor rendering progress
- Manage output formats and quality

#### 6. Quality Assurance Agent
- Verify mathematical accuracy
- Check visual clarity and pacing
- Ensure educational effectiveness
- Suggest improvements
- Validate against original request

## Implementation Strategy

### Phase 1: Foundation
1. Set up project structure with modular agent design
2. Implement basic orchestrator with message passing
3. Create simple Manim templates for common concepts

### Phase 2: Core Agents
1. Develop content research agent with knowledge retrieval
2. Build script generation with timing controls
3. Create visual design system with style guidelines

### Phase 3: Manim Integration
1. Implement code generation for basic animations
2. Add mathematical object library
3. Create rendering pipeline with error handling

### Phase 4: Enhancement
1. Add multi-concept support
2. Implement adaptive difficulty levels
3. Create feedback loop for improvements

## Technical Requirements

### Dependencies
- Python 3.9+
- Manim Community Edition
- LLM integration (for agent intelligence)
- Video processing libraries
- Mathematical computation libraries (NumPy, SymPy)

### Agent Communication
- JSON-based message protocol
- Asynchronous task handling
- Error propagation and recovery
- Progress tracking

### Output Specifications
- Default: 1080p MP4 video
- Frame rate: 30fps
- Audio: Optional narration track
- Duration: 2-10 minutes based on complexity

## Example Usage

```python
# User request
request = "Explain the Taylor series with visual examples"

# System response
video = ManimExplainerAgent.create_video(request)
# Produces: taylor_series_explained.mp4
```

## Success Criteria
1. Accurate mathematical content
2. Clear, engaging visualizations
3. Appropriate pacing and difficulty
4. Consistent visual style
5. Error-free rendering
6. Modular, extensible architecture