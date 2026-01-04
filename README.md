# HA AI Assistant

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

AI-powered Home Assistant integration for personal organization and reducing spontaneity.

## What It Does

HA AI Assistant is your personal organization coach that helps you:

- 📋 **Analyze your todo lists and calendar** - Get AI-powered insights about your tasks and schedule
- ⏰ **Receive smart reminders** - Get context-aware reminders at the right time
- 🎯 **Reduce spontaneity** - AI coaching to help you plan ahead and avoid impulsive decisions
- 📅 **Optimize task scheduling** - Get suggestions for when to complete specific tasks
- 🔍 **Identify conflicts and gaps** - Spot scheduling issues before they become problems
- 💬 **Chat interface** - Ask your assistant questions about your schedule anytime

The integration is specifically designed to help you be more organized and less spontaneous by providing proactive analysis and suggestions based on your Home Assistant todo lists and calendar entities.

## Features

### Current Features (v0.1.0)

✅ **AI Provider Support**
- GitHub Models integration (GPT-4o, GPT-4o-mini)
- Extensible architecture for adding more providers

✅ **Core Services**
- `check_and_remind` - Manual trigger for reminders and analysis
- `chat` - Interactive chat with your AI assistant
- `analyze_schedule` - Get detailed schedule analysis
- `suggest_task_time` - Ask AI when to schedule tasks

✅ **Smart Scheduling**
- Configurable check intervals (30-240 minutes)
- Active hours configuration (e.g., 7 AM - 11 PM)
- Automatic context gathering from todo lists and calendars

✅ **Easy Configuration**
- Simple UI-based setup (no YAML required)
- Configure AI provider, check intervals, and active hours
- Enable/disable features as needed

### Roadmap

🔜 Additional AI providers (OpenAI, Anthropic, local LLMs)
🔜 Learning from user patterns
🔜 More sophisticated scheduling algorithms
🔜 Template sensors for statistics
🔜 Mobile notifications integration
🔜 Voice assistant integration

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/mathewmeconry/ha-ai-assistant`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the HA AI Assistant card
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/ha_ai_assistant` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click "Add Integration"
5. Search for "HA AI Assistant"

## Configuration

### Getting Started

1. **Get a GitHub Models API Token**
   - Go to [github.com/settings/tokens](https://github.com/settings/tokens)
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name (e.g., "Home Assistant AI")
   - No specific scopes are required for GitHub Models
   - Click "Generate token" and copy it immediately

2. **Add the Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "HA AI Assistant"
   - Select "GitHub Models" as your AI provider
   - Enter your API token
   - Choose your model (gpt-4o-mini is recommended for cost-effectiveness)

3. **Configure Options**
   - **Check Interval**: How often to check for reminders (30-240 minutes)
   - **Active Hours**: When the assistant should be active (e.g., 7 AM - 11 PM)
   - **Enable Reminders**: Toggle automatic reminder checks
   - **Enable Schedule Analysis**: Toggle schedule analysis features

### Configuration Options Explained

| Option | Description | Default | Range |
|--------|-------------|---------|-------|
| AI Provider | Which AI service to use | GitHub Models | GitHub Models (more coming) |
| API Token | Your API authentication token | - | Required |
| Model | Which AI model to use | gpt-4o-mini | gpt-4o, gpt-4o-mini |
| Check Interval | How often to run analysis (minutes) | 60 | 30-240 |
| Active Hours Start | When to start daily checks | 7 AM | 0-23 |
| Active Hours End | When to stop daily checks | 11 PM | 0-23 |
| Enable Reminders | Automatic reminder checks | Yes | Yes/No |
| Enable Schedule Analysis | Schedule analysis features | Yes | Yes/No |

## Usage

### Services

The integration provides four main services:

#### `ha_ai_assistant.check_and_remind`

Manually trigger a check for reminders and get AI analysis.

```yaml
service: ha_ai_assistant.check_and_remind
```

The analysis is returned via the `ha_ai_assistant_reminder` event.

#### `ha_ai_assistant.chat`

Send a message to your AI assistant and get a response.

```yaml
service: ha_ai_assistant.chat
data:
  message: "What should I focus on today?"
```

Returns a response that can be used in automations or notifications.

#### `ha_ai_assistant.analyze_schedule`

Get AI analysis of your upcoming schedule.

```yaml
service: ha_ai_assistant.analyze_schedule
```

Returns detailed analysis of conflicts, gaps, and workload.

#### `ha_ai_assistant.suggest_task_time`

Ask AI when to schedule a specific task.

```yaml
service: ha_ai_assistant.suggest_task_time
data:
  task: "Review and respond to emails"
```

Returns time suggestions based on your current schedule.

### Example Automations

See the [examples/automations.yaml](examples/automations.yaml) file for complete examples. Here are some highlights:

**Hourly reminder check:**
```yaml
automation:
  - alias: "AI Assistant: Hourly Check"
    trigger:
      - platform: time_pattern
        hours: "/1"
    condition:
      - condition: time
        after: "07:00:00"
        before: "23:00:00"
    action:
      - service: ha_ai_assistant.check_and_remind
```

**Morning briefing:**
```yaml
automation:
  - alias: "AI Assistant: Morning Briefing"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: ha_ai_assistant.analyze_schedule
        response_variable: schedule_analysis
      - service: notify.notify
        data:
          title: "Good Morning! Here's your day ahead:"
          message: "{{ schedule_analysis.response }}"
```

**Evening review:**
```yaml
automation:
  - alias: "AI Assistant: Evening Review"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: ha_ai_assistant.check_and_remind
```

More examples available in [examples/automations.yaml](examples/automations.yaml).

### Dashboard Integration

See [examples/dashboard.yaml](examples/dashboard.yaml) for a complete dashboard example with:
- Chat interface
- Task scheduling helper
- Quick actions
- Todo list integration
- Calendar view
- Configuration guides

## How It Helps Reduce Spontaneity

The AI assistant is specifically prompted to help you:

1. **Plan Ahead**: Encourages reviewing and planning your schedule
2. **Complete Existing Tasks**: Reminds you to finish pending work before starting new tasks
3. **Identify Long-Pending Items**: Highlights tasks that have been waiting too long
4. **Suggest Breaking Down Tasks**: Helps make large tasks more manageable
5. **Spot Conflicts**: Identifies scheduling conflicts before they cause issues
6. **Optimize Time Usage**: Suggests better times for tasks based on your schedule
7. **Stay Focused**: Provides supportive reminders to keep you on track

The system prompt specifically instructs the AI to discourage impulsive decisions and encourage organization.

## Requirements

- Home Assistant 2024.1 or newer
- Python 3.11 or newer
- At least one todo list entity (`todo.*`)
- At least one calendar entity (`calendar.*`) - optional but recommended
- GitHub account with API access (for GitHub Models provider)

## Privacy & Data

- All API calls are made directly from your Home Assistant instance to the AI provider
- Your todo and calendar data is sent to the AI provider for analysis
- API tokens are stored securely in Home Assistant's config entries
- No data is stored or logged by this integration beyond Home Assistant's normal logging

**Important**: Your todo items and calendar events will be sent to the AI provider (GitHub Models/OpenAI) for analysis. Make sure you're comfortable with this before using the integration.

## Troubleshooting

### Integration Won't Load

- Check Home Assistant logs for errors
- Verify your API token is correct
- Ensure you have todo or calendar entities available

### No Analysis or Responses

- Check that you're within active hours
- Verify reminders are enabled in configuration
- Check the Home Assistant logs for AI API errors
- Ensure your API token has not expired

### API Errors

- GitHub Models: Verify your token at [github.com/settings/tokens](https://github.com/settings/tokens)
- Check your API rate limits
- Ensure the selected model is available

### Getting Better Responses

- Use descriptive names for your todo items
- Add due dates to tasks when possible
- Keep your calendar up to date
- Be specific in chat messages
- Use the chat service to ask follow-up questions

## Development

### Adding New AI Providers

See [custom_components/ha_ai_assistant/ai_providers/README.md](custom_components/ha_ai_assistant/ai_providers/README.md) for detailed instructions on adding new AI providers.

The architecture is designed to be extensible - you just need to:
1. Create a new provider class inheriting from `AIProviderBase`
2. Implement the required methods
3. Update the config flow
4. Add to the provider factory

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Project Structure

```
custom_components/ha_ai_assistant/
├── __init__.py              # Integration setup and service registration
├── manifest.json            # Integration metadata
├── config_flow.py          # Configuration UI
├── const.py                # Constants and configuration keys
├── coordinator.py          # Data coordinator for todo/calendar
├── services.yaml           # Service definitions
└── ai_providers/           # AI provider implementations
    ├── __init__.py
    ├── base.py             # Abstract base class
    ├── github_models.py    # GitHub Models implementation
    └── README.md           # Provider development guide
```

## Support

- 🐛 [Report bugs](https://github.com/mathewmeconry/ha-ai-assistant/issues)
- 💡 [Request features](https://github.com/mathewmeconry/ha-ai-assistant/issues)
- 📖 [Read the docs](https://github.com/mathewmeconry/ha-ai-assistant)
- 💬 [Discussions](https://github.com/mathewmeconry/ha-ai-assistant/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for [Home Assistant](https://www.home-assistant.io/)
- Uses [GitHub Models](https://github.com/marketplace/models) for AI capabilities
- Inspired by the need for better personal organization tools

---

**Made with ❤️ for the Home Assistant community**

[releases-shield]: https://img.shields.io/github/release/mathewmeconry/ha-ai-assistant.svg
[releases]: https://github.com/mathewmeconry/ha-ai-assistant/releases
[license-shield]: https://img.shields.io/github/license/mathewmeconry/ha-ai-assistant.svg
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg