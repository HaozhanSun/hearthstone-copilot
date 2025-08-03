"""
Base step class for the Hearthstone Bot
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from core.bot_state import BotState, BotContext
from core.exceptions import StepException


class BaseStep(ABC):
    """Abstract base class for all bot steps"""
    
    def __init__(self, services: Dict[str, Any], max_retries: int = 3):
        self.services = services
        self.max_retries = max_retries
        self.logger = services.get('logger')
    
    @abstractmethod
    def execute(self, context: BotContext) -> BotContext:
        """Execute the step and return updated context"""
        pass
    
    @abstractmethod
    def can_skip(self, context: BotContext) -> bool:
        """Check if this step can be skipped"""
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Get the name of this step"""
        pass
    
    def handle_error(self, context: BotContext, error: Exception) -> BotContext:
        """Handle step execution errors"""
        import traceback
        
        step_name = self.get_step_name()
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        self.logger.error(f"Step '{step_name}' failed: {error_message}")
        self.logger.error(f"Stack trace:\n{stack_trace}")
        
        context.increment_retry_count()
        
        if context.can_retry(self.max_retries):
            self.logger.info(f"Retrying step '{step_name}' (attempt {context.retry_count}/{self.max_retries})")
            return context
        else:
            self.logger.error(f"Step '{step_name}' failed after {self.max_retries} attempts")
            context.set_error(f"Step '{step_name}' failed: {error_message}\nStack trace:\n{stack_trace}")
            return context
    
    def pre_execute(self, context: BotContext) -> BotContext:
        """Pre-execution setup"""
        context.reset_retry_count()
        context.current_step = self.get_step_name()
        self.logger.info(f"Starting step: {self.get_step_name()}")
        return context
    
    def post_execute(self, context: BotContext) -> BotContext:
        """Post-execution cleanup"""
        self.logger.info(f"Completed step: {self.get_step_name()}")
        return context
    
    def run(self, context: BotContext) -> BotContext:
        """Run the step with error handling"""
        try:
            context = self.pre_execute(context)
            context = self.execute(context)
            context = self.post_execute(context)
            return context
        except Exception as e:
            return self.handle_error(context, e) 