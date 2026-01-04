"""Constants for the HA AI Assistant integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "ha_ai_assistant"

# Configuration keys
CONF_AI_PROVIDER: Final = "ai_provider"
CONF_API_TOKEN: Final = "api_token"
CONF_CHECK_INTERVAL: Final = "check_interval"
CONF_ACTIVE_HOURS_START: Final = "active_hours_start"
CONF_ACTIVE_HOURS_END: Final = "active_hours_end"
CONF_MODEL: Final = "model"
CONF_ENABLE_REMINDERS: Final = "enable_reminders"
CONF_ENABLE_SCHEDULE_ANALYSIS: Final = "enable_schedule_analysis"

# AI Provider types
AI_PROVIDER_GITHUB_MODELS: Final = "github_models"
AI_PROVIDER_OPENAI: Final = "openai"
AI_PROVIDER_ANTHROPIC: Final = "anthropic"
AI_PROVIDER_LOCAL: Final = "local"

SUPPORTED_PROVIDERS: Final = [
    AI_PROVIDER_GITHUB_MODELS,
]

# Default values
DEFAULT_CHECK_INTERVAL: Final = 60  # minutes
DEFAULT_ACTIVE_HOURS_START: Final = 7  # 7 AM
DEFAULT_ACTIVE_HOURS_END: Final = 23  # 11 PM
DEFAULT_MODEL_GITHUB: Final = "gpt-4o-mini"
DEFAULT_ENABLE_REMINDERS: Final = True
DEFAULT_ENABLE_SCHEDULE_ANALYSIS: Final = True

# GitHub Models settings
GITHUB_MODELS_ENDPOINT: Final = "https://models.inference.ai.azure.com"
GITHUB_MODELS_AVAILABLE: Final = [
    "gpt-4o",
    "gpt-4o-mini",
]

# Service names
SERVICE_CHECK_AND_REMIND: Final = "check_and_remind"
SERVICE_CHAT: Final = "chat"
SERVICE_ANALYZE_SCHEDULE: Final = "analyze_schedule"
SERVICE_SUGGEST_TASK_TIME: Final = "suggest_task_time"

# Service parameters
ATTR_MESSAGE: Final = "message"
ATTR_TASK: Final = "task"
ATTR_RESPONSE: Final = "response"

# Data keys
DATA_COORDINATOR: Final = "coordinator"
DATA_AI_PROVIDER: Final = "ai_provider"
DATA_CONFIG: Final = "config"

# Update intervals
MIN_UPDATE_INTERVAL: Final = 30  # minutes
MAX_UPDATE_INTERVAL: Final = 240  # minutes

# Entity types to monitor
TODO_ENTITY_PREFIX: Final = "todo."
CALENDAR_ENTITY_PREFIX: Final = "calendar."

# Logging
LOGGER_NAME: Final = "ha_ai_assistant"
