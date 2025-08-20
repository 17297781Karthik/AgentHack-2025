"""
Mock Portia AI SDK for demo purposes
This replaces the actual Portia SDK to enable the Crisis Commander to run
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class ToolRunContext:
    """Mock context for tool execution"""
    def __init__(self, **kwargs):
        self.data = kwargs


class Tool(ABC):
    """Mock base Tool class to replace Portia Tool"""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.output_schema: tuple = ("dict", "")
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool logic"""
        pass
    
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """Make the tool callable"""
        return self.run(*args, **kwargs)