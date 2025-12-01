# Dota Imba Macro Tool

A macro tool for Dota Imba with custom skill casting features.

## Features

### Quick-Cast
Instantly cast skills at your cursor position. When enabled, pressing a skill hotkey will immediately cast the skill without requiring a separate click.

### Auto-Cast
Automatically press skill hotkeys at specified intervals. Useful for skills that need to be spammed or cast repeatedly.

### Custom Macros
Create your own key sequences with:
- Key presses
- Key holds
- Mouse clicks
- Delays
- Key combos

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python main.py
```

### Using the GUI
1. **Quick-Cast Tab**: Enable/disable quick-cast and configure skill hotkeys
2. **Auto-Cast Tab**: Add skills to auto-cast with custom intervals
3. **Macros Tab**: Create custom macros with multiple actions
4. **Settings Tab**: Configure global toggle hotkey and other settings

### Hotkeys
- Default toggle hotkey: `F9` (toggles macro engine on/off)
- Configure skill hotkeys in the Quick-Cast tab

## Configuration

Settings are stored in `~/.macro_imba/config.yaml` and saved automatically when you close the application.

### Example Configuration
```yaml
quick_cast:
  enabled: true
  hotkeys:
    skill_1: q
    skill_2: w
    skill_3: e
    skill_4: r
    skill_5: d
    skill_6: f

auto_cast:
  enabled: false
  skills:
    - hotkey: q
      interval_ms: 100
  interval_ms: 100

macros:
  - name: combo_1
    hotkey: x
    actions:
      - type: key_press
        key: q
      - type: delay
        delay_ms: 50
      - type: key_press
        key: w

global_hotkey: f9
toggle_enabled: true
```

## Macro Action Types

| Type | Description | Parameters |
|------|-------------|------------|
| `key_press` | Press and release a key | `key`: The key to press |
| `key_hold` | Hold a key for a duration | `key`: The key, `duration_ms`: Hold time |
| `mouse_click` | Click a mouse button | `button`: "left" or "right" |
| `delay` | Wait before next action | `delay_ms`: Delay in milliseconds |
| `combo` | Press multiple keys together | `keys`: List of keys to press |

## Requirements

- Python 3.8+
- pynput
- keyboard
- PyQt5
- pywin32 (Windows only)
- pyyaml

## License

MIT License
