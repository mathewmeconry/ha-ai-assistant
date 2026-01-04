"""The HA AI Assistant integration."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .ai_providers import AIProviderBase, GitHubModelsProvider
from .const import (
    AI_PROVIDER_GITHUB_MODELS,
    ATTR_MESSAGE,
    ATTR_RESPONSE,
    ATTR_TASK,
    CONF_AI_PROVIDER,
    CONF_CHECK_INTERVAL,
    DATA_AI_PROVIDER,
    DATA_CONFIG,
    DATA_COORDINATOR,
    DEFAULT_CHECK_INTERVAL,
    DOMAIN,
    SERVICE_ANALYZE_SCHEDULE,
    SERVICE_CHAT,
    SERVICE_CHECK_AND_REMIND,
    SERVICE_SUGGEST_TASK_TIME,
)
from .coordinator import HAAssistantCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HA AI Assistant integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA AI Assistant from a config entry."""
    # Get configuration
    config = {**entry.data, **entry.options}
    
    # Create AI provider
    try:
        ai_provider = await _create_ai_provider(hass, config)
    except Exception as err:
        _LOGGER.error("Failed to create AI provider: %s", err)
        raise ConfigEntryNotReady(f"Failed to create AI provider: {err}")
    
    # Create coordinator
    check_interval = config.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL)
    update_interval = timedelta(minutes=check_interval)
    
    coordinator = HAAssistantCoordinator(
        hass,
        ai_provider,
        update_interval,
        config,
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator and provider
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_AI_PROVIDER: ai_provider,
        DATA_CONFIG: config,
    }
    
    # Register services
    await _async_register_services(hass, entry)
    
    # Set up platforms (if any in the future)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    if PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if not unload_ok:
            return False
    
    # Clean up AI provider
    data = hass.data[DOMAIN].pop(entry.entry_id)
    ai_provider = data[DATA_AI_PROVIDER]
    await ai_provider.close()
    
    # Unregister services if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_CHECK_AND_REMIND)
        hass.services.async_remove(DOMAIN, SERVICE_CHAT)
        hass.services.async_remove(DOMAIN, SERVICE_ANALYZE_SCHEDULE)
        hass.services.async_remove(DOMAIN, SERVICE_SUGGEST_TASK_TIME)
    
    return True


async def _create_ai_provider(
    hass: HomeAssistant, config: dict[str, Any]
) -> AIProviderBase:
    """Create AI provider instance based on configuration.
    
    Args:
        hass: Home Assistant instance
        config: Integration configuration
    
    Returns:
        AI provider instance
    
    Raises:
        ValueError: If provider type is unsupported
    """
    provider_type = config.get(CONF_AI_PROVIDER)
    
    if provider_type == AI_PROVIDER_GITHUB_MODELS:
        return GitHubModelsProvider(config)
    
    raise ValueError(f"Unsupported AI provider: {provider_type}")


async def _async_register_services(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Register integration services.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
    """
    # Only register services once (for the first entry)
    if hass.services.has_service(DOMAIN, SERVICE_CHECK_AND_REMIND):
        return
    
    async def handle_check_and_remind(call: ServiceCall) -> None:
        """Handle check_and_remind service call."""
        # Refresh all coordinators
        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data[DATA_COORDINATOR]
            await coordinator.async_request_refresh()
            
            # Get the analysis
            if coordinator.data and coordinator.data.get("analysis"):
                _LOGGER.info("AI Analysis: %s", coordinator.data["analysis"])
                # Fire event with the analysis
                hass.bus.async_fire(
                    f"{DOMAIN}_reminder",
                    {"analysis": coordinator.data["analysis"]},
                )
    
    async def handle_chat(call: ServiceCall) -> None:
        """Handle chat service call."""
        message = call.data.get(ATTR_MESSAGE)
        
        if not message:
            _LOGGER.error("No message provided for chat service")
            return
        
        # Use the first available coordinator
        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data[DATA_COORDINATOR]
            response = await coordinator.async_chat(message)
            
            _LOGGER.info("Chat response: %s", response)
            
            # Fire event with response
            hass.bus.async_fire(
                f"{DOMAIN}_chat_response",
                {ATTR_MESSAGE: message, ATTR_RESPONSE: response},
            )
            
            # Set service response
            call.async_set_response({ATTR_RESPONSE: response})
            return
    
    async def handle_analyze_schedule(call: ServiceCall) -> None:
        """Handle analyze_schedule service call."""
        # Use the first available coordinator
        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data[DATA_COORDINATOR]
            analysis = await coordinator.async_analyze_schedule()
            
            _LOGGER.info("Schedule analysis: %s", analysis)
            
            # Fire event with analysis
            hass.bus.async_fire(
                f"{DOMAIN}_schedule_analysis",
                {"analysis": analysis},
            )
            
            # Set service response
            call.async_set_response({ATTR_RESPONSE: analysis})
            return
    
    async def handle_suggest_task_time(call: ServiceCall) -> None:
        """Handle suggest_task_time service call."""
        task = call.data.get(ATTR_TASK)
        
        if not task:
            _LOGGER.error("No task provided for suggest_task_time service")
            return
        
        # Use the first available coordinator
        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data[DATA_COORDINATOR]
            suggestion = await coordinator.async_suggest_task_time(task)
            
            _LOGGER.info("Task time suggestion: %s", suggestion)
            
            # Fire event with suggestion
            hass.bus.async_fire(
                f"{DOMAIN}_task_suggestion",
                {ATTR_TASK: task, ATTR_RESPONSE: suggestion},
            )
            
            # Set service response
            call.async_set_response({ATTR_RESPONSE: suggestion})
            return
    
    # Register all services
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHECK_AND_REMIND,
        handle_check_and_remind,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHAT,
        handle_chat,
        supports_response=True,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_ANALYZE_SCHEDULE,
        handle_analyze_schedule,
        supports_response=True,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUGGEST_TASK_TIME,
        handle_suggest_task_time,
        supports_response=True,
    )
