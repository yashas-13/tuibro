# Tuibro

**AI-controlled browser browsing from your terminal.**

Tuibro is a TUI (Terminal User Interface) application with an embedded Chromium browser controlled by an AI agent. It features a split-screen layout with a chat interface on the left and a live DOM/a11y tree view of the browser on the right.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TUIBRO ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐  ┌───────────────────────────────────┐    │
│  │    CHAT PANE         │  │        BROWSER PANE               │    │
│  │                      │  │                                   │    │
│  │  🔵 User: task...   │  │  URL: https://google.com         │    │
│  │  🤖 Agent: done...  │  │  [Document] root                  │    │
│  │  → action logs      │  │    [search] "Python..." [→click] │    │
│  │                      │  │    [btn] "Google Search" [→click]│    │
│  │                      │  │                                   │    │
│  ├──────────────────────┤  │  Status: Ready | Elements: 12    │    │
│  │ > input...           │  │  Last action: click #3           │    │
│  └──────────────────────┘  └───────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Provider: openai | Model: gpt-4o | [F1]Help [F2]Provider   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

- **Embedded Browser**: Headless Chromium controlled via Playwright
- **AI Agent**: Autonomous browsing with tool-calling (navigate, click, type, scroll)
- **Split Screen**: Chat + browser DOM view
- **11 LLM Providers**: OpenAI, Anthropic, Google, Groq, Mistral, Cohere, Together, Ollama, LM Studio, vLLM, OpenRouter
- **Android Optimized**: Tuned for Termux/proot on Android devices
- **Minimal Dependencies**: Just `playwright` + `httpx`

## Quick Start

```bash
# Setup
bash setup.sh

# Set your API key
export TUIBRO_OPENAI_API_KEY=sk-...

# Run
python3 main.py

# With a task
python3 main.py --task "Search Google for Python web scraping tutorials"
```

## Usage

### Commands (inside TUI)

| Key/Command | Action |
|-------------|--------|
| `Tab` | Switch between chat and browser panes |
| `Enter` | Send message / command |
| `F1` | Show help |
| `F2` | Cycle through LLM providers |
| `F3` | Cycle through models |
| `F4` | Clear chat |
| `Ctrl+C` | Stop agent / Quit |

### Chat Commands

| Command | Description |
|---------|-------------|
| `/url <URL>` | Navigate to URL |
| `/google <query>` | Quick Google search |
| `/bing <query>` | Quick Bing search |
| `help` | Show available commands |
| `providers` | List available providers |
| `model` | Show current model |
| `clear` | Clear chat history |

### CLI Options

```bash
python3 main.py [OPTIONS]

Options:
  --provider NAME    LLM provider (default: openai)
  --model NAME       Model name (default: gpt-4o)
  --task TEXT         Task for autonomous agent
  --debug             Enable debug logging
  --no-headless       Show browser window
  --max-iterations N  Max agent iterations (default: 20)
```

## Supported Providers

| Provider | Models | Notes |
|----------|--------|-------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo | Requires API key |
| Anthropic | claude-sonnet-4-20250514, claude-3-5-sonnet-20241022 | Requires API key |
| Google | gemini-2.0-flash, gemini-1.5-pro | Requires API key |
| Groq | llama-3.3-70b-versatile, mixtral-8x7b | Requires API key |
| Mistral | mistral-large-latest, codestral-latest | Requires API key |
| Cohere | command-r-plus, command-r | Requires API key |
| Together | llama-3.1-70b, mixtral-8x7b | Requires API key |
| Ollama | llama3.1, mistral, codellama | Local, no API key |
| LM Studio | local-model | Local, no API key |
| vLLM | local-model | Local, no API key |
| OpenRouter | Multi-model | Requires API key |

## Architecture

- **TUI**: Python `curses` — split-pane layout with real-time DOM rendering
- **Browser**: Playwright + headless Chromium — full web capabilities
- **Agent**: LLM tool-calling loop — observe → think → act → render
- **Providers**: Raw HTTP via `httpx` — minimal dependencies

## Requirements

- Python 3.10+
- Playwright (installs Chromium automatically)
- httpx
- ~500MB disk for Chromium
- ~2GB RAM for browser + agent
