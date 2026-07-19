"""Status bar component for Tuibro TUI."""


def render_status_line(provider: str, model: str, agent_status: str = "Idle") -> str:
    parts = [
        f"Provider: {provider}",
        f"Model: {model}",
        f"Agent: {agent_status}",
    ]
    parts.append("[F1]Help [F2]Provider [F3]Model [Ctrl+C]Quit")
    return " │ ".join(parts)
