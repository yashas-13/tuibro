"""Tuibro CLI — agentic browser agent, terminal-native."""
import argparse
import asyncio
import os
import sys
import json
from pathlib import Path


VERSION = "0.1.0"
CONFIG_DIR = Path.home() / ".tuibro"
KEYS_FILE = CONFIG_DIR / "keys.json"


BANNER = r"""
  _____ _     _                 _
 |_   _(_)___| |__  _   _  __| | ___  _ __ ___
   | | | |_  / '_ \| | | |/ _` |/ _ \| '__/ _ \
   | | | |/ /| |_) | |_| | (_| | (_) | | |  __/
   |_| |_|_/ |_.__/ \__,_|\__,_|\___/|_|  \___|
                           v{version}

  AI-controlled browser agent for your terminal
"""


def print_banner():
    print(BANNER.format(version=VERSION))


def cmd_run(args):
    """Run tuibro with a task or interactive mode."""
    from tuibro.config import Config
    from tuibro.utils.logger import setup_logger
    from tuibro.app import TuibroApp

    config = Config().load()

    if args.provider:
        config.provider = args.provider
    if args.model:
        config.model = args.model
    if args.debug:
        config.debug = True
    if args.no_headless:
        config.headless = False
    if args.max_iterations:
        config.max_iterations = args.max_iterations

    setup_logger(config.debug)
    config.save()

    print_banner()
    print(f"  Provider: {config.provider} | Model: {config.model}")
    print(f"  Browser: {'headless' if config.headless else 'visible'}")
    if args.task:
        print(f"  Task: {args.task[:60]}...")
    print()

    app = TuibroApp(config)
    app._initial_task = args.task
    try:
        asyncio.run(app.run(task=args.task))
    except KeyboardInterrupt:
        print("\n  Goodbye!")


def cmd_setup(args):
    """First-time setup — install deps + Chromium."""
    import subprocess

    print_banner()
    print("  Running first-time setup...\n")

    script_dir = Path(__file__).parent.parent
    setup_script = script_dir / "setup.sh"

    if setup_script.exists():
        print(f"  Running {setup_script}...")
        subprocess.run(["bash", str(setup_script)], check=True)
    else:
        print("  [1/2] Installing Python dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--break-system-packages",
             "-r", str(script_dir / "requirements.txt")],
            check=True,
        )
        print("\n  [2/2] Installing Playwright Chromium...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    print("\n  ✓ Setup complete!")
    print(f"\n  Next: export TUIBRO_OPENAI_API_KEY=sk-...")
    print(f"  Then: tuibro")


def cmd_config(args):
    """View or set configuration."""
    if args.action == "show":
        config_file = CONFIG_DIR / "config.json"
        if config_file.exists():
            print(config_file.read_text())
        else:
            print("No config found. Run: tuibro setup")
        return

    if args.action == "set":
        if not args.key or not args.value:
            print("Usage: tuibro config set <key> <value>")
            return
        from tuibro.config import Config
        config = Config().load()
        if hasattr(config, args.key):
            setattr(config, args.key, args.value)
            config.save()
            print(f"  Set {args.key} = {args.value}")
        else:
            print(f"  Unknown key: {args.key}")
            print(f"  Available: provider, model, max_iterations, viewport_width, viewport_height")
        return

    if args.action == "get":
        from tuibro.config import Config
        config = Config().load()
        if args.key:
            val = getattr(config, args.key, None)
            print(f"{args.key} = {val}")
        else:
            print(f"provider = {config.provider}")
            print(f"model = {config.model}")
            print(f"headless = {config.headless}")
            print(f"max_iterations = {config.max_iterations}")
        return


def cmd_keys(args):
    """Manage API keys."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if args.action == "set":
        if not args.provider or not args.key:
            print("Usage: tuibro keys set <provider> <api-key>")
            return
        keys = {}
        if KEYS_FILE.exists():
            keys = json.loads(KEYS_FILE.read_text())
        keys[args.provider] = args.key
        KEYS_FILE.write_text(json.dumps(keys, indent=2))
        os.chmod(KEYS_FILE, 0o600)
        print(f"  Key saved for {args.provider}")
        return

    if args.action == "show":
        if not KEYS_FILE.exists():
            print("  No keys configured.")
            print("  Set with: tuibro keys set <provider> <key>")
            return
        keys = json.loads(KEYS_FILE.read_text())
        for name, key in keys.items():
            masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
            print(f"  {name}: {masked}")
        return

    if args.action == "remove":
        if not args.provider:
            print("Usage: tuibro keys remove <provider>")
            return
        if KEYS_FILE.exists():
            keys = json.loads(KEYS_FILE.read_text())
            if args.provider in keys:
                del keys[args.provider]
                KEYS_FILE.write_text(json.dumps(keys, indent=2))
                print(f"  Removed key for {args.provider}")
            else:
                print(f"  No key for {args.provider}")
        return

    if args.action == "list":
        if not KEYS_FILE.exists():
            print("  No keys configured.")
            return
        keys = json.loads(KEYS_FILE.read_text())
        print(f"  Configured providers ({len(keys)}):")
        for name in keys:
            print(f"    - {name}")
        return


def cmd_providers(args):
    """List available providers and models."""
    from tuibro.agent.providers import import_all, list_providers
    import_all()

    providers = list_providers()

    if args.name:
        if args.name not in providers:
            print(f"  Unknown provider: {args.name}")
            print(f"  Available: {', '.join(providers)}")
            return
        from tuibro.agent.providers import get_provider
        p = get_provider(args.name, "")
        print(f"\n  {p.name}")
        print(f"  Models:")
        for m in p.models:
            default = " (default)" if m == p.default_model else ""
            print(f"    - {m}{default}")
        print(f"  Base URL: {p.base_url}")
        print(f"  API Key: TUIBRO_{args.name.upper()}_API_KEY")
        return

    print(f"\n  Available providers ({len(providers)}):\n")
    for name in providers:
        try:
            p = get_provider(name, "")
            models_str = ", ".join(p.models[:3])
            if len(p.models) > 3:
                models_str += f" (+{len(p.models)-3} more)"
            print(f"  {name:12s}  {models_str}")
        except Exception:
            print(f"  {name:12s}")
    print(f"\n  Usage: tuibro --provider <name>")
    print(f"  Set key: tuibro keys set <provider> <key>")


def cmd_browser(args):
    """Direct browser commands (no agent)."""
    from tuibro.browser.engine import BrowserEngine

    async def run():
        engine = BrowserEngine(headless=True)
        await engine.start()

        if args.navigate:
            url = args.navigate
            if not url.startswith("http"):
                url = "https://" + url
            page = await engine.navigate(url)
            print(f"  Title: {page.title}")
            print(f"  URL: {page.url}")
            print(f"  Elements: {len(page.interactive_elements)}")
            for el in page.interactive_elements[:20]:
                print(f"    [{el.index}] {el.role}: {el.name}")
        elif args.js:
            result = await engine.evaluate_js(args.js)
            print(f"  Result: {result.page_text}")

        await engine.stop()

    asyncio.run(run())


def cmd_version(args):
    print(f"tuibro {VERSION}")


def main():
    parser = argparse.ArgumentParser(
        prog="tuibro",
        description="Tuibro — AI-controlled browser agent for your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tuibro setup                          First-time setup
  tuibro                                Interactive mode
  tuibro run --task "search google..."  Run with a task
  tuibro keys set openai sk-...         Set API key
  tuibro providers                      List providers
  tuibro browser --navigate google.com  Direct browser
  tuibro config set model gpt-4o-mini   Change model

Keyboard (in TUI):
  Tab       Cycle focus (Chat/Browser/Activity)
  F1        Help
  F2        Cycle provider
  F3        Cycle model
  F4        Clear chat
  F5        Toggle activity pane
  F6        New tab
  F7        Close tab
  Ctrl+C    Stop/Quit
""",
    )
    parser.add_argument("--version", "-v", action="store_true", help="Show version")
    parser.add_argument("--provider", "-p", help="LLM provider")
    parser.add_argument("--model", "-m", help="Model name")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run
    p_run = subparsers.add_parser("run", help="Run agent with a task")
    p_run.add_argument("task", nargs="?", help="Task for the agent")
    p_run.add_argument("--provider", "-p", help="LLM provider")
    p_run.add_argument("--model", "-m", help="Model name")
    p_run.add_argument("--debug", "-d", action="store_true")
    p_run.add_argument("--no-headless", action="store_true")
    p_run.add_argument("--max-iterations", type=int, default=20)

    # setup
    subparsers.add_parser("setup", help="First-time setup")

    # config
    p_config = subparsers.add_parser("config", help="View/set config")
    p_config.add_argument("action", choices=["show", "set", "get"])
    p_config.add_argument("key", nargs="?")
    p_config.add_argument("value", nargs="?")

    # keys
    p_keys = subparsers.add_parser("keys", help="Manage API keys")
    p_keys.add_argument("action", choices=["set", "show", "remove", "list"])
    p_keys.add_argument("provider", nargs="?")
    p_keys.add_argument("key", nargs="?")

    # providers
    p_providers = subparsers.add_parser("providers", help="List providers")
    p_providers.add_argument("name", nargs="?")

    # browser
    p_browser = subparsers.add_parser("browser", help="Direct browser commands")
    p_browser.add_argument("--navigate", "-n", help="Navigate to URL")
    p_browser.add_argument("--js", help="Execute JavaScript")

    # version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.version:
        cmd_version(args)
        return

    if args.command == "run":
        cmd_run(args)
    elif args.command == "setup":
        cmd_setup(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "keys":
        cmd_keys(args)
    elif args.command == "providers":
        cmd_providers(args)
    elif args.command == "browser":
        cmd_browser(args)
    elif args.command == "version":
        cmd_version(args)
    else:
        # No subcommand = interactive mode (like codex)
        from tuibro.config import Config
        from tuibro.utils.logger import setup_logger
        from tuibro.app import TuibroApp

        config = Config().load()
        if args.provider:
            config.provider = args.provider
        if args.model:
            config.model = args.model
        if args.debug:
            config.debug = True
        setup_logger(config.debug)

        print_banner()
        print(f"  Provider: {config.provider} | Model: {config.model}")
        print()

        app = TuibroApp(config)
        try:
            asyncio.run(app.run())
        except KeyboardInterrupt:
            print("\n  Goodbye!")
