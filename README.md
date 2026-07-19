<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-1.45+-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Platform-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Version-0.1.0-orange?style=for-the-badge" alt="v0.1.0">
</p>

<h1 align="center">
  <br>
  🌐 Tuibro
  <br>
  <sub>Your AI browsing agent — lives in your terminal, controls a real browser</sub>
</h1>

<p align="center">
  <b>Tell it what you need. It browses the web for you.</b><br>
  <sub>Click, type, scroll, navigate — all autonomous, all visible in real-time.</sub>
</p>

<p align="center">
  <a href="#-what-is-tuibro">What is this?</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-screenshot">Screenshot</a> •
  <a href="#-features">Features</a> •
  <a href="#-supported-providers">Providers</a> •
  <a href="#-how-it-works">How it works</a> •
  <a href="#-keyboard-shortcuts">Shortcuts</a> •
  <a href="#-install">Install</a>
</p>

---

## 🤔 What is Tuibro?

Imagine you could say *"find me the cheapest flight to Tokyo next week"* and watch an AI agent open Google Flights, search dates, compare prices, and hand you the answer — all from a split-screen in your terminal.

**That's Tuibro.**

It's a **terminal-based browser agent** that gives an AI model full control of a real Chromium browser. You type a task on the left side of your screen. On the right side, you watch the agent navigate websites, click buttons, fill forms, and extract data — step by step, in real-time.

No browser extension. No cloud service. No JavaScript injection. A **real browser** that the AI controls directly, running right on your Android device (or any Linux machine).

### Why does this exist?

Most AI browser tools are either:
- **Cloud-only** (you don't see what's happening)
- **Browser extensions** (limited to what Chrome allows)
- **Desktop-only** (can't run on mobile)

Tuibro is different:
- **Runs in your terminal** — works on Android via Termux/proot
- **Fully transparent** — you see every action as it happens
- **Real browser** — not a simulation, actual Chromium with Playwright
- **Your data stays local** — no third-party servers, no data collection
- **12 LLM providers** — use whatever model you prefer

---

## 📸 Screenshot

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [0:NewTab]  [1:Google Search ◄]  [2:Bing]                                  (chat)      │
├─────────────────────┬──────────────────────────────────┬─────────────────────────────────┤
│  💬 Chat             │  🌐 Browser                       │  📊 Activity                    │
│                     │                                  │                                 │
│ You: Search Google  │  Tab: [1/3] python tutorials     │  URL: google.com/search?q=py.. │
│  for Python         │  URL: https://www.google.com/    │  Scroll: 0% | Elements: 12     │
│  tutorials          │  Title: python tutorials -       │  ─────────────────────────      │
│                     │         Google Search             │  Activity Log:                  │
│ Agent: I'll find    │  Interactive elements:            │                                 │
│  the best free      │   [0] searchbox: Search [FOCUSED]│  06:33:06 · Browser started     │
│  resources for      │   [1] button: Google Search      │  06:33:11 → → google.com       │
│  you.               │   [2] link: Python.org           │  06:33:16 👆 Click [0] Search  │
│                     │   [3] link: Real Python          │  06:33:18 ⌨ Type: python tut.. │
│ → navigate(google)  │   [4] link: W3Schools Python     │  06:33:21 👆 Click [1] Search  │
│ → click(0) Search   │   [5] link: freeCodeCamp         │  06:33:24 ＋ Tab 1 opened      │
│ → type(0, python)   │                                  │  06:33:26 ⇄ Switched to tab 0  │
│ → click(1) Search   │  Last: Click [1] Google Search   │  06:33:28 📋 Extracted 12 links│
│                     │                                  │                                 │
│ Agent: Found great  │                                  │                                 │
│  results!           │                                  │                                 │
├─────────────────────┴──────────────────────────────────┴─────────────────────────────────┤
│ Provider: 9router │ Model: oc │ Agent: Running iter 3/20                                │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Features

### 🧠 AI-Powered Browsing
The agent doesn't just open pages — it **understands** them. It reads the accessibility tree, identifies interactive elements by index, and makes intelligent decisions about what to click, type, or extract next.

### 📑 Tab Management
Open multiple tabs, switch between them, close the ones you don't need — just like a real browser, but controlled by the AI. The tab bar at the top shows all open tabs with the active one highlighted.

### 🎯 Full DOM Control
The agent has 21 tools at its disposal:

| Category | Tools |
|----------|-------|
| **Navigation** | `navigate`, `go_back`, `go_forward` |
| **Tabs** | `new_tab`, `close_tab`, `switch_tab`, `list_tabs` |
| **Interaction** | `click`, `type_text`, `select_option`, `scroll`, `wait` |
| **DOM Extraction** | `get_element_text`, `get_element_attribute`, `evaluate_js`, `get_page_html` |
| **Data Collection** | `get_all_links`, `get_all_forms`, `get_cookies`, `set_local_storage` |
| **Complete** | `done` (with final answer) |

### 📊 Real-Time Activity Pane
The third pane shows a live feed of every action the agent takes — timestamped and icon-coded:

| Icon | Meaning |
|------|---------|
| `→` | Navigation |
| `👆` | Click |
| `⌨` | Typing |
| `＋` | New tab opened |
| `⇄` | Tab switch |
| `📋` | Data extraction |
| `⚙` | JavaScript evaluation |
| `✗` | Error |

### 🔀 12 LLM Providers
Use any model from any provider. The `oc` combo model on 9router auto-routes to the best available:

| Provider | Default Model | Notes |
|----------|--------------|-------|
| **9router** | `oc` | 464+ models, auto-routing combo |
| **OpenAI** | `gpt-4o` | Best for complex browsing tasks |
| **Anthropic** | `claude-sonnet-4-20250514` | Strong at following instructions |
| **Google** | `gemini-2.0-flash` | Fast multimodal reasoning |
| **Groq** | `llama-3.3-70b-versatile` | Ultra-fast inference |
| **Mistral** | `mistral-large-latest` | Good balance of speed/quality |
| **Cohere** | `command-r-plus` | Strong at search tasks |
| **Together** | `llama-3.1-70b` | Open-source models |
| **Ollama** | `llama3.1` | Local, no API key needed |
| **LM Studio** | `local-model` | Local with UI |
| **vLLM** | `local-model` | High-throughput local serving |
| **OpenRouter** | `openai/gpt-4o` | Multi-model gateway |

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repo
git clone https://github.com/yashas-13/tuibro.git
cd tuibro

# Install dependencies + Chromium
bash setup.sh

# Or install manually
pip install -e .
python3 -m playwright install chromium
```

### 2. Configure

```bash
# Option A: Set API key via CLI
tuibro keys set openai sk-your-key-here

# Option B: Set via environment variable
export TUIBRO_OPENAI_API_KEY=sk-your-key-here

# Option C: Use 9router (464+ models, one key)
tuibro keys set 9router sk_9router
```

### 3. Run

```bash
# Interactive mode (just like Codex CLI)
tuibro

# With a specific task
tuibro run "Search Google for Python web scraping tutorials"

# With a different provider
tuibro -p anthropic -m claude-sonnet-4-20250514

# Direct browser (no agent)
tuibro browser -n google.com
```

---

## 🎮 How It Works

```
  You type a task
       │
       ▼
  ┌─────────────────────────────────────────┐
  │  Agent (LLM) sees the page state:       │
  │  - URL, title, scroll position          │
  │  - List of interactive elements         │
  │  - Element indices: [0], [1], [2]...    │
  │                                          │
  │  Agent decides: "click element [3]"     │
  └─────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────┐
  │  Browser executes the action:           │
  │  - Clicks the element                   │
  │  - Waits for page to load               │
  │  - Extracts new page state              │
  │  - Logs the event to activity pane      │
  └─────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────┐
  │  Agent observes the result:             │
  │  - New page loaded: "Search Results"    │
  │  - New elements available               │
  │  - Decides next action                  │
  │  - Repeats until task is done           │
  └─────────────────────────────────────────┘
       │
       ▼
  Agent reports final answer in chat
```

The whole loop runs autonomously. You can watch it work, or let it run in the background with `--task`.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Cycle focus between Chat / Browser / Activity panes |
| `Enter` | Send message (in Chat pane) |
| `F1` | Show help overlay |
| `F2` | Cycle through LLM providers |
| `F3` | Cycle through models |
| `F4` | Clear chat history |
| `F5` | Toggle activity pane on/off |
| `F6` | Open new browser tab |
| `F7` | Close current tab |
| `Ctrl+C` | Stop agent / Quit |

### Chat Commands

| Command | Description |
|---------|-------------|
| `/url <URL>` | Navigate to a URL directly |
| `/google <query>` | Quick Google search |
| `/bing <query>` | Quick Bing search |
| `/tab <N>` | Switch to tab N |
| `/newtab [URL]` | Open a new tab |
| `/closetab` | Close current tab |
| `help` | Show all commands |
| `providers` | List available providers |
| `status` | Show agent and browser status |
| `tabs` | List all open tabs |
| `clear` | Clear chat |

---

## 📁 Project Structure

```
tuibro/
├── main.py                          # Entry point
├── pyproject.toml                   # Package config + CLI entry point
├── setup.sh                         # One-command setup script
├── requirements.txt                 # Dependencies (just 2!)
│
├── tuibro/
│   ├── cli.py                       # CLI with subcommands (like Codex)
│   ├── app.py                       # Main app — orchestrates everything
│   ├── config.py                    # Config management + API key storage
│   ├── preview.py                   # Text preview for non-TTY environments
│   │
│   ├── browser/
│   │   ├── engine.py                # Playwright browser + tabs + events
│   │   ├── actions.py               # 21 tool definitions + execution
│   │   ├── dom.py                   # Accessibility tree parser
│   │   └── renderer.py              # DOM → terminal text renderer
│   │
│   ├── agent/
│   │   ├── core.py                  # Agent loop: observe → think → act
│   │   ├── prompts.py               # System prompts for browsing
│   │   └── providers/               # 12 LLM providers
│   │       ├── base.py              # Abstract provider interface
│   │       ├── openai.py            # OpenAI
│   │       ├── anthropic.py         # Anthropic Claude
│   │       ├── google.py            # Google Gemini
│   │       ├── groq.py              # Groq (fast)
│   │       ├── mistral.py           # Mistral
│   │       ├── cohere.py            # Cohere
│   │       ├── together.py          # Together AI
│   │       ├── ollama.py            # Ollama (local)
│   │       ├── lmstudio.py          # LM Studio (local)
│   │       ├── vllm.py              # vLLM (local)
│   │       ├── openrouter.py        # OpenRouter
│   │       └── ninerouter.py        # 9router (464+ models)
│   │
│   ├── tui/
│   │   ├── layout.py                # Split-pane layout manager
│   │   ├── chat_pane.py             # Chat interface
│   │   ├── browser_pane.py          # Browser DOM + activity view
│   │   ├── status_bar.py            # Bottom status bar
│   │   └── theme.py                 # Colors + Unicode characters
│   │
│   └── utils/
│       ├── keys.py                  # API key storage
│       └── logger.py                # Debug logging
```

---

## 🔧 CLI Reference

```bash
# ── Main Commands ──────────────────────────────────────
tuibro                                # Interactive TUI mode
tuibro run "task description"         # Run with a specific task
tuibro setup                          # First-time setup (deps + Chromium)

# ── Configuration ──────────────────────────────────────
tuibro config show                    # Show current config
tuibro config get model               # Get a specific value
tuibro config set model gpt-4o-mini   # Change a setting
tuibro config set provider anthropic  # Switch provider

# ── API Keys ───────────────────────────────────────────
tuibro keys show                      # Show configured keys (masked)
tuibro keys set openai sk-...         # Save a key
tuibro keys remove openai             # Remove a key
tuibro keys list                      # List all providers with keys

# ── Providers ──────────────────────────────────────────
tuibro providers                      # List all providers + models
tuibro providers openai               # Show details for a provider
tuibro providers 9router              # Show 9router models

# ── Browser (no agent) ─────────────────────────────────
tuibro browser -n google.com          # Navigate to URL
tuibro browser --js "document.title"  # Execute JavaScript

# ── Global Options ─────────────────────────────────────
--provider, -p    LLM provider (default: 9router)
--model, -m       Model name (default: oc)
--debug, -d       Enable debug logging
--version, -v     Show version
```

---

## 📱 Android Setup

Tuibro is optimized for Android through Termux/proot:

```bash
# 1. Install Termux from F-Droid (not Play Store)
# 2. Install Ubuntu proot
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

# 3. Inside Ubuntu, install Tuibro
apt update && apt install python3 python3-pip git
git clone https://github.com/yashas-13/tuibro.git
cd tuibro && bash setup.sh

# 4. Configure and run
tuibro keys set 9router sk_9router
tuibro
```

### Android-Specific Optimizations

The browser launches with these flags tuned for mobile/proot environments:

```
--no-sandbox              # Required in proot
--disable-gpu             # No GPU in proot
--disable-dev-shm-usage   # Use /tmp instead of shared memory
--single-process          # Reduce memory on mobile
--disable-extensions      # Minimal footprint
--no-first-run            # Skip first-run dialogs
```

---

## 🛡️ Privacy & Security

- **Your API keys stay on your device** — stored in `~/.tuibro/keys.json` with `0600` permissions
- **No telemetry** — Tuibro doesn't phone home, track usage, or collect data
- **No cloud dependency** — runs entirely locally (except for LLM API calls you configure)
- **Open source** — every line of code is auditable
- **Browser runs headless** — no visible window unless you use `--no-headless`

---

## 🤝 Contributing

Contributions welcome! Here's how to get started:

```bash
git clone https://github.com/yashas-13/tuibro.git
cd tuibro
pip install -e ".[dev]"
```

### Ideas for contributions:
- [ ] Streaming response support (token-by-token in chat)
- [ ] Screenshot capture and display (sixel/kitty protocol)
- [ ] Session history and replay
- [ ] Custom tool definitions
- [ ] Plugin system for custom browser actions
- [ ] Voice input support
- [ ] Multi-language UI

---

## 📜 License

MIT — use it however you want. Commercial, personal, educational. No restrictions.

---

<p align="center">
  <b>Made with ❤️ for the terminal community</b>
</p>

<p align="center">
  <a href="https://github.com/yashas-13/tuibro">
    <img src="https://img.shields.io/github/stars/yashas-13/tuibro?style=social" alt="Star on GitHub">
  </a>
  <a href="https://github.com/yashas-13/tuibro/fork">
    <img src="https://img.shields.io/github/forks/yashas-13/tuibro?style=social" alt="Fork on GitHub">
  </a>
</p>
