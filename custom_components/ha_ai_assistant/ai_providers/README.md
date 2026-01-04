# AI Providers

This directory contains AI provider implementations for the HA AI Assistant integration.

## Architecture

The AI provider architecture follows a plugin pattern, allowing easy addition of new AI services without modifying core integration code.

### Base Class

All AI providers must inherit from `AIProviderBase` and implement the following methods:

```python
class AIProviderBase(ABC):
    async def analyze_context(self, context: dict[str, Any]) -> AIResponse:
        """Analyze user's context and return suggestions/reminders."""
        
    async def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Chat interface for user interaction."""
        
    async def analyze_schedule(self, context: dict[str, Any]) -> AIResponse:
        """Analyze upcoming schedule and provide insights."""
        
    async def suggest_task_time(self, task: str, context: dict[str, Any]) -> AIResponse:
        """Suggest optimal time for a specific task."""
        
    async def close(self) -> None:
        """Clean up resources (optional)."""
```

### Context Structure

The `context` dictionary passed to AI providers typically contains:

```python
{
    "current_time": datetime,  # Current timestamp
    "todos": [
        {
            "summary": str,      # Task description
            "completed": bool,   # Completion status
            "due": datetime,     # Due date (optional)
            "entity_id": str,    # Home Assistant entity ID
        },
        # ... more todos
    ],
    "calendar_events": [
        {
            "summary": str,      # Event title
            "start": datetime,   # Event start time
            "end": datetime,     # Event end time
            "entity_id": str,    # Home Assistant entity ID
        },
        # ... more events
    ],
    "user_preferences": {
        "active_hours_start": int,  # e.g., 7 for 7 AM
        "active_hours_end": int,    # e.g., 23 for 11 PM
    }
}
```

### AIResponse Structure

The `AIResponse` dataclass is used for structured responses:

```python
@dataclass
class AIResponse:
    content: str                           # Main response text
    metadata: dict[str, Any] | None = None # Optional metadata (usage stats, etc.)
    error: str | None = None               # Error message if any
```

## Existing Providers

### GitHub Models Provider

Implementation: `github_models.py`

Uses the Azure AI Inference API to access GitHub Models (OpenAI models via GitHub).

**Configuration:**
- `api_token`: GitHub Personal Access Token with model access
- `model`: Model name (default: `gpt-4o-mini`)
- `endpoint`: API endpoint (default: `https://models.inference.ai.azure.com`)

**Features:**
- Context-aware chat interface
- Schedule analysis with conflict detection
- Task time suggestions
- Anti-spontaneity coaching through system prompts

## Adding a New Provider

Follow these steps to add support for a new AI service:

### 1. Create Provider File

Create a new file in this directory, e.g., `openai_provider.py`:

```python
"""OpenAI AI provider implementation."""
import logging
from typing import Any

from .base import AIProviderBase, AIResponse

_LOGGER = logging.getLogger(__name__)


class OpenAIProvider(AIProviderBase):
    """OpenAI AI provider."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize OpenAI provider."""
        super().__init__(config)
        self.api_key = config.get("api_token")
        self.model = config.get("model", "gpt-4")
        # Initialize your provider-specific client
    
    async def analyze_context(self, context: dict[str, Any]) -> AIResponse:
        """Implement context analysis."""
        # Your implementation here
        pass
    
    async def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Implement chat interface."""
        # Your implementation here
        pass
    
    async def analyze_schedule(self, context: dict[str, Any]) -> AIResponse:
        """Implement schedule analysis."""
        # Your implementation here
        pass
    
    async def suggest_task_time(self, task: str, context: dict[str, Any]) -> AIResponse:
        """Implement task time suggestions."""
        # Your implementation here
        pass
    
    async def close(self) -> None:
        """Clean up resources."""
        # Close connections, release resources, etc.
        pass
```

### 2. Update __init__.py

Add your provider to `__init__.py`:

```python
from .openai_provider import OpenAIProvider

__all__ = [
    "AIProviderBase",
    "AIResponse",
    "GitHubModelsProvider",
    "OpenAIProvider",  # Add here
]
```

### 3. Update const.py

Add your provider constant to `const.py`:

```python
AI_PROVIDER_OPENAI: Final = "openai"

SUPPORTED_PROVIDERS: Final = [
    AI_PROVIDER_GITHUB_MODELS,
    AI_PROVIDER_OPENAI,  # Add here
]
```

### 4. Update config_flow.py

Add configuration options for your provider in the config flow.

### 5. Update __init__.py (Integration)

Update the provider factory function in the main `__init__.py`:

```python
def _create_ai_provider(config: dict) -> AIProviderBase:
    """Create AI provider instance."""
    provider_type = config.get(CONF_AI_PROVIDER)
    
    if provider_type == AI_PROVIDER_GITHUB_MODELS:
        return GitHubModelsProvider(config)
    elif provider_type == AI_PROVIDER_OPENAI:
        return OpenAIProvider(config)
    # Add more providers here
```

### 6. Add Requirements

If your provider needs additional Python packages, add them to `manifest.json`:

```json
{
  "requirements": [
    "aiohttp>=3.9.0",
    "python-dateutil>=2.8.0",
    "openai>=1.0.0"  // Add your dependency
  ]
}
```

## Best Practices

1. **Async/Await**: All provider methods should be async and use `await` for I/O operations
2. **Error Handling**: Catch and log errors, return meaningful error messages in `AIResponse`
3. **Resource Cleanup**: Implement `close()` to properly release resources
4. **Rate Limiting**: Implement rate limiting if your provider has API limits
5. **Logging**: Use the logger to help with debugging
6. **Type Hints**: Use type hints for all method parameters and return values
7. **Context Formatting**: Create helper methods to format context data for your AI model
8. **System Prompts**: Design prompts that align with the anti-spontaneity goal

## Testing Your Provider

Test your provider with:

```python
# Create test context
context = {
    "current_time": datetime.now(),
    "todos": [
        {"summary": "Test task", "completed": False}
    ],
    "calendar_events": [],
}

# Initialize provider
provider = YourProvider({"api_token": "test_token"})

# Test methods
response = await provider.analyze_context(context)
chat_response = await provider.chat("Hello!")
schedule = await provider.analyze_schedule(context)
task_time = await provider.suggest_task_time("New task", context)

# Cleanup
await provider.close()
```

## Contributing

When contributing a new provider:

1. Follow the existing code style
2. Add comprehensive error handling
3. Include docstrings for all public methods
4. Update this README with provider details
5. Test with real API credentials
6. Consider privacy and security implications
