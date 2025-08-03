"""
Custom exceptions for the Hearthstone Bot
"""


class BotException(Exception):
    """Base exception for all bot-related errors"""
    pass


class StepException(BotException):
    """Exception raised when a step fails"""
    def __init__(self, step_name: str, message: str, retry_count: int = 0):
        self.step_name = step_name
        self.retry_count = retry_count
        super().__init__(f"Step '{step_name}' failed: {message}")


class ServiceException(BotException):
    """Exception raised when a service fails"""
    def __init__(self, service_name: str, message: str):
        self.service_name = service_name
        super().__init__(f"Service '{service_name}' failed: {message}")


class WindowNotFoundException(ServiceException):
    """Exception raised when a required window is not found"""
    def __init__(self, window_name: str):
        super().__init__("WindowService", f"Window '{window_name}' not found")


class OCRException(ServiceException):
    """Exception raised when OCR operations fail"""
    def __init__(self, message: str):
        super().__init__("OCRService", message)


class ScreenshotException(ServiceException):
    """Exception raised when screenshot operations fail"""
    def __init__(self, message: str):
        super().__init__("ScreenshotService", message) 