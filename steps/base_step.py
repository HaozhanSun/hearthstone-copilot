"""
Base step class for the Hearthstone Bot
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
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
    
    # === Common Utility Methods ===
    
    def validate_services(self, required_services: list) -> None:
        """Validate that required services are available"""
        services = [self.services.get(service) for service in required_services]
        if not all(services):
            raise StepException(self.get_step_name(), f"Required services not available: {required_services}")
    
    def get_service(self, service_name: str):
        """Get a service by name"""
        return self.services.get(service_name)
    
    def focus_window_with_retry(self, window, window_service, max_retries: int = 1) -> bool:
        """Focus window with optional retry logic"""
        for attempt in range(max_retries + 1):
            if window_service.focus_window(window):
                return True
            
            if attempt < max_retries:
                self.logger.warning(f"Failed to focus window (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(0.5)  # Small delay between attempts
        
        return False
    
    def capture_screenshot_safe(self, screenshot_service, x: int, y: int, width: int, height: int, 
                               retry_count: int = 3, retry_delay: float = 1.0):
        """Safely capture screenshot with retry logic"""
        for attempt in range(retry_count):
            screenshot = screenshot_service.capture_window(x, y, width, height)
            if screenshot is not None:
                return screenshot
            
            if attempt < retry_count - 1:
                self.logger.warning(f"Screenshot capture failed (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(retry_delay)
        
        return None
    
    def capture_window_screenshot_safe(self, screenshot_service, window, retry_count: int = 3, retry_delay: float = 1.0):
        """Safely capture window screenshot with retry logic"""
        for attempt in range(retry_count):
            screenshot = screenshot_service.capture_window_object(window)
            if screenshot is not None:
                return screenshot
            
            if attempt < retry_count - 1:
                self.logger.warning(f"Window screenshot capture failed (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(retry_delay)
        
        return None
    
    def save_debug_screenshot(self, screenshot, name: str, success: bool, message: str, step: str = None):
        """Save debug screenshot with consistent formatting"""
        logger = self.get_service('logger')
        if logger and screenshot is not None:
            step_name = step or self.get_step_name()
            logger.save_debug_screenshot(screenshot, name, success, message, step_name)
    
    def safe_step_execution(self, func, *args, **kwargs):
        """Execute a function with consistent error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e))
    
    def check_bot_running(self, context: BotContext) -> bool:
        """Check if bot should continue running"""
        return context.state not in [BotState.STOPPED, BotState.ERROR]
    
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