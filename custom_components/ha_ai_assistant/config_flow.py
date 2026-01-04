"""Config flow for HA AI Assistant integration."""
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .ai_providers.github_models import GitHubModelsProvider
from .const import (
    AI_PROVIDER_GITHUB_MODELS,
    CONF_ACTIVE_HOURS_END,
    CONF_ACTIVE_HOURS_START,
    CONF_AI_PROVIDER,
    CONF_API_TOKEN,
    CONF_CHECK_INTERVAL,
    CONF_ENABLE_REMINDERS,
    CONF_ENABLE_SCHEDULE_ANALYSIS,
    CONF_MODEL,
    DEFAULT_ACTIVE_HOURS_END,
    DEFAULT_ACTIVE_HOURS_START,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_ENABLE_REMINDERS,
    DEFAULT_ENABLE_SCHEDULE_ANALYSIS,
    DEFAULT_MODEL_GITHUB,
    DOMAIN,
    GITHUB_MODELS_AVAILABLE,
    SUPPORTED_PROVIDERS,
)


class HAAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA AI Assistant."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the provider selection
            provider = user_input.get(CONF_AI_PROVIDER)
            
            if provider not in SUPPORTED_PROVIDERS:
                errors["base"] = "invalid_provider"
            else:
                # Store provider selection and move to provider config
                self.context["provider"] = provider
                return await self.async_step_provider_config()

        # Show provider selection form
        data_schema = vol.Schema({
            vol.Required(CONF_AI_PROVIDER, default=AI_PROVIDER_GITHUB_MODELS): vol.In(
                {
                    AI_PROVIDER_GITHUB_MODELS: "GitHub Models",
                }
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_provider_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the selected AI provider."""
        errors = {}
        provider = self.context.get("provider", AI_PROVIDER_GITHUB_MODELS)

        if user_input is not None:
            # Validate API token by testing connection
            api_token = user_input.get(CONF_API_TOKEN)
            
            if not api_token:
                errors["base"] = "missing_token"
            else:
                # Test the connection
                try:
                    if provider == AI_PROVIDER_GITHUB_MODELS:
                        test_provider = GitHubModelsProvider({
                            "api_token": api_token,
                            "model": user_input.get(CONF_MODEL, DEFAULT_MODEL_GITHUB),
                        })
                        # Try a simple test call
                        response = await test_provider.chat("Hello", context=None)
                        await test_provider.close()
                        
                        if response.startswith("Error:"):
                            errors["base"] = "auth_error"
                        else:
                            # Success - store config and move to options
                            self.context["provider_config"] = user_input
                            return await self.async_step_options()
                    
                except Exception as err:
                    errors["base"] = "connection_error"

        # Build schema based on provider
        if provider == AI_PROVIDER_GITHUB_MODELS:
            data_schema = vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(
                    CONF_MODEL,
                    default=DEFAULT_MODEL_GITHUB,
                ): vol.In(GITHUB_MODELS_AVAILABLE),
            })
        else:
            # Fallback for other providers
            data_schema = vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
            })

        return self.async_show_form(
            step_id="provider_config",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "provider": provider,
            },
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure integration options."""
        if user_input is not None:
            # Combine all configuration
            provider = self.context.get("provider")
            provider_config = self.context.get("provider_config", {})
            
            config_data = {
                CONF_AI_PROVIDER: provider,
                **provider_config,
                **user_input,
            }
            
            # Create the config entry
            return self.async_create_entry(
                title=f"HA AI Assistant ({provider})",
                data=config_data,
            )

        # Show options form
        data_schema = vol.Schema({
            vol.Optional(
                CONF_CHECK_INTERVAL,
                default=DEFAULT_CHECK_INTERVAL,
            ): vol.All(cv.positive_int, vol.Range(min=30, max=240)),
            vol.Optional(
                CONF_ACTIVE_HOURS_START,
                default=DEFAULT_ACTIVE_HOURS_START,
            ): vol.All(cv.positive_int, vol.Range(min=0, max=23)),
            vol.Optional(
                CONF_ACTIVE_HOURS_END,
                default=DEFAULT_ACTIVE_HOURS_END,
            ): vol.All(cv.positive_int, vol.Range(min=0, max=23)),
            vol.Optional(
                CONF_ENABLE_REMINDERS,
                default=DEFAULT_ENABLE_REMINDERS,
            ): cv.boolean,
            vol.Optional(
                CONF_ENABLE_SCHEDULE_ANALYSIS,
                default=DEFAULT_ENABLE_SCHEDULE_ANALYSIS,
            ): cv.boolean,
        })

        return self.async_show_form(
            step_id="options",
            data_schema=data_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return HAAssistantOptionsFlowHandler(config_entry)


class HAAssistantOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for HA AI Assistant."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current configuration
        current_config = {**self.config_entry.data, **self.config_entry.options}

        data_schema = vol.Schema({
            vol.Optional(
                CONF_CHECK_INTERVAL,
                default=current_config.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL),
            ): vol.All(cv.positive_int, vol.Range(min=30, max=240)),
            vol.Optional(
                CONF_ACTIVE_HOURS_START,
                default=current_config.get(
                    CONF_ACTIVE_HOURS_START, DEFAULT_ACTIVE_HOURS_START
                ),
            ): vol.All(cv.positive_int, vol.Range(min=0, max=23)),
            vol.Optional(
                CONF_ACTIVE_HOURS_END,
                default=current_config.get(
                    CONF_ACTIVE_HOURS_END, DEFAULT_ACTIVE_HOURS_END
                ),
            ): vol.All(cv.positive_int, vol.Range(min=0, max=23)),
            vol.Optional(
                CONF_ENABLE_REMINDERS,
                default=current_config.get(
                    CONF_ENABLE_REMINDERS, DEFAULT_ENABLE_REMINDERS
                ),
            ): cv.boolean,
            vol.Optional(
                CONF_ENABLE_SCHEDULE_ANALYSIS,
                default=current_config.get(
                    CONF_ENABLE_SCHEDULE_ANALYSIS, DEFAULT_ENABLE_SCHEDULE_ANALYSIS
                ),
            ): cv.boolean,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
