"""Config command - Manage application configuration."""

import click
from rich.console import Console
from rich.table import Table

from mtg_card_app.config import ProviderFactory, get_config

console = Console()


@click.group()
def config() -> None:
    """Manage MTG Card App configuration.

    Examples:
        mtg config show

        mtg config set llm.provider openai

        mtg config get llm.provider

    """


@config.command()
def show() -> None:
    """Display current configuration."""
    cfg = get_config()

    # Create table for display
    table = Table(title="⚙️  Configuration", show_header=True)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # LLM settings
    provider = cfg.get("llm.provider")
    table.add_row("LLM Provider", provider or "ollama")

    # Provider config
    provider_config = cfg.get_provider_config()
    model = provider_config.get("model", "N/A")
    table.add_row("LLM Model", model)

    # Cache settings
    cache_enabled = cfg.get("cache.enabled")
    cache_maxsize = cfg.get("cache.maxsize")
    table.add_row("Cache Enabled", str(cache_enabled))
    table.add_row("Cache Max Size", str(cache_maxsize))

    # Data settings
    data_dir = cfg.get("data.directory")
    table.add_row("Data Directory", data_dir or "data")

    console.print(table)
    console.print(f"\n[dim]Config file: {cfg.config_path}[/dim]")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a configuration value.

    Examples:
        mtg config set llm.provider openai

        mtg config set cache.enabled true

    """
    cfg = get_config()

    # Convert boolean strings
    if value.lower() in ["true", "false"]:
        value = value.lower() == "true"

    # Convert numeric strings
    try:
        if "." in value:
            value = float(value)
        else:
            value = int(value)
    except ValueError:
        pass  # Keep as string

    cfg.set(key, value)
    console.print(f"[green]✓[/green] Set {key} = {value}")
    console.print(f"[dim]Saved to: {cfg.config_path}[/dim]")


@config.command()
@click.argument("key")
def get(key: str) -> None:
    """Get a configuration value.

    Examples:
        mtg config get llm.provider

        mtg config get cache.enabled

    """
    cfg = get_config()
    value = cfg.get(key)

    if value is None:
        console.print(f"[yellow]Key '{key}' not found[/yellow]")
    else:
        console.print(f"{key} = [green]{value}[/green]")


@config.command()
def reset() -> None:
    """Reset configuration to defaults."""
    cfg = get_config()

    click.confirm("This will reset all settings to defaults. Continue?", abort=True)

    cfg.reset_to_defaults()
    console.print("[green]✓[/green] Configuration reset to defaults")
    console.print(f"[dim]Config file: {cfg.config_path}[/dim]")


@config.command()
def providers() -> None:
    """List available LLM providers."""
    cfg = get_config()
    factory = ProviderFactory(cfg)

    available = factory.get_available_providers()

    table = Table(title="🤖 Available LLM Providers", show_header=True)
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Install Command")

    all_providers = ["ollama", "openai", "anthropic", "gemini", "groq"]

    for provider in all_providers:
        is_available = provider in available
        status = "✓ Available" if is_available else "✗ Not Installed"
        install_cmd = "-" if is_available or provider == "ollama" else f"pip install mtg-card-app[{provider}]"

        table.add_row(provider.capitalize(), status, install_cmd)

    console.print(table)

    # Show current provider
    current = cfg.get("llm.provider", "ollama")
    console.print(f"\n[dim]Current provider: [bold]{current}[/bold][/dim]")
