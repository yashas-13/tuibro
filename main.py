#!/usr/bin/env python3
"""Tuibro - TUI Embedded Browser Agent for Android."""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tuibro.config import Config
from tuibro.utils.logger import setup_logger


def parse_args():
    parser = argparse.ArgumentParser(
        prog="tuibro",
        description="Tuibro — AI-controlled browsing from your terminal",
    )
    parser.add_argument("--provider", default=None, help="LLM provider (openai, anthropic, google, groq, mistral, cohere, together, ollama, lmstudio, vllm, openrouter)")
    parser.add_argument("--model", default=None, help="Model name")
    parser.add_argument("--task", default=None, help="Task for the agent to execute autonomously")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--max-iterations", type=int, default=20, help="Max agent iterations")
    return parser.parse_args()


def main():
    args = parse_args()
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

    from tuibro.app import TuibroApp
    app = TuibroApp(config)
    app._initial_task = args.task
    asyncio.run(app.run(task=args.task))


if __name__ == "__main__":
    main()
