from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
import asyncio


class AgentMessage(BaseModel):
    """Message format for inter-agent communication"""
    sender: str
    recipient: str
    action: str
    payload: Dict[str, Any]
    timestamp: Optional[float] = None


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.state = {}
        
    def simulate_algorithm(self, task: str) -> Dict[str, Any]:
        """
        Mental simulation before action - MUST be called before process()
        Following CLAUDE.md protocol
        """
        simulation = {
            "task": task,
            "components_involved": [],
            "data_flow": [],
            "potential_issues": [],
            "planned_approach": ""
        }
        return simulation
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message and return response"""
        pass
    
    async def handle_error(self, error: Exception) -> None:
        """Handle errors gracefully"""
        print(f"[{self.name}] Error: {error}")
        
    def update_state(self, key: str, value: Any) -> None:
        """Update agent's internal state"""
        self.state[key] = value