"""
Main bot controller for the Hearthstone Bot
"""

import threading
import time
from typing import Dict, Any, List, Optional
from core.bot_state import BotState, BotContext
from core.exceptions import BotException
from steps import (
    OCRManagementStep,
    BattleNetLaunchStep,
    PlayButtonStep,
    HearthstoneNavigationStep,
    CollectionAccessStep
)
from steps.base_step import BaseStep


class BotController:
    """Main bot controller that orchestrates all steps"""
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = services.get('logger')
        self.steps = self._initialize_steps()
        self.context = BotContext()
        self.running = False
        self.stop_event = threading.Event()
        self.execution_thread: Optional[threading.Thread] = None
        self.start_lock = threading.Lock()  # Add lock to prevent multiple simultaneous starts
    
    def _initialize_steps(self) -> List[BaseStep]:
        """Initialize all bot steps"""
        return [
            OCRManagementStep(self.services),
            BattleNetLaunchStep(self.services),
            PlayButtonStep(self.services),
            HearthstoneNavigationStep(self.services),
            CollectionAccessStep(self.services)
        ]
    
    def start(self) -> None:
        """Start the bot"""
        import threading
        import time
        
        # Use lock to prevent multiple simultaneous starts
        if not self.start_lock.acquire(blocking=False):
            self.logger.warning("Bot start already in progress")
            return
        
        try:
            if self.running:
                self.logger.warning("Bot is already running")
                return
            
            # Additional check to prevent race conditions
            if hasattr(self, 'execution_thread') and self.execution_thread and self.execution_thread.is_alive():
                self.logger.warning("Bot execution thread is already alive")
                return
            
            # Set running flag BEFORE starting thread to prevent race conditions
            self.running = True
            self.stop_event.clear()
            self.context = BotContext(state=BotState.STARTING)
            
            # Start execution in a separate thread
            self.execution_thread = threading.Thread(target=self._run, daemon=True, name="BotExecutionThread")
            self.execution_thread.start()
            
            self.logger.info("Bot started successfully")
        except Exception as e:
            # Reset state if thread creation fails
            self.running = False
            self.execution_thread = None
            self.logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            self.start_lock.release()
    
    def stop(self) -> None:
        """Stop the bot"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        # Force terminate execution thread
        if self.execution_thread and self.execution_thread.is_alive():
            try:
                self.execution_thread.join(timeout=2)
                if self.execution_thread.is_alive():
                    self.logger.warning("Execution thread did not stop, forcing termination")
                    # Cannot set daemon on active thread, just log and continue
                    self.logger.info("Thread will be terminated when process exits")
            except Exception as e:
                self.logger.error(f"Error stopping execution thread: {e}")
        
        self.context.update_state(BotState.STOPPED)
        self.logger.info("Bot stopped")
    
    def _run(self) -> None:
        """Main bot execution loop"""
        try:
            
            for step in self.steps:
                # Check if bot should stop
                if not self.running or self.stop_event.is_set():
                    self.logger.info("Bot execution interrupted")
                    break
                
                # Check if step can be skipped
                if step.can_skip(self.context):
                    self.logger.info(f"Skipping step: {step.get_step_name()}")
                    continue
                
                # Execute step
                step_name = step.get_step_name()
                self.logger.info(f"Executing step: {step_name}")
                self.context = step.run(self.context)
                
                # Check for errors
                if self.context.state == BotState.ERROR:
                    self.logger.error(f"Bot execution failed: {self.context.error_message}")
                    break
                
                # Check if step was successful
                if not self.context.is_running():
                    break
                
                # Small delay between steps
                time.sleep(0.5)
            
            # Final state update
            if self.context.state not in [BotState.ERROR, BotState.STOPPED]:
                if self.context.state == BotState.COMPLETED:
                    self.logger.info("Bot execution completed successfully!")
                else:
                    self.context.update_state(BotState.COMPLETED)
                    self.logger.info("Bot execution completed successfully!")
            
        except Exception as e:
            import traceback
            stack_trace = traceback.format_exc()
            self.logger.error(f"Unexpected error in bot execution: {e}")
            self.logger.error(f"Stack trace:\n{stack_trace}")
            self.context.set_error(f"Unexpected error: {e}\nStack trace:\n{stack_trace}")
        finally:
            self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'running': self.running,
            'state': self.context.state.value,
            'current_step': self.context.current_step,
            'completed_steps': self.context.completed_steps,
            'error_message': self.context.error_message,
            'elapsed_time': self.context.get_elapsed_time(),
            'retry_count': self.context.retry_count
        }
    
    def is_running(self) -> bool:
        """Check if bot is running"""
        return self.running
    
    def get_context(self) -> BotContext:
        """Get current bot context"""
        return self.context 