from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
import asyncio
import json
import os
import uuid
from datetime import datetime
import logging

# Import our agent system
from manim_agent.core.orchestrator import ManimExplainerAgent
from manim_agent.core.advanced_orchestrator import AdvancedManimExplainerAgent
from manim_agent.core.llm_service import LLMService
from manim_agent.agents.content_agent import ContentAgent
from manim_agent.agents.visual_design_agent import VisualDesignAgent
from manim_agent.agents.manim_code_agent import ManimCodeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Manim Agent API")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ConversationMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    video_url: Optional[str] = None

class PromptRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[ConversationMessage]] = []
    model: Optional[str] = "sonnet"  # "sonnet" or "opus"
    duration_minutes: Optional[int] = 1  # Target duration in minutes

class GenerationStatus(BaseModel):
    session_id: str
    status: str
    current_agent: Optional[str] = None
    progress: float
    message: str
    video_url: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None

class VideoInfo(BaseModel):
    session_id: str
    prompt: str
    video_url: str
    created_at: datetime
    duration: Optional[float] = None

# Global storage (in production, use Redis or similar)
sessions: Dict[str, dict] = {}
websocket_connections: Dict[str, WebSocket] = {}

def fix_manim_errors(code: str, error: str) -> str:
    """Fix common Manim rendering errors"""
    # Fix syntax errors first
    if "SyntaxError" in error:
        # Fix unclosed parentheses
        if "'(' was never closed" in error:
            # Count open and close parentheses
            open_count = code.count('(')
            close_count = code.count(')')
            if open_count > close_count:
                # Add missing closing parentheses at the end
                code += ')' * (open_count - close_count)
                logger.info(f"Fixed unclosed parentheses - added {open_count - close_count} closing parentheses")
        
        # Fix unclosed brackets
        if "'[' was never closed" in error:
            open_count = code.count('[')
            close_count = code.count(']')
            if open_count > close_count:
                code += ']' * (open_count - close_count)
                logger.info(f"Fixed unclosed brackets - added {open_count - close_count} closing brackets")
        
        # Fix unclosed braces
        if "'{' was never closed" in error:
            open_count = code.count('{')
            close_count = code.count('}')
            if open_count > close_count:
                code += '}' * (open_count - close_count)
                logger.info(f"Fixed unclosed braces - added {open_count - close_count} closing braces")
    
    # Fix IndexError with self.mobjects
    if "IndexError" in error and "self.mobjects" in error:
        # Replace problematic self.mobjects references
        import re
        # Pattern to match self.mobjects[-1][0][0] type references
        pattern = r'self\.mobjects\[-?\d+\]\[.*?\]'
        
        # Check if array_boxes exists in the code
        if "array_boxes" in code:
            # Replace with stored reference
            code = re.sub(pattern + r'(?=.*?, UP)', 'array_boxes', code)
            logger.info("Fixed self.mobjects reference by using array_boxes")
        else:
            # Create a dummy reference
            code = re.sub(pattern, 'self.mobjects[0] if self.mobjects else Dot()', code)
            logger.info("Fixed self.mobjects reference with safety check")
    
    # Fix ShowCreation deprecation
    if "ShowCreation" in error:
        code = code.replace("ShowCreation(", "Create(")
        logger.info("Fixed ShowCreation -> Create")
    
    # Fix color interpolation errors
    if "interpolate_color" in error or "'str' object has no attribute 'interpolate'" in error:
        # Replace string colors with ManimColor objects
        code = code.replace("interpolate_color(self.PRIMARY, GREY,", "interpolate_color(ManimColor(self.PRIMARY), ManimColor(GREY),")
        code = code.replace("interpolate_color(", "ManimColor.from_rgb(")
        # Alternative fix - use direct color assignment
        import re
        code = re.sub(r'color = interpolate_color\([^)]+\)', 'color = self.PRIMARY', code)
        logger.info("Fixed color interpolation issues")
    
    # Fix other deprecated animations
    deprecated_replacements = {
        "ShowIncreasingSubsets": "Create",
        "ShowSubmobjectsOneByOne": "Create",
        "ShowCreationThenDestruction": "ShowPassingFlash",
        "WiggleOutThenIn": "Wiggle",
        "CircleIndicate": "Indicate",
    }
    
    for old_anim, new_anim in deprecated_replacements.items():
        if old_anim in error or old_anim in code:
            code = code.replace(f"{old_anim}(", f"{new_anim}(")
            logger.info(f"Fixed {old_anim} -> {new_anim}")
    
    # Fix missing imports
    if "ManimColor" in code and "from manim import" in code:
        # Ensure ManimColor is imported
        if "ManimColor" not in code.split("from manim import")[1].split("\n")[0]:
            code = code.replace("from manim import *", "from manim import *\nfrom manim.utils.color import ManimColor")
    
    return code

# Initialize the agent system
orchestrator = None

async def initialize_agents():
    """Initialize the agent system"""
    global orchestrator
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize orchestrator with Anthropic
        from manim_agent.core.llm_service import LLMProvider
        
        # Use advanced orchestrator for all videos now (it handles both short and long)
        use_advanced = os.getenv("USE_ADVANCED_ORCHESTRATOR", "true").lower() == "true"
        
        if use_advanced:
            logger.info("Using Advanced Orchestrator (supports all durations)")
            orchestrator = AdvancedManimExplainerAgent(
                llm_provider=LLMProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            orchestrator = ManimExplainerAgent(
                llm_provider=LLMProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        logger.info("Agent system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    await initialize_agents()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections[session_id] = websocket
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while True:
            # Keep connection alive and handle ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                # Respond to ping with pong to keep connection alive
                await websocket.send_text("pong")
            # Just keep the connection open for other messages
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        if session_id in websocket_connections:
            del websocket_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        if session_id in websocket_connections:
            del websocket_connections[session_id]

async def send_status_update(session_id: str, status: GenerationStatus):
    """Send status update via WebSocket"""
    if session_id in websocket_connections:
        try:
            await websocket_connections[session_id].send_json(status.dict())
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")

async def send_streaming_update(session_id: str, agent: str, content: str):
    """Send streaming content update to WebSocket client"""
    if session_id in websocket_connections:
        try:
            await websocket_connections[session_id].send_json({
                "type": "streaming",
                "agent": agent,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send streaming update: {e}")

@app.post("/api/generate")
async def generate_video(request: PromptRequest, background_tasks: BackgroundTasks):
    """Generate a Manim video from a prompt"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Initialize session
    sessions[session_id] = {
        "prompt": request.prompt,
        "status": "initializing",
        "created_at": datetime.now(),
        "video_path": None
    }
    
    # Start generation in background
    background_tasks.add_task(
        process_generation,
        session_id,
        request.prompt,
        request.conversation_history,
        request.model,
        request.duration_minutes
    )
    
    return {"session_id": session_id, "message": "Generation started"}

async def process_generation(session_id: str, prompt: str, conversation_history: List[ConversationMessage] = [], model: str = "sonnet", duration_minutes: int = 3):
    """Process video generation with status updates"""
    logger.info(f"Starting generation for session {session_id}: model={model}, duration={duration_minutes}m")
    
    try:
        # Update status: Content Research
        await send_status_update(session_id, GenerationStatus(
            session_id=session_id,
            status="processing",
            current_agent="ContentAgent",
            progress=0.2,
            message="Researching educational content...",
            details=f"Creating {duration_minutes}-minute video using {model.upper()} model"
        ))
        
        # Build context from conversation history
        context = ""
        if conversation_history:
            context = "Previous conversation:\n"
            for msg in conversation_history:
                context += f"{msg.role}: {msg.content}\n"
                if msg.video_url:
                    context += f"(Video was generated for this message)\n"
            context += "\n"
        
        # Check if using advanced orchestrator
        if hasattr(orchestrator, 'create_video'):
            # Use advanced orchestrator's comprehensive method
            logger.info(f"Using advanced video creation pipeline with {model} model for {duration_minutes} minutes")
            
            # Create a status callback function
            async def status_callback(agent_name: str, action: str, progress: float):
                await send_status_update(session_id, GenerationStatus(
                    session_id=session_id,
                    status="processing",
                    current_agent=agent_name,
                    progress=progress,
                    message=action,
                    details=f"Agent {agent_name} is working..."
                ))
            
            # Pass model and duration to orchestrator
            manim_code = await orchestrator.create_video(prompt, context, model, duration_minutes, status_callback)
            
            # Skip individual agent processing since create_video handles everything
            # Just save the code for rendering
            code_result_payload = {"code": manim_code}
        else:
            # Use standard agent processing
            from manim_agent.core.base_agent import AgentMessage
            
            content_msg = AgentMessage(
                sender="API",
                recipient="ContentAgent",
                action="research",
                payload={
                    "topic": prompt,
                    "context": context,
                    "full_prompt": context + f"Current request: {prompt}"
                }
            )
            content_result = await orchestrator.agents["content"].process(content_msg)
        
            # Update status: Visual Design
            await send_status_update(session_id, GenerationStatus(
                session_id=session_id,
                status="processing",
                current_agent="VisualDesignAgent",
                progress=0.4,
                message="Planning visual animations...",
                details=f"Designing scenes and transitions for {duration_minutes}-minute video"
            ))
            
            # Generate visual design
            visual_msg = AgentMessage(
                sender="API",
                recipient="VisualDesignAgent",
                action="design",
                payload={
                    "content": content_result.payload.get("content", {}),
                    "topic": prompt,
                    "context": context,
                    "full_prompt": context + f"Current request: {prompt}"
                }
            )
            visual_result = await orchestrator.agents["visual_design"].process(visual_msg)
            
            # Update status: Code Generation
            await send_status_update(session_id, GenerationStatus(
                session_id=session_id,
                status="processing",
                current_agent="ManimCodeAgent",
                progress=0.6,
                message="Generating animation code...",
                details="Writing Manim scene code with animations"
            ))
            
            # Generate Manim code
            code_msg = AgentMessage(
                sender="API",
                recipient="ManimCodeAgent",
                action="generate_code",
                payload={
                    "content": content_result.payload.get("content", {}),
                    "visual_design": visual_result.payload.get("design", {}),
                    "topic": prompt,
                    "context": context,
                    "full_prompt": context + f"Current request: {prompt}"
                }
            )
            code_result = await orchestrator.agents["manim_code"].process(code_msg)
            code_result_payload = code_result.payload
        
        # Update status: Rendering
        await send_status_update(session_id, GenerationStatus(
            session_id=session_id,
            status="processing",
            current_agent="Renderer",
            progress=0.8,
            message="Rendering animation...",
            details="Running Manim to create MP4 video"
        ))
        
        # Save and render the code
        filename = f"generated_{session_id}.py"
        filepath = os.path.join("generated_videos", filename)
        os.makedirs("generated_videos", exist_ok=True)
        
        with open(filepath, "w") as f:
            f.write(code_result_payload.get("code", ""))
        
        # Render with Manim (with error recovery)
        max_render_attempts = 3
        render_attempt = 0
        output_path = None
        last_error = None
        
        while render_attempt < max_render_attempts:
            try:
                output_path = await render_manim_video(filepath, session_id)
                break  # Success!
            except Exception as e:
                render_attempt += 1
                last_error = str(e)
                logger.warning(f"Render attempt {render_attempt} failed: {last_error}")
                
                if render_attempt < max_render_attempts:
                    # Try to fix common errors
                    await send_status_update(session_id, GenerationStatus(
                        session_id=session_id,
                        status="processing",
                        current_agent="ErrorFixer",
                        progress=0.85,
                        message="Fixing rendering errors...",
                        details=f"Attempting to fix: {last_error}"
                    ))
                    
                    # Read and fix the code
                    with open(filepath, "r") as f:
                        code = f.read()
                    
                    # Apply fixes
                    fixed_code = fix_manim_errors(code, last_error)
                    
                    # Write fixed code
                    with open(filepath, "w") as f:
                        f.write(fixed_code)
        
        if output_path is None:
            raise Exception(f"Failed to render after {max_render_attempts} attempts. Last error: {last_error}")
        
        # Update session
        sessions[session_id]["status"] = "completed"
        sessions[session_id]["video_path"] = output_path
        
        # Send completion status
        await send_status_update(session_id, GenerationStatus(
            session_id=session_id,
            status="completed",
            current_agent=None,
            progress=1.0,
            message="Video generated successfully!",
            video_url=f"/api/video/{session_id}"
        ))
        
    except Exception as e:
        logger.error(f"Generation failed for session {session_id}: {e}")
        sessions[session_id]["status"] = "failed"
        
        await send_status_update(session_id, GenerationStatus(
            session_id=session_id,
            status="failed",
            current_agent=None,
            progress=0,
            message="Generation failed",
            error=str(e)
        ))

async def render_manim_video(script_path: str, session_id: str) -> str:
    """Render Manim script to video"""
    import subprocess
    
    output_dir = os.path.join("generated_videos", "media")
    
    # Run Manim render command
    cmd = [
        "manim", "-pql",  # Preview quality for faster rendering
        "--media_dir", output_dir,
        script_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Manim render failed: {result.stderr}")
    
    # Find the generated video file
    # Manim outputs to media/videos/{quality}/{scene_name}.mp4
    video_pattern = os.path.join(output_dir, "videos", "**", "*.mp4")
    import glob
    video_files = glob.glob(video_pattern, recursive=True)
    
    if not video_files:
        raise Exception("No video file generated")
    
    # Copy to accessible location
    final_path = os.path.join("generated_videos", f"{session_id}.mp4")
    import shutil
    shutil.copy(video_files[0], final_path)
    
    return final_path

@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """Get generation status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return GenerationStatus(
        session_id=session_id,
        status=session["status"],
        progress=1.0 if session["status"] == "completed" else 0.5,
        message=f"Status: {session['status']}",
        video_url=f"/api/video/{session_id}" if session.get("video_path") else None
    )

@app.get("/api/video/{session_id}")
async def get_video(session_id: str):
    """Serve generated video file"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    video_path = sessions[session_id].get("video_path")
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"manim_animation_{session_id}.mp4"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "manim-agent-api",
        "version": "1.0.0",
        "model": "claude-sonnet-4"
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"status": "ok", "message": "API is running"}

@app.get("/api/history")
async def get_history():
    """Get generation history"""
    history = []
    for session_id, session in sessions.items():
        if session["status"] == "completed":
            history.append(VideoInfo(
                session_id=session_id,
                prompt=session["prompt"],
                video_url=f"/api/video/{session_id}",
                created_at=session["created_at"]
            ))
    
    return sorted(history, key=lambda x: x.created_at, reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)