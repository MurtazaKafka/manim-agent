# Manim Explainer Agent 🎬

An AI-powered system that transforms any educational prompt into beautiful Manim animations. Simply describe what you want to explain, and the system generates complete, production-ready Manim code.

## 🌟 Features

- **Beautiful Web Interface**: Claude-inspired chat UI for easy interaction
- **Real-Time Progress**: Watch as AI agents work on your animation
- **Universal Topic Support**: Handles ANY mathematical, scientific, or educational topic
- **Multi-Agent Architecture**: Specialized AI agents collaborate to create optimal animations
- **Production-Ready Code**: Generates clean, well-structured Manim code
- **Intelligent Visual Design**: Automatically plans animations, color schemes, and transitions
- **Video Preview & Download**: Watch and download your animations instantly
- **LLM Flexibility**: Supports both OpenAI and Anthropic Claude

## 🏗️ Architecture

```
User Prompt → Orchestrator → Content Agent → Visual Design Agent → Code Generation Agent → Manim Code
```

- **Orchestrator**: Coordinates the entire pipeline
- **Content Agent**: Researches and structures educational content  
- **Visual Design Agent**: Plans animations, layouts, and visual flow
- **Manim Code Agent**: Generates executable Python Manim code

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MurtazaKafka/manim-agent.git
cd manim-agent

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
ANTHROPIC_API_KEY='your-anthropic-api-key'
# Optional: OPENAI_API_KEY='your-openai-api-key'
```

### Option 1: Web Interface (Recommended)

1. **Start the backend API server:**
```bash
python api_server.py
```

2. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm install  # First time only
npm run dev
```

3. **Open your browser to [http://localhost:3000](http://localhost:3000)**

4. **Start creating animations!** Just type your educational topic in the chat.

### Option 2: Command Line Usage

```python
from manim_agent import ManimExplainerAgent

# Create agent (defaults to OpenAI)
agent = ManimExplainerAgent()

# Generate animation code for ANY topic
manim_code = await agent.create_video("Explain how neural networks learn")

# Save and render
with open("neural_networks.py", "w") as f:
    f.write(manim_code)

# Render with Manim
# manim -pql neural_networks.py
```

### Example Topics

The system can handle any educational topic:

- "Explain the Fourier transform and how it decomposes signals"
- "Show how gradient descent optimization works"
- "Visualize quantum superposition"
- "Demonstrate binary search trees"
- "Explain the central limit theorem"
- "Show how RSA encryption works"
- "Visualize eigenvalues and eigenvectors"
- "Explain backpropagation in neural networks"
- "Show the relationship between e, pi, and i"
- "Demonstrate how quicksort works"

### Run Examples

```bash
# Run the example script
python example_usage.py

# This will generate a Manim file, then render it:
manim -pql generated_explain_the_fourier_transfor.py
```

## 📋 Advanced Usage

### Choose LLM Provider

```python
from manim_agent import ManimExplainerAgent
from manim_agent.core.llm_service import LLMProvider

# Use OpenAI GPT-4
agent = ManimExplainerAgent(llm_provider=LLMProvider.OPENAI)

# Use Anthropic Claude
agent = ManimExplainerAgent(llm_provider=LLMProvider.ANTHROPIC)
```

### Custom Prompts

Be specific for better results:

```python
# Basic
"Explain derivatives"

# Better
"Explain derivatives using the limit definition, show geometric interpretation with tangent lines"

# Best
"Create a 3-minute video explaining derivatives: start with rate of change concept, show limit definition, demonstrate with f(x)=x², include tangent line animation, and practical applications"
```

## 🛠️ Development

### Project Structure

```
manim-agent/
├── manim_agent/
│   ├── core/           # Core infrastructure
│   │   ├── base_agent.py      # Base agent class
│   │   ├── orchestrator.py    # Main coordinator
│   │   └── llm_service.py     # LLM integrations
│   ├── agents/         # Specialized agents
│   │   ├── content_agent.py        # Content research
│   │   ├── visual_design_agent.py  # Visual planning
│   │   └── manim_code_agent.py     # Code generation
│   └── utils/          # Utilities
└── frontend/           # Next.js web interface
```


## 🚀 Production Deployment

### Using Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using the Production Script

```bash
# Install production dependencies
pip install gunicorn

# Run production server
./start_production.sh
```

### Cloud Deployment

#### Deploy to Railway/Render/Fly.io

1. Push your code to GitHub
2. Connect your repository
3. Set environment variables:
   - `ANTHROPIC_API_KEY`
   - `USE_ADVANCED_ORCHESTRATOR=true`
4. Deploy!

#### Deploy to AWS/GCP/Azure

Use the provided Dockerfile:

```bash
# Build image
docker build -t manim-agent .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd)/generated_videos:/app/generated_videos \
  manim-agent
```

## 🎯 Best Practices

1. **Clear Prompts**: Be specific about what you want to explain
2. **Educational Focus**: The system is optimized for educational content
3. **Time Considerations**: Default videos are 3-5 minutes
4. **Visual Elements**: Mention specific visualizations you want
5. **Mathematical Notation**: Use standard mathematical terms

## 🐛 Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set key in current session
export ANTHROPIC_API_KEY='sk-...'
```

### Manim Rendering Issues
```bash
# Install system dependencies (macOS)
brew install cairo pango

# Install system dependencies (Ubuntu)
sudo apt-get install libcairo2-dev libpango1.0-dev
```

### Code Generation Issues
- Ensure your prompt is clear and educational
- Check API rate limits
- Review generated code for syntax errors