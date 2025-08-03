"""
Battle.net Launch Step for the Hearthstone Bot
"""

import subprocess
import os
import time
from typing import Dict, Any
from core.bot_state import BotState, BotContext
from core.exceptions import StepException
from .base_step import BaseStep
from config import get_battlenet_path


class BattleNetLaunchStep(BaseStep):
    """Step to launch Battle.net"""
    
    def get_step_name(self) -> str:
        return "Battle.net Launch"
    
    def can_skip(self, context: BotContext) -> bool:
        # Can skip if Hearthstone is already running
        window_service = self.services.get('window')
        if window_service and window_service.is_hearthstone_running():
            self.logger.info("Hearthstone is already running, skipping Battle.net step")
            return True
        return False
    
    def execute(self, context: BotContext) -> BotContext:
        """Launch Battle.net"""
        try:
            # Get Battle.net executable path from config
            battlenet_path = get_battlenet_path()
            
            # Check if Battle.net exists
            if not os.path.exists(battlenet_path):
                raise StepException(
                    self.get_step_name(),
                    f"Battle.net executable not found at: {battlenet_path}"
                )
            
            self.logger.info(f"Launching Battle.net from: {battlenet_path}")
            
            # Launch Battle.net
            subprocess.Popen([battlenet_path], shell=True)
            
            # Wait for Battle.net to start
            time.sleep(5)
            
            # Wait for Battle.net window to appear
            window_service = self.services.get('window')
            if window_service:
                battlenet_window = window_service.wait_for_window("Battle.net", timeout=30)
                if battlenet_window:
                    self.logger.info("Battle.net window found")
                    context.step_data['battlenet_window'] = battlenet_window
                    context.update_state(BotState.FINDING_PLAY_BUTTON)
                    return context
                else:
                    raise StepException(
                        self.get_step_name(),
                        "Battle.net window did not appear within timeout"
                    )
            else:
                # If no window service, just continue
                context.update_state(BotState.FINDING_PLAY_BUTTON)
                return context
                
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e)) 