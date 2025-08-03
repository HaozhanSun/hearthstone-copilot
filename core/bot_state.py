"""
State management for the Hearthstone Bot
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BotState(Enum):
    """Bot states"""
    IDLE = "idle"
    STARTING = "starting"
    CHECKING_OCR = "checking_ocr"
    LAUNCHING_BATTLENET = "launching_battlenet"
    FINDING_PLAY_BUTTON = "finding_play_button"
    WAITING_FOR_HEARTHSTONE = "waiting_for_hearthstone"
    NAVIGATING_HEARTHSTONE = "navigating_hearthstone"
    ACCESSING_COLLECTION = "accessing_collection"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class BotContext:
    """Context for bot execution"""
    state: BotState = BotState.IDLE
    step_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    start_time: Optional[datetime] = None
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def update_state(self, new_state: BotState, step_name: Optional[str] = None):
        """Update bot state and track step completion"""
        self.state = new_state
        if step_name and step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
        self.current_step = step_name
    
    def set_error(self, error_message: str):
        """Set error state"""
        self.state = BotState.ERROR
        self.error_message = error_message
    
    def reset_retry_count(self):
        """Reset retry count for current step"""
        self.retry_count = 0
    
    def increment_retry_count(self):
        """Increment retry count"""
        self.retry_count += 1
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since start"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def is_running(self) -> bool:
        """Check if bot is in a running state"""
        return self.state not in [BotState.IDLE, BotState.COMPLETED, BotState.ERROR, BotState.STOPPED]
    
    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if current step can be retried"""
        return self.retry_count < max_retries 