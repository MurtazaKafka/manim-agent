# CLAUDE.md - Persistent Instructions for Manim Agent Development

## Algorithm Simulation Protocol

**IMPORTANT**: Before taking any actions or writing code, you MUST first mentally simulate the algorithm and workflow. This ensures thoughtful, coordinated development.

### Simulation Steps:

1. **Pause and Visualize**: When given a task, first close your eyes (metaphorically) and trace through the entire process
2. **Identify Components**: List all agents/modules that will be involved
3. **Trace Data Flow**: Follow how information moves between components
4. **Anticipate Issues**: Consider potential failures or edge cases
5. **Plan Actions**: Only then proceed with implementation

### Example Simulation:

When asked to "implement Taylor series visualization":
1. First simulate: User input → Orchestrator → Content Agent (fetches formula) → Visual Agent (plans animations) → Code Agent (generates Manim) → Renderer
2. Consider: What if formula is too complex? How to handle edge cases?
3. Then act: Write the actual implementation

## Sub-Agent Instructions

All sub-agents should follow this same protocol:

```python
# Before any agent action:
def before_action(self, task):
    # 1. Simulate the task mentally
    # 2. Identify inputs/outputs
    # 3. Consider dependencies
    # 4. Plan approach
    # 5. Then execute
    pass
```

## Project-Specific Guidelines

### Manim Code Generation
- Always simulate the animation in your mind before generating code
- Visualize how mathematical objects will move and transform
- Consider timing and pacing before writing Scene classes

### Content Research
- Simulate how a teacher would explain the concept
- Think through logical progression before structuring content
- Imagine student questions and confusion points

### Visual Design
- Mentally preview the entire animation sequence
- Simulate color changes, movements, and transitions
- Consider visual hierarchy and focus points

## Development Commands

### Testing and Validation
- Run tests: `python -m pytest tests/`
- Type checking: `mypy manim_agent/`
- Linting: `ruff check .`
- Format: `ruff format .`

### Manim Rendering
- Preview: `manim -pql scene.py SceneName`
- High quality: `manim -pqh scene.py SceneName`
- With debugging: `manim -pql --save_sections scene.py SceneName`

## Remember
**Always simulate before you stimulate (action)!** This mental rehearsal prevents errors and ensures coordinated development across all agents.