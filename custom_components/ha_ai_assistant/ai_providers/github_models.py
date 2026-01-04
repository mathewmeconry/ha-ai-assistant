"""GitHub Models AI provider implementation."""
import json
import logging
from typing import Any

import aiohttp

from .base import AIProviderBase, AIResponse

_LOGGER = logging.getLogger(__name__)


class GitHubModelsProvider(AIProviderBase):
    """GitHub Models AI provider using Azure AI Inference API."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize GitHub Models provider.
        
        Args:
            config: Configuration containing api_token, model, and endpoint
        """
        super().__init__(config)
        self.api_token = config.get("api_token")
        self.model = config.get("model", "gpt-4o-mini")
        self.endpoint = config.get("endpoint", "https://models.inference.ai.azure.com")
        self.session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI."""
        return """You are a personal AI assistant designed to help reduce spontaneity and improve organization.

Your role is to:
1. Analyze the user's todo lists and calendar events
2. Provide timely reminders about important tasks and events
3. Help the user stay organized and focused
4. Discourage impulsive decisions and encourage planning
5. Suggest optimal times for tasks based on the schedule
6. Identify conflicts, gaps, or opportunities in the schedule

When analyzing context:
- Be proactive but not overwhelming
- Focus on high-priority and time-sensitive items
- Encourage completion of existing tasks before starting new ones
- Identify tasks that have been pending for too long
- Suggest breaking down large tasks into smaller steps
- Be supportive and positive in your tone

Remember: Your goal is to help the user be more organized and less spontaneous."""

    async def _make_api_call(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Make API call to GitHub Models.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Sampling temperature (0-1)
        
        Returns:
            API response dictionary
        """
        session = self._get_session()
        url = f"{self.endpoint}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }
        
        payload = {
            "messages": messages,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": 1000,
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error(
                        "GitHub Models API error: %s - %s",
                        response.status,
                        error_text,
                    )
                    return {
                        "error": f"API error: {response.status}",
                        "details": error_text,
                    }
                
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error calling GitHub Models API: %s", err)
            return {"error": f"Network error: {err}"}
        except Exception as err:
            _LOGGER.error("Unexpected error calling GitHub Models API: %s", err)
            return {"error": f"Unexpected error: {err}"}

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context information for the AI.
        
        Args:
            context: Context dictionary
        
        Returns:
            Formatted context string
        """
        parts = []
        
        if "current_time" in context:
            parts.append(f"Current time: {context['current_time']}")
        
        if "todos" in context and context["todos"]:
            parts.append("\nTodo Items:")
            for todo in context["todos"]:
                status = "✓" if todo.get("completed") else "○"
                parts.append(f"  {status} {todo.get('summary', 'Untitled')}")
                if todo.get("due"):
                    parts.append(f"    Due: {todo['due']}")
        
        if "calendar_events" in context and context["calendar_events"]:
            parts.append("\nUpcoming Calendar Events:")
            for event in context["calendar_events"]:
                parts.append(f"  • {event.get('summary', 'Untitled')}")
                if event.get("start"):
                    parts.append(f"    Start: {event['start']}")
                if event.get("end"):
                    parts.append(f"    End: {event['end']}")
        
        if not parts:
            return "No context information available."
        
        return "\n".join(parts)

    async def analyze_context(self, context: dict[str, Any]) -> AIResponse:
        """Analyze user's current context and return suggestions/reminders."""
        context_str = self._format_context(context)
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": f"Please analyze my current context and provide any reminders, "
                f"suggestions, or insights that would help me stay organized:\n\n{context_str}",
            },
        ]
        
        response = await self._make_api_call(messages)
        
        if "error" in response:
            return AIResponse(
                content="",
                error=response["error"],
                metadata={"details": response.get("details")},
            )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return AIResponse(
                content=content,
                metadata={
                    "model": self.model,
                    "usage": response.get("usage", {}),
                },
            )
        except (KeyError, IndexError) as err:
            _LOGGER.error("Failed to parse API response: %s", err)
            return AIResponse(
                content="",
                error=f"Failed to parse response: {err}",
            )

    async def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Chat interface for user interaction."""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
        ]
        
        if context:
            context_str = self._format_context(context)
            messages.append({
                "role": "system",
                "content": f"Current context:\n{context_str}",
            })
        
        messages.append({"role": "user", "content": message})
        
        response = await self._make_api_call(messages)
        
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as err:
            _LOGGER.error("Failed to parse chat response: %s", err)
            return f"Error: Failed to parse response: {err}"

    async def analyze_schedule(self, context: dict[str, Any]) -> AIResponse:
        """Analyze upcoming schedule and provide insights."""
        context_str = self._format_context(context)
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": f"Please analyze my upcoming schedule and provide insights about:\n"
                f"- Busy periods and gaps\n"
                f"- Potential conflicts\n"
                f"- Time for completing pending tasks\n"
                f"- Overall workload assessment\n\n{context_str}",
            },
        ]
        
        response = await self._make_api_call(messages, temperature=0.5)
        
        if "error" in response:
            return AIResponse(
                content="",
                error=response["error"],
                metadata={"details": response.get("details")},
            )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return AIResponse(
                content=content,
                metadata={
                    "model": self.model,
                    "usage": response.get("usage", {}),
                },
            )
        except (KeyError, IndexError) as err:
            return AIResponse(
                content="",
                error=f"Failed to parse response: {err}",
            )

    async def suggest_task_time(self, task: str, context: dict[str, Any]) -> AIResponse:
        """Suggest optimal time for a specific task."""
        context_str = self._format_context(context)
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": f"I need to schedule the following task: '{task}'\n\n"
                f"Based on my current schedule, when would be the best time to do this? "
                f"Consider my existing commitments and provide specific time suggestions.\n\n"
                f"{context_str}",
            },
        ]
        
        response = await self._make_api_call(messages, temperature=0.5)
        
        if "error" in response:
            return AIResponse(
                content="",
                error=response["error"],
                metadata={"details": response.get("details")},
            )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return AIResponse(
                content=content,
                metadata={
                    "model": self.model,
                    "usage": response.get("usage", {}),
                },
            )
        except (KeyError, IndexError) as err:
            return AIResponse(
                content="",
                error=f"Failed to parse response: {err}",
            )

    async def close(self) -> None:
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
