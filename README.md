<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-1.45+-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Platform-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge" alt="MIT Licence">
  <img src="https://img.shields.io/badge/Version-0.1.0-orange?style=for-the-badge" alt="v0.1.0">
  <img src="https://img.shields.io/badge/Providers-12-purple?style=for-the-badge" alt="12 LLM Providers">
  <img src="https://img.shields.io/badge/Tools-21-red?style=for-the-badge" alt="21 Agent Tools">
  <img src="https://img.shields.io/badge/Engine-Playwright+%7C+Carbonyl-yellow?style=for-the-badge" alt="Dual Engine">
</p>

<h1 align="center">
  <br>
  🌐 Tuibro
  <br>
  <sub>AI-controlled browser agent that lives in your terminal</sub>
</h1>

<p align="center">
  <b>Tell it what you need. It browses the web for you.</b><br>
  <sub>Click, type, scroll, navigate — all autonomous, all visible in real-time.</sub>
</p>

<p align="center">
  <a href="#-what-is-tuibro">What</a> •
  <a href="#-split-screen-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-agent-tools">Tools</a> •
  <a href="#-supported-providers">Providers</a> •
  <a href="#-how-it-works">How it works</a> •
  <a href="#-keyboard-shortcuts">Shortcuts</a> •
  <a href="#-android-setup">Android</a> •
  <a href="#-contributing">Contribute</a>
</p>

---

## 🤔 What is Tuibro?

Imagine saying *"find me the best-rated drone under $500 across Amazon, Best Buy, and B&H Photo"* — and watching an AI agent open all three stores in parallel tabs, search each one, compare prices and ratings, extract product details, and present you a side-by-side comparison — all from a split-screen in your terminal.

**That's Tuibro.**

It's a **terminal-native browser agent** that gives an AI model full control of a real Chromium browser. You type a task on the left side of your screen. On the right side, you watch the agent navigate websites, click buttons, fill forms, and extract data — step by step, in real-time. An activity log captures every action as it happens.

No browser extension. No cloud service. No JavaScript injection. A **real browser** that the AI controls directly, running right on your Android device (or any Linux machine).

### Why does this exist?

Most AI browser tools are either:
- **Cloud-only** — you hand over your data and trust a black box
- **Browser extensions** — limited to what Chrome allows, desktop-only
- **Desktop-only** — can't run on the device you actually carry

Tuibro is different:
- **Runs in your terminal** — works on Android via Termux/proot-distro
- **Fully transparent** — you see every click, every navigation, every extraction
- **Real browser** — actual Chromium with Playwright, not a simulation
- **Your data stays local** — no third-party servers, no telemetry, no tracking
- **12 LLM providers** — OpenAI, Anthropic, Google, Groq, 9router (464+ models), and more
- **21 agent tools** — navigate, click, type, scroll, tab management, DOM extraction, JS eval
- **Dual engine** — Playwright (full DOM) + Carbonyl (text-native, agent-optimized)

---

## 🖥️ Split-Screen Architecture

Tuibro's TUI divides your terminal into three synchronized panes:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [0:NewTab]  [1:Google ◄]  [2:Bing]  [3:Amazon]                          Provider: 9router│
├─────────────────────┬──────────────────────────────────┬─────────────────────────────────┤
│                     │                                  │                                 │
│  💬 Chat            │  🌐 Browser                      │  📊 Activity                    │
│                     │                                  │                                 │
│ You: Search Amazon  │  Tab: [3/4] Drones - Amazon      │  URL: amazon.com/s?k=drones    │
│  for drones under   │  URL: https://amazon.com/s?k=   │  Scroll: 32% | Elements: 47     │
│  $500               │  Title: Drones: Electronics      │  ───────────────────────────    │
│                     │                                  │  Activity Log:                  │
│ Agent: I'll search  │  Interactive elements:            │                                 │
│  3 stores in        │   [0] searchbox: Search Amazon   │  09:14:06 · Browser started     │
│  parallel for you.  │   [1] link: Electronics          │  09:14:08 ⇄ New tab 1: Amz     │
│                     │   [2] button: Add to Cart        │  09:14:11 → amazon.com/s?k=...  │
│  Opening tabs...    │   [3] link: DJI Mini 4 Pro      │  09:14:15 👆 Click [0] Search   │
│  → Tab 1: Amazon    │   [4] link: Holy Stone HS720G   │  09:14:17 ⌨ Type: drones       │
│  → Tab 2: Best Buy  │   [5] link: Ruko F11 GIM2      │  09:14:20 👆 Click [1] Search   │
│  → Tab 3: B&H Photo │   [6] link: Potensic Atom SE    │  09:14:23 ⇄ Tab 2 opened       │
│                     │   [7] button: Next Page          │  09:14:25 📋 Extracted 12 items │
│ Comparing prices... │   [8] link: DJI Mini 3 Pro      │  09:14:28 → bestbuy.com/...     │
│ Found 12 products   │   [9] button: Add to Wishlist   │  09:14:31 👆 Click [4] HS720G   │
│ across 3 stores.    │                                  │  09:14:34 📋 Got $399.99       │
│                     │  Last: Click [4] Holy Stone      │  09:14:36 ⇄ Tab 3: B&H         │
│ Results:            │                                  │  09:14:39 📋 Extracted 8 items │
│  1. DJI Mini 4 Pro  │                                  │  09:14:42 📊 Comparison ready  │
│  2. Holy Stone 720G │                                  │                                 │
│  3. Ruko F11 GIM2   │                                  │                                 │
│                     │                                  │                                 │
│ [Confirm to buy?]   │                                  │                                 │
│                     │                                  │                                 │
├─────────────────────┴──────────────────────────────────┴─────────────────────────────────┤
│ Provider: 9router │ Model: oc │ Agent: Running iter 5/20 │ [F1]Help [F2]Prov [F5]Viz    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Three-Pane Layout

| Pane | What it shows | How it helps |
|------|---------------|--------------|
| **💬 Chat** (left) | Your messages, agent responses, action log | See the conversation and what the agent is doing |
| **🌐 Browser** (center) | Live DOM/a11y tree, interactive elements with indices, tab indicators | Watch the agent interact with real web pages |
| **📊 Activity** (right) | Timestamped event stream with icons (→ navigate, 👆 click, ⌨ type, ⇄ tab switch, 📋 extract) | Real-time feed of every action the agent takes |

### Multi-Tab Workflow

The agent can manage multiple browser tabs simultaneously:

- **Open new tabs** for parallel research across multiple websites
- **Switch between tabs** to compare information side by side
- **Close tabs** when research is complete
- **Tab bar** shows all open tabs with the active one highlighted

---

## 🚀 Quick Start

### One-liner install

```bash
# Clone, setup, and run
git clone https://github.com/yashas-13/tuibro.git && cd tuibro && bash setup.sh
```

### Manual install

```bash
# Install Python dependencies
pip install -e .

# Install Playwright Chromium
python -m playwright install chromium

# Set your API key (9router is free, or use your own provider)
tuibro keys set 9router sk_9router

# Run!
tuibro
```

### First run

```bash
tuibro
```

You'll see the split-screen TUI. Type a task on the left, and watch the agent work on the right.

### Headless mode (no TUI)

```bash
tuibro run "Navigate to https://example.com and tell me the title" --no-tui
```

---

## ✨ Features

### 🧠 AI Agent with Full Browser Control

The agent observes the page, decides what to do, and executes actions autonomously:

1. **Observe** — reads the DOM/a11y tree to understand the page
2. **Think** — sends the page state to the LLM for decision-making
3. **Act** — executes the chosen action (click, type, navigate, etc.)
4. **Render** — updates all three TUI panes in real-time
5. **Repeat** — until the task is complete

### 📑 Tab Management

| Action | Tool | Description |
|--------|------|-------------|
| Open tab | `new_tab(url)` | Opens a new tab, optionally navigating to a URL |
| Close tab | `close_tab(index)` | Closes a tab by index |
| Switch tab | `switch_tab(index)` | Switches to a different tab |
| List tabs | `list_tabs()` | Lists all open tabs with titles and URLs |

### 🔍 DOM Control

| Action | Tool | Description |
|--------|------|-------------|
| Click | `click(element_index)` | Clicks any interactive element by index |
| Type | `type_text(element_index, text)` | Types text into input fields |
| Select | `select_option(element_index, value)` | Selects dropdown options |
| Scroll | `scroll(direction)` | Scrolls up or down |
| Extract text | `get_element_text(index)` | Gets text content of an element |
| Get attribute | `get_element_attribute(index, attr)` | Gets any HTML attribute |
| Execute JS | `evaluate_js(expression)` | Runs arbitrary JavaScript |
| Get HTML | `get_page_html(selector)` | Extracts page HTML |
| Get links | `get_all_links()` | Lists all links on the page |
| Get forms | `get_all_forms()` | Lists all forms with their fields |

### 📊 Real-Time Activity Visualization

The activity pane logs every action with timestamps and icons:

- `→` Navigation (URL changes)
- `👆` Clicks
- `⌨` Text input
- `↕` Scrolling
- `＋` Tab opened
- `✕` Tab closed
- `⇄` Tab switched
- `📋` Data extraction
- `⚙` JavaScript evaluation
- `📝` Form submission
- `🌐` Network activity
- `✗` Errors

### 🔧 Dual Browser Engine

| Engine | Best for | Trade-off |
|--------|----------|-----------|
| **Playwright** | Full DOM access, screenshots, JavaScript execution | Heavier resource usage |
| **Carbonyl** | Text-native browsing, agent-optimized, lightweight | Limited to text-mode rendering |

The engine selector automatically falls back: Carbonyl → Playwright.

---

## 🛠️ Agent Tools (21 total)

### Navigation
- `navigate(url)` — Navigate to a URL
- `go_back()` — Go back in history
- `go_forward()` — Go forward in history

### Tab Management
- `new_tab(url)` — Open a new tab
- `close_tab(index)` — Close a tab
- `switch_tab(index)` — Switch to a tab
- `list_tabs()` — List all tabs

### Interaction
- `click(element_index)` — Click an element
- `type_text(element_index, text)` — Type text
- `select_option(element_index, value)` — Select dropdown
- `scroll(direction)` — Scroll up/down
- `wait(seconds)` — Wait for page loading

### Extraction
- `get_element_text(index)` — Get element text
- `get_element_attribute(index, attribute)` — Get HTML attribute
- `evaluate_js(expression)` — Execute JavaScript
- `get_page_html(selector)` — Get page HTML
- `get_all_links()` — List all links
- `get_all_forms()` — List all forms
- `get_cookies()` — Get browser cookies
- `set_local_storage(key, value)` — Set localStorage

### Control
- `done(answer)` — Complete the task with a final answer

---

## 🤖 Supported Providers

Tuibro supports **12 LLM providers** — use whichever model you prefer:

| Provider | Default Model | Notes |
|----------|---------------|-------|
| **9router** | `oc` | 464+ models, free combo router, localhost |
| **OpenAI** | `gpt-4o` | GPT-4o, GPT-4o-mini, GPT-4.1 |
| **Anthropic** | `claude-sonnet-4` | Claude 3.5 Sonnet, Claude 3 Opus |
| **Google** | `gemini-2.5-flash` | Gemini 2.5 Flash, Gemini 2.5 Pro |
| **Groq** | `llama-3.3-70b` | Ultra-fast inference |
| **Mistral** | `mistral-large` | Mistral Large, Codestral |
| **Cohere** | `command-r-plus` | Command R+ |
| **Together** | `meta-llama/Llama-3.3-70B` | Open-source models |
| **Ollama** | `llama3.3` | Local models |
| **LM Studio** | `local-model` | Local models |
| **vLLM** | `local-model` | Self-hosted |
| **OpenRouter** | `auto` | Meta-provider, 100+ models |

### Setting up a provider

```bash
# 9router (free, 464+ models)
tuibro keys set 9router sk_9router

# OpenAI
tuibro keys set openai sk-your-key

# Anthropic
tuibro keys set anthropic sk-ant-your-key

# Google
tuibro keys set google your-gemini-key

# Use it
tuibro --provider openai --model gpt-4o
```

---

## ⚡ How It Works

```
User types task
       │
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Agent Core  │────▶│  LLM Provider │────▶│  Browser     │
│  (loop)      │◀────│  (think)      │◀────│  Engine      │
└──────┬──────┘     └──────────────┘     └──────┬──────┘
       │                                          │
       ▼                                          ▼
┌─────────────┐                          ┌──────────────┐
│  TUI Panes   │                          │  Chromium     │
│  (render)    │◀─────────────────────────│  (real page)  │
└─────────────┘                          └──────────────┘
```

### The Agent Loop

1. **Start** — User provides a task (e.g., "search Amazon for drones")
2. **Observe** — Agent reads the current page state (URL, title, interactive elements)
3. **Think** — Sends page state + task to the LLM, which decides the next action
4. **Act** — Executes the action (click element #3, type "drones", etc.)
5. **Render** — Updates all TUI panes with the new state
6. **Repeat** — Loop continues until the agent calls `done()` or hits max iterations

### Multi-Tab Parallel Search

For tasks like "search multiple stores for drones":

1. Agent opens 3 tabs (Amazon, Best Buy, B&H Photo)
2. Navigates each tab to the store's search page
3. Types the search query in each tab
4. Extracts product data from each tab
5. Compiles a comparison across all stores
6. Presents results and waits for user confirmation

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Cycle focus between Chat / Browser / Activity panes |
| `↑` / `↓` | Scroll the active pane |
| `Enter` | Send message (Chat) or submit URL (Browser) |
| `F1` | Help overlay |
| `F2` | Cycle LLM providers |
| `F3` | Cycle models |
| `F5` | Toggle activity pane visibility |
| `F6` | Open new browser tab |
| `F7` | Close current tab |
| `Ctrl+C` | Stop agent / Quit |

---

## 📱 Android Setup

Tuibro is optimized for Android through Termux + proot-distro:

### Step-by-step

```bash
# 1. Install Termux from F-Droid (NOT Play Store — Play Store version is outdated)
# 2. Install Ubuntu proot
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

# 3. Inside Ubuntu
apt update && apt install python3 python3-pip git curl
git clone https://github.com/yashas-13/tuibro.git
cd tuibro && bash setup.sh

# 4. Configure and run
tuibro keys set 9router sk_9router
tuibro
```

### Android-specific browser flags

The browser launches with flags tuned for mobile/proot environments:

```
--no-sandbox              # Required in proot
--disable-gpu             # No GPU in proot
--disable-dev-shm-usage   # Use /tmp instead of shared memory
--single-process          # Reduce memory on mobile
--disable-extensions      # Minimal footprint
--no-first-run            # Skip first-run dialogs
--disable-background-networking  # Save battery
```

### Battery & Memory Tips

- Use `headless: true` (default) to save resources
- The Carbonyl engine uses less memory than Playwright
- Close unused tabs with `F7` or `close_tab()`
- Use `--max-iterations 10` to limit agent steps

---

## 🔒 Privacy & Security

- **Your API keys stay on your device** — stored in `~/.tuibro/keys.json` with `0600` permissions
- **No telemetry** — Tuibro doesn't phone home, track usage, or collect data
- **No cloud dependency** — runs entirely locally (except for LLM API calls you configure)
- **Open source** — every line of code is auditable under MIT licence
- **Headless by default** — no visible window unless you use `--no-headless`

---

## 🏗️ Project Structure

```
tuibro/
├── __init__.py                # Package root
├── cli.py                     # CLI entry point (tuibro command)
├── app.py                     # Main TUI app (curses, panes, event loop)
├── config.py                  # Config + key management (~/.tuibro/)
├── preview.py                 # Text-based TUI preview (no curses needed)
│
├── agent/
│   ├── core.py                # Agent loop (observe → think → act → render)
│   ├── prompts.py             # System + task prompts
│   └── providers/
│       ├── base.py            # Provider ABC + dataclasses
│       ├── openai.py          # OpenAI
│       ├── anthropic.py       # Anthropic
│       ├── google.py          # Google Gemini
│       ├── groq.py            # Groq
│       ├── mistral.py         # Mistral
│       ├── cohere.py          # Cohere
│       ├── together.py        # Together AI
│       ├── ollama.py          # Ollama (local)
│       ├── lmstudio.py        # LM Studio (local)
│       ├── vllm.py            # vLLM (local)
│       ├── openrouter.py      # OpenRouter
│       └── ninerouter.py      # 9router (464+ models)
│
├── browser/
│   ├── engine.py              # Playwright engine (tabs, DOM, events)
│   ├── carbonyl_engine.py     # Carbonyl engine (text-native)
│   ├── engine_selector.py     # Auto-fallback engine picker
│   ├── actions.py             # 21 tool definitions + execution
│   ├── renderer.py            # DOM/a11y tree → terminal renderer
│   └── dom.py                 # DOM parsing utilities
│
├── tui/
│   ├── layout.py              # Split-pane layout manager
│   ├── chat_pane.py           # Chat interface
│   ├── browser_pane.py        # Browser DOM + activity view
│   ├── status_bar.py          # Bottom status bar
│   └── theme.py               # Colors + Unicode characters
│
└── utils/
    ├── keys.py                # API key storage
    └── logger.py              # Debug logging
```

---

## 🔧 CLI Reference

```bash
# ── Main Commands ──────────────────────────────────────
tuibro                                # Interactive TUI mode
tuibro run "task description"         # Run with a specific task
tuibro run "task" --no-tui            # Headless mode (no TUI)
tuibro setup                          # First-time setup (deps + Chromium)

# ── Configuration ──────────────────────────────────────
tuibro config show                    # Show current config
tuibro config get model               # Get a specific value
tuibro config set model gpt-4o-mini   # Change a setting
tuibro config set provider anthropic  # Switch provider
tuibro config set max_iterations 30   # More agent steps

# ── API Keys ───────────────────────────────────────────
tuibro keys show                      # Show configured keys (masked)
tuibro keys set openai sk-...         # Save a key
tuibro keys remove openai             # Remove a key
tuibro keys list                      # List all providers with keys

# ── Providers ──────────────────────────────────────────
tuibro providers                      # List all 12 providers
tuibro providers openai               # Show models for a provider
tuibro providers 9router              # Show 9router's 464+ models

# ── Browser (no agent) ─────────────────────────────────
tuibro browser -n google.com          # Navigate to URL
tuibro browser --js "document.title"  # Execute JavaScript

# ── Global Options ─────────────────────────────────────
--provider, -p    LLM provider (default: 9router)
--model, -m       Model name (default: oc)
--engine, -e      Browser engine: carbonyl | playwright
--debug, -d       Enable debug logging
--version, -v     Show version
```

---

## 🧪 Example: E-Commerce Multi-Store Search

```bash
tuibro run "Search Amazon, Best Buy, and B&H Photo for 'DJI Mini 4 Pro'. Compare prices, ratings, and availability. Present a comparison table." --no-tui
```

The agent will:
1. Open 3 browser tabs (one per store)
2. Navigate each to the store's search page
3. Search for "DJI Mini 4 Pro" on each
4. Extract: product name, price, rating, availability
5. Compile a comparison across all stores
6. Present results and wait for your confirmation

---

## 🤝 Contributing

Contributions welcome! Here's how to get started:

```bash
git clone https://github.com/yashas-13/tuibro.git
cd tuibro
pip install -e ".[dev]"
```

### Ideas for contributions

- [ ] Streaming response support (token-by-token in chat pane)
- [ ] Screenshot capture and display (sixel/kitty/iterm2 protocol)
- [ ] Session history and replay
- [ ] Custom tool definitions
- [ ] Plugin system for custom browser actions
- [ ] Voice input support
- [ ] Multi-language UI
- [ ] Shopping cart automation (add to cart, checkout flow)
- [ ] Form auto-fill from saved profiles
- [ ] Cookie/session persistence across runs

---

## 🙏 Tributes

Tuibro stands on the shoulders of giants. These open source projects made it possible.

### Core Dependencies

- **[Playwright](https://github.com/microsoft/playwright)** · [playwright.dev](https://playwright.dev) — Browser automation backbone. Launches Chromium, navigates pages, clicks elements, extracts the DOM tree. The foundation of Tuibro's browser engine.

- **[httpx](https://github.com/encode/httpx)** · [python-httpx.org](https://www.python-httpx.org) — Async HTTP client. Every LLM API call across all 12 providers flows through httpx.

- **[Carbonyl](https://github.com/jmagly/carbonyl-agent)** — Text-native headless browser, agent-optimized alternative to Playwright. Renders pages as text for faster, lighter agent interaction.

- **Python curses** · [docs.python.org/3/library/curses.html](https://docs.python.org/3/library/curses.html) — Built-in TUI rendering. Split panes, color pairs, keyboard handling — the visual backbone of the terminal interface.

### LLM Ecosystem

- **[OpenAI](https://github.com/openai/openai-python)** · [platform.openai.com/docs](https://platform.openai.com/docs) — Pioneered the function/tool calling API format that Tuibro's 12 providers follow.

- **[Anthropic](https://github.com/anthropics/anthropic-sdk-python)** · [docs.anthropic.com](https://docs.anthropic.com) — Claude's tool use format. Tuibro's Anthropic provider adapts this for browser automation.

- **[9router](https://www.npmjs.com/package/9router)** — Combo model router providing 464+ models through a single localhost endpoint. The default provider for Tuibro.

- **[Ollama](https://github.com/ollama/ollama)** · [ollama.com](https://ollama.com) — Local model serving. Inspired Tuibro's BYOK (Bring Your Own Key) approach — your models, your rules.

### Inspiration

- **[Open Interpreter](https://github.com/OpenInterpreter/open-interpreter)** · [openinterpreter.com](https://openinterpreter.com) — Showed the world that AI agents can control computers from a terminal. The core idea behind Tuibro.

- **[Aider](https://github.com/paul-gauthier/aider)** · [aider.chat](https://aider.chat) — Terminal-native AI coding. Inspired Tuibro's CLI-first design, provider cycling, and model switching.

- **[Claude Code](https://github.com/anthropics/claude-code)** · [docs.anthropic.com/claude-code](https://docs.anthropic.com/claude-code) — Terminal agent pattern. The observe → think → act loop and tool calling architecture that Tuibro follows.

- **[Codex CLI](https://github.com/openai/codex)** · [openai.com/index/codex-cli](https://openai.com/index/codex-cli) — Terminal-native agent execution. Influenced Tuibro's headless `--no-tui` mode.

- **[Browser Use](https://github.com/browser-use/browser-use)** · [browser-use.com](https://browser-use.com) — AI browser automation patterns. Influenced the DOM element indexing and action loop.

- **[Textual](https://github.com/Textualize/textual)** · [textual.textualize.io](https://textual.textualize.io) — TUI framework. Inspired the split-pane layout and real-time update architecture.

- **[Rich](https://github.com/Textualize/rich)** · [rich.readthedocs.io](https://rich.readthedocs.io) — Terminal rendering. Inspired the color theme and Unicode box-drawing characters.

### Infrastructure

- **[Termux](https://github.com/termux/termux-app)** · [termux.dev](https://termux.dev) — Android terminal emulator. Makes TUI apps like Tuibro possible on mobile.

- **[proot-distro](https://github.com/proot-me/proot-distro)** — Linux environments on Android. Tuibro runs inside proot Ubuntu on phones and tablets.

- **[Chromium](https://chromium.googlesource.com/chromium/src)** · [chromium.org](https://www.chromium.org) — The browser engine. Playwright controls Chromium under the hood.

---

## 📜 Licence

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
  <a href="https://github.com/yashas-13/tuibro/issues">
    <img src="https://img.shields.io/github/issues/yashas-13/tuibro?style=social" alt="Issues">
  </a>
</p>
