# Manim Explainer Agent

An AI agent system that transforms user prompts into Manim explainer videos.

## Overview

This project implements a multi-agent system where specialized AI agents collaborate to:
1. Research educational content
2. Design visualizations
3. Generate Manim animation code
4. Produce explainer videos

## Architecture

- **Orchestrator Agent**: Coordinates the entire pipeline
- **Content Agent**: Researches and structures educational content
- **Visual Design Agent**: Plans animations and visual elements
- **Manim Code Agent**: Generates Python Manim code
- **Rendering Agent**: Executes code and produces videos
- **QA Agent**: Ensures quality and accuracy

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run example
python example_usage.py

# Render generated video
manim -pql generated_explain_the_taylor_series_wit.py
```

## Development Philosophy

Following CLAUDE.md protocol:
1. **Simulate Before Action**: Always mentally simulate the algorithm before implementing
2. **Modular Design**: Each agent has a specific responsibility
3. **Clear Communication**: JSON-based message passing between agents
4. **Error Resilience**: Graceful handling of edge cases

## Example Usage

```python
from manim_agent import ManimExplainerAgent

agent = ManimExplainerAgent()
manim_code = await agent.create_video("Explain the Taylor series")
```

## Project Structure

```
manim-agent/
├── manim_agent/
│   ├── core/          # Core infrastructure
│   ├── agents/        # Specialized agents
│   ├── templates/     # Manim templates
│   └── utils/         # Utilities
├── tests/             # Test suite
├── CLAUDE.md          # Development instructions
├── DEVELOPMENT_PROMPT.md  # Comprehensive prompt
└── example_usage.py   # Demo script
```