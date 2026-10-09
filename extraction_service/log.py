from rich.console import Console

console = Console()

class Logger:
    def info(self, msg, *args, **kwargs):
        console.print(f"[bold blue]INFO:[/bold blue] {msg}")

    def warning(self, msg, *args, **kwargs):
        console.print(f"[bold yellow]WARN:[/bold yellow] {msg}")

    def error(self, msg, *args, **kwargs):
        console.print(f"[bold red]ERROR:[/bold red] {msg}")
    
    def debug(self, msg, *args, **kwargs):
        console.print(f"[dim]DEBUG:[/dim] {msg}")

log = Logger()
