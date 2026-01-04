"""Base class for AI providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AIResponse:
    """Response from AI provider."""

    content: str
    metadata: dict[str, Any] | None = None
    error: str | None = None


class AIProviderBase(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the AI provider.
        
        Args:
            config: Configuration dictionary containing API keys, endpoints, etc.
        """
        self.config = config

    @abstractmethod
    async def analyze_context(self, context: dict[str, Any]) -> AIResponse:
        """Analyze user's current context and return suggestions/reminders.
        
        Args:
            context: Dictionary containing:
                - todos: List of todo items from Home Assistant
                - calendar_events: List of upcoming calendar events
                - current_time: Current datetime
                - user_preferences: User settings and preferences
        
        Returns:
            AIResponse with analysis and suggestions
        """
        pass

    @abstractmethod
    async def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Chat interface for user interaction.
        
        Args:
            message: User's message/question
            context: Optional context dictionary with relevant information
        
        Returns:
            AI's response as a string
        """
        pass

    @abstractmethod
    async def analyze_schedule(self, context: dict[str, Any]) -> AIResponse:
        """Analyze upcoming schedule and provide insights.
        
        Args:
            context: Dictionary containing calendar events and todos
        
        Returns:
            AIResponse with schedule analysis
        """
        pass

    @abstractmethod
    async def suggest_task_time(self, task: str, context: dict[str, Any]) -> AIResponse:
        """Suggest optimal time for a specific task.
        
        Args:
            task: Description of the task
            context: Dictionary containing schedule and preferences
        
        Returns:
            AIResponse with time suggestions
        """
        pass

    async def close(self) -> None:
        """Clean up resources. Override if needed."""
        pass
