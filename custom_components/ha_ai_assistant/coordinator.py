"""Data update coordinator for HA AI Assistant."""
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import EVENT_END, EVENT_START, EVENT_SUMMARY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .ai_providers.base import AIProviderBase
from .const import (
    CALENDAR_ENTITY_PREFIX,
    DOMAIN,
    TODO_ENTITY_PREFIX,
)

_LOGGER = logging.getLogger(__name__)


class HAAssistantCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates for HA AI Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        ai_provider: AIProviderBase,
        update_interval: timedelta,
        config: dict[str, Any],
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            ai_provider: AI provider instance
            update_interval: How often to update data
            config: Integration configuration
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.ai_provider = ai_provider
        self.config = config

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Home Assistant.
        
        Returns:
            Dictionary containing todos, calendar events, and AI analysis
        """
        try:
            # Check if we're within active hours
            if not self._is_active_hours():
                _LOGGER.debug("Outside active hours, skipping update")
                return {
                    "todos": [],
                    "calendar_events": [],
                    "analysis": None,
                    "last_update": dt_util.now(),
                    "active": False,
                }

            # Fetch todo items
            todos = await self._fetch_todos()
            
            # Fetch calendar events
            calendar_events = await self._fetch_calendar_events()
            
            # Build context for AI analysis
            context = {
                "current_time": dt_util.now(),
                "todos": todos,
                "calendar_events": calendar_events,
                "user_preferences": {
                    "active_hours_start": self.config.get("active_hours_start", 7),
                    "active_hours_end": self.config.get("active_hours_end", 23),
                },
            }
            
            # Get AI analysis if enabled
            analysis = None
            if self.config.get("enable_reminders", True):
                try:
                    ai_response = await self.ai_provider.analyze_context(context)
                    if ai_response.error:
                        _LOGGER.error("AI analysis error: %s", ai_response.error)
                    else:
                        analysis = ai_response.content
                except Exception as err:
                    _LOGGER.error("Error getting AI analysis: %s", err)
            
            return {
                "todos": todos,
                "calendar_events": calendar_events,
                "analysis": analysis,
                "last_update": dt_util.now(),
                "active": True,
            }
            
        except Exception as err:
            _LOGGER.error("Error updating coordinator data: %s", err)
            raise UpdateFailed(f"Error communicating with Home Assistant: {err}")

    def _is_active_hours(self) -> bool:
        """Check if current time is within configured active hours.
        
        Returns:
            True if within active hours, False otherwise
        """
        now = dt_util.now()
        current_hour = now.hour
        
        start_hour = self.config.get("active_hours_start", 7)
        end_hour = self.config.get("active_hours_end", 23)
        
        return start_hour <= current_hour < end_hour

    async def _fetch_todos(self) -> list[dict[str, Any]]:
        """Fetch all todo items from Home Assistant.
        
        Returns:
            List of todo items with their details
        """
        todos = []
        
        # Get all todo entities
        states = self.hass.states.async_all(TODO_ENTITY_PREFIX.rstrip('.'))
        
        for state in states:
            if not state.entity_id.startswith(TODO_ENTITY_PREFIX):
                continue
                
            # Get todo list items
            try:
                # Call the todo list service to get items
                response = await self.hass.services.async_call(
                    "todo",
                    "get_items",
                    {"entity_id": state.entity_id},
                    blocking=True,
                    return_response=True,
                )
                
                if response and state.entity_id in response:
                    items = response[state.entity_id].get("items", [])
                    for item in items:
                        todos.append({
                            "summary": item.get("summary", ""),
                            "completed": item.get("status") == "completed",
                            "due": item.get("due"),
                            "entity_id": state.entity_id,
                            "uid": item.get("uid"),
                        })
            except Exception as err:
                _LOGGER.warning("Error fetching todos from %s: %s", state.entity_id, err)
                continue
        
        return todos

    async def _fetch_calendar_events(self) -> list[dict[str, Any]]:
        """Fetch upcoming calendar events from Home Assistant.
        
        Returns:
            List of calendar events
        """
        events = []
        now = dt_util.now()
        end_time = now + timedelta(days=7)  # Look ahead 7 days
        
        # Get all calendar entities
        states = self.hass.states.async_all(CALENDAR_ENTITY_PREFIX.rstrip('.'))
        
        for state in states:
            if not state.entity_id.startswith(CALENDAR_ENTITY_PREFIX):
                continue
                
            try:
                # Call the calendar service to get events
                response = await self.hass.services.async_call(
                    "calendar",
                    "get_events",
                    {
                        "entity_id": state.entity_id,
                        "start_date_time": now.isoformat(),
                        "end_date_time": end_time.isoformat(),
                    },
                    blocking=True,
                    return_response=True,
                )
                
                if response and state.entity_id in response:
                    calendar_events = response[state.entity_id].get("events", [])
                    for event in calendar_events:
                        events.append({
                            "summary": event.get(EVENT_SUMMARY, event.get("summary", "")),
                            "start": event.get(EVENT_START, event.get("start")),
                            "end": event.get(EVENT_END, event.get("end")),
                            "entity_id": state.entity_id,
                            "description": event.get("description"),
                        })
            except Exception as err:
                _LOGGER.warning("Error fetching events from %s: %s", state.entity_id, err)
                continue
        
        # Sort events by start time
        events.sort(key=lambda x: x.get("start", ""))
        
        return events

    async def async_chat(self, message: str) -> str:
        """Send a chat message to the AI provider.
        
        Args:
            message: User's message
        
        Returns:
            AI's response
        """
        # Build current context
        context = {
            "current_time": dt_util.now(),
            "todos": self.data.get("todos", []) if self.data else [],
            "calendar_events": self.data.get("calendar_events", []) if self.data else [],
        }
        
        return await self.ai_provider.chat(message, context)

    async def async_analyze_schedule(self) -> str:
        """Get AI analysis of the schedule.
        
        Returns:
            Schedule analysis
        """
        # Build current context
        context = {
            "current_time": dt_util.now(),
            "todos": self.data.get("todos", []) if self.data else [],
            "calendar_events": self.data.get("calendar_events", []) if self.data else [],
        }
        
        response = await self.ai_provider.analyze_schedule(context)
        if response.error:
            return f"Error: {response.error}"
        return response.content

    async def async_suggest_task_time(self, task: str) -> str:
        """Ask AI to suggest time for a task.
        
        Args:
            task: Task description
        
        Returns:
            Time suggestion
        """
        # Build current context
        context = {
            "current_time": dt_util.now(),
            "todos": self.data.get("todos", []) if self.data else [],
            "calendar_events": self.data.get("calendar_events", []) if self.data else [],
        }
        
        response = await self.ai_provider.suggest_task_time(task, context)
        if response.error:
            return f"Error: {response.error}"
        return response.content
