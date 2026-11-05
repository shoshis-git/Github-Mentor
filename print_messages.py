from rich.console import Console
from rich.panel import Panel

ROLE_STYLES = {
    "HumanMessage": ("[bold blue]User[/bold blue]",   "blue"),
    "AIMessage":    ("[bold green]Agent[/bold green]", "green"),
    "ToolMessage":  ("[bold yellow]Tool[/bold yellow]", "yellow"),
}

def extract_content(message):
    content = message.content if hasattr(message, "content") else message
    if isinstance(content, list):
        return "\n".join(
            part["text"] if isinstance(part, dict) and "text" in part else str(part)
            for part in content
        )
    return str(content)

def print_messages(messages):
    console = Console()
    for msg in messages:
        role = type(msg).__name__
        title, border = ROLE_STYLES.get(role, (role, "white"))
        console.print(Panel(extract_content(msg), title=title, border_style=border))
