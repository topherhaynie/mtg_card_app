"""Setup wizard - Interactive first-time setup."""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from mtg_card_app.config import ProviderFactory, get_config

console = Console()


def run_setup_wizard() -> None:
    """Run the interactive setup wizard.

    Guides users through:
    1. Choosing an LLM provider
    2. Configuring API keys
    3. Testing the connection
    4. Verifying data files

    """
    console.print(
        Panel.fit(
            "[bold cyan]🎴 MTG Card App - Setup Wizard[/bold cyan]\n\n"
            "This wizard will help you configure the app for first use.",
            border_style="cyan",
        )
    )

    config = get_config()
    factory = ProviderFactory(config)

    # Step 1: Welcome and current status
    _show_welcome_status(config, factory)

    # Step 2: Choose LLM provider
    if Confirm.ask("\n[bold]Configure LLM provider?[/bold]", default=True):
        _configure_llm_provider(config, factory)

    # Step 3: Verify data files
    console.print("\n[bold cyan]📂 Step 3: Data Files[/bold cyan]")
    _verify_data_files(config)

    # Step 4: Test connection
    if Confirm.ask("\n[bold]Test your configuration?[/bold]", default=True):
        _test_configuration(config, factory)

    # Final summary
    console.print(
        Panel.fit(
            "[green]✓[/green] Setup complete!\n\n"
            "You're ready to use MTG Card App.\n\n"
            "[bold]Try these commands:[/bold]\n"
            "  mtg                    # Start chat mode\n"
            '  mtg search "Lightning Bolt"\n'
            '  mtg combo find "Thoracle"\n'
            "  mtg stats              # View system info",
            border_style="green",
            title="🎉 All Set!",
        )
    )


def _show_welcome_status(config, factory) -> None:
    """Show current configuration status."""
    console.print("\n[bold cyan]📊 Step 1: Current Configuration[/bold cyan]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    # LLM Provider
    current_provider = config.get("llm.provider", "ollama")
    is_available = factory.is_provider_available(current_provider)
    status = "[green]✓ Available[/green]" if is_available else "[red]✗ Not installed[/red]"
    table.add_row("LLM Provider", f"{current_provider} {status}")

    # Config file location
    table.add_row("Config File", str(config.config_path))

    # Data directory
    data_dir = config.get("data.directory", "data")
    table.add_row("Data Directory", str(data_dir))

    console.print(table)


def _configure_llm_provider(config, factory) -> None:
    """Interactive LLM provider configuration."""
    console.print("\n[bold cyan]🤖 Step 2: LLM Provider Selection[/bold cyan]")

    # Show provider options
    _show_provider_options(factory)

    # Get user choice
    current = config.get("llm.provider", "ollama")
    provider_choice = Prompt.ask(
        "\n[bold]Choose your provider[/bold]",
        choices=["ollama", "openai", "anthropic", "gemini", "groq"],
        default=current,
    )

    # Check if provider is available
    if not factory.is_provider_available(provider_choice):
        console.print(f"\n[yellow]⚠ {provider_choice.capitalize()} is not installed.[/yellow]")
        console.print(f"Install with: [bold]pip install mtg-card-app[{provider_choice}][/bold]")

        if not Confirm.ask("Continue anyway?", default=False):
            console.print("[dim]Keeping current provider.[/dim]")
            return

    # Save provider choice
    config.set("llm.provider", provider_choice)
    console.print(f"[green]✓[/green] Set provider to: [bold]{provider_choice}[/bold]")

    # Configure provider-specific settings
    _configure_provider_settings(config, provider_choice)


def _show_provider_options(factory) -> None:
    """Display provider comparison table."""
    table = Table(title="Available LLM Providers", show_header=True)
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Cost", style="yellow")
    table.add_column("Speed", style="green")
    table.add_column("Privacy", style="magenta")
    table.add_column("Status")

    providers_info = [
        ("ollama", "Free", "Medium", "Complete", factory.is_provider_available("ollama")),
        ("gemini", "Free*", "Fast", "Google", factory.is_provider_available("gemini")),
        ("groq", "Free*", "Very Fast", "Groq", factory.is_provider_available("groq")),
        ("openai", "Paid", "Fast", "OpenAI", factory.is_provider_available("openai")),
        ("anthropic", "Paid", "Fast", "Anthropic", factory.is_provider_available("anthropic")),
    ]

    for provider, cost, speed, privacy, available in providers_info:
        status = "[green]✓ Ready[/green]" if available else "[dim]Not installed[/dim]"
        table.add_row(provider.capitalize(), cost, speed, privacy, status)

    console.print(table)
    console.print("[dim]* Free tier has rate limits (15-30 requests/min)[/dim]")


def _configure_provider_settings(config, provider: str) -> None:
    """Configure provider-specific settings like API keys and models."""
    if provider == "ollama":
        _configure_ollama(config)
    elif provider == "openai":
        _configure_openai(config)
    elif provider == "anthropic":
        _configure_anthropic(config)
    elif provider == "gemini":
        _configure_gemini(config)
    elif provider == "groq":
        _configure_groq(config)


def _configure_ollama(config) -> None:
    """Configure Ollama settings."""
    console.print("\n[bold]Ollama Configuration:[/bold]")

    # Base URL
    current_url = config.get("llm.ollama.base_url", "http://localhost:11434/api/generate")
    if Confirm.ask(f"Use default Ollama URL? ({current_url})", default=True):
        base_url = current_url
    else:
        base_url = Prompt.ask("Enter Ollama API URL", default=current_url)
    config.set("llm.ollama.base_url", base_url)

    # Model selection
    current_model = config.get("llm.ollama.model", "llama3")
    console.print("\n[dim]Popular Ollama models: llama3, mistral, codellama, phi[/dim]")
    model = Prompt.ask("Enter model name", default=current_model)
    config.set("llm.ollama.model", model)

    console.print("[green]✓[/green] Ollama configured")


def _configure_openai(config) -> None:
    """Configure OpenAI settings."""
    console.print("\n[bold]OpenAI Configuration:[/bold]")

    # API Key
    current_key = config.get("llm.openai.api_key", "")
    if current_key and current_key.startswith("${"):
        # Environment variable reference
        console.print(f"[dim]Current: {current_key}[/dim]")
        env_var = current_key.strip("${}")
        actual_key = os.getenv(env_var, "")
        if actual_key:
            console.print(f"[green]✓[/green] API key found in ${env_var}")
        else:
            console.print(f"[yellow]⚠[/yellow] ${env_var} not set")
    else:
        actual_key = current_key

    if not actual_key or Confirm.ask("Update API key?", default=not actual_key):
        console.print("\n[bold]How would you like to provide your API key?[/bold]")
        console.print("1. Environment variable (recommended)")
        console.print("2. Direct entry (less secure)")

        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")

        if choice == "1":
            env_var = Prompt.ask("Environment variable name", default="OPENAI_API_KEY")
            config.set("llm.openai.api_key", f"${{{env_var}}}")
            console.print(f"[green]✓[/green] Set to use ${env_var}")
            console.print(f"[dim]Remember to set: export {env_var}=sk-...[/dim]")
        else:
            api_key = Prompt.ask("Enter API key", password=True)
            config.set("llm.openai.api_key", api_key)
            console.print("[green]✓[/green] API key saved")

    # Model selection
    current_model = config.get("llm.openai.model", "gpt-4o-mini")
    console.print("\n[dim]Available models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo[/dim]")
    model = Prompt.ask("Enter model name", default=current_model)
    config.set("llm.openai.model", model)

    console.print("[green]✓[/green] OpenAI configured")


def _configure_anthropic(config) -> None:
    """Configure Anthropic settings."""
    console.print("\n[bold]Anthropic Configuration:[/bold]")

    # API Key
    current_key = config.get("llm.anthropic.api_key", "")
    if current_key and current_key.startswith("${"):
        env_var = current_key.strip("${}")
        console.print(f"[dim]Current: {current_key}[/dim]")
        actual_key = os.getenv(env_var, "")
        if actual_key:
            console.print(f"[green]✓[/green] API key found in ${env_var}")
        else:
            console.print(f"[yellow]⚠[/yellow] ${env_var} not set")
    else:
        actual_key = current_key

    if not actual_key or Confirm.ask("Update API key?", default=not actual_key):
        console.print("\n[bold]How would you like to provide your API key?[/bold]")
        console.print("1. Environment variable (recommended)")
        console.print("2. Direct entry (less secure)")

        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")

        if choice == "1":
            env_var = Prompt.ask("Environment variable name", default="ANTHROPIC_API_KEY")
            config.set("llm.anthropic.api_key", f"${{{env_var}}}")
            console.print(f"[green]✓[/green] Set to use ${env_var}")
            console.print(f"[dim]Remember to set: export {env_var}=sk-ant-...[/dim]")
        else:
            api_key = Prompt.ask("Enter API key", password=True)
            config.set("llm.anthropic.api_key", api_key)
            console.print("[green]✓[/green] API key saved")

    # Model selection
    current_model = config.get("llm.anthropic.model", "claude-3-5-sonnet-20241022")
    console.print("\n[dim]Available models: claude-3-5-sonnet-20241022, claude-3-opus-20240229[/dim]")
    model = Prompt.ask("Enter model name", default=current_model)
    config.set("llm.anthropic.model", model)

    console.print("[green]✓[/green] Anthropic configured")


def _configure_gemini(config) -> None:
    """Configure Gemini settings."""
    console.print("\n[bold]Google Gemini Configuration:[/bold]")

    # API Key
    current_key = config.get("llm.gemini.api_key", "")
    if current_key and current_key.startswith("${"):
        env_var = current_key.strip("${}")
        console.print(f"[dim]Current: {current_key}[/dim]")
        actual_key = os.getenv(env_var, "")
        if actual_key:
            console.print(f"[green]✓[/green] API key found in ${env_var}")
        else:
            console.print(f"[yellow]⚠[/yellow] ${env_var} not set")
    else:
        actual_key = current_key

    if not actual_key or Confirm.ask("Update API key?", default=not actual_key):
        console.print("\n[bold]How would you like to provide your API key?[/bold]")
        console.print("1. Environment variable (recommended)")
        console.print("2. Direct entry (less secure)")

        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")

        if choice == "1":
            env_var = Prompt.ask("Environment variable name", default="GEMINI_API_KEY")
            config.set("llm.gemini.api_key", f"${{{env_var}}}")
            console.print(f"[green]✓[/green] Set to use ${env_var}")
            console.print(f"[dim]Remember to set: export {env_var}=...[/dim]")
        else:
            api_key = Prompt.ask("Enter API key", password=True)
            config.set("llm.gemini.api_key", api_key)
            console.print("[green]✓[/green] API key saved")

    # Model selection
    current_model = config.get("llm.gemini.model", "gemini-1.5-flash")
    console.print("\n[dim]Available models: gemini-1.5-pro, gemini-1.5-flash[/dim]")
    model = Prompt.ask("Enter model name", default=current_model)
    config.set("llm.gemini.model", model)

    console.print("[green]✓[/green] Gemini configured")


def _configure_groq(config) -> None:
    """Configure Groq settings."""
    console.print("\n[bold]Groq Configuration:[/bold]")

    # API Key
    current_key = config.get("llm.groq.api_key", "")
    if current_key and current_key.startswith("${"):
        env_var = current_key.strip("${}")
        console.print(f"[dim]Current: {current_key}[/dim]")
        actual_key = os.getenv(env_var, "")
        if actual_key:
            console.print(f"[green]✓[/green] API key found in ${env_var}")
        else:
            console.print(f"[yellow]⚠[/yellow] ${env_var} not set")
    else:
        actual_key = current_key

    if not actual_key or Confirm.ask("Update API key?", default=not actual_key):
        console.print("\n[bold]How would you like to provide your API key?[/bold]")
        console.print("1. Environment variable (recommended)")
        console.print("2. Direct entry (less secure)")

        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")

        if choice == "1":
            env_var = Prompt.ask("Environment variable name", default="GROQ_API_KEY")
            config.set("llm.groq.api_key", f"${{{env_var}}}")
            console.print(f"[green]✓[/green] Set to use ${env_var}")
            console.print(f"[dim]Remember to set: export {env_var}=gsk_...[/dim]")
        else:
            api_key = Prompt.ask("Enter API key", password=True)
            config.set("llm.groq.api_key", api_key)
            console.print("[green]✓[/green] API key saved")

    # Model selection
    current_model = config.get("llm.groq.model", "llama-3.3-70b-versatile")
    console.print("\n[dim]Available models: llama-3.3-70b-versatile, mixtral-8x7b-32768[/dim]")
    model = Prompt.ask("Enter model name", default=current_model)
    config.set("llm.groq.model", model)

    console.print("[green]✓[/green] Groq configured")


def _verify_data_files(config) -> None:
    """Verify that required data files exist."""
    data_dir = Path(config.get("data.directory", "data"))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("File", style="cyan")
    table.add_column("Status")

    # Check for critical files
    files_to_check = [
        ("cards.db", "SQLite database"),
        ("chroma/", "Vector embeddings"),
    ]

    all_exist = True
    for filename, description in files_to_check:
        file_path = data_dir / filename
        exists = file_path.exists()
        all_exist = all_exist and exists

        status = "[green]✓ Found[/green]" if exists else "[yellow]✗ Missing[/yellow]"
        table.add_row(f"{filename} ({description})", status)

    console.print(table)

    if not all_exist:
        console.print("\n[yellow]⚠ Some data files are missing.[/yellow]")
        console.print("\n[bold]Quick Setup Options:[/bold]")
        console.print("1. Download pre-built data bundle (~78 MB, 2-minute setup)")
        console.print("2. Build from scratch (download all cards, ~10 minutes)")
        
        choice = Prompt.ask(
            "\n[bold]Choose setup method[/bold]",
            choices=["1", "2"],
            default="1",
        )
        
        if choice == "1":
            _download_and_extract_bundle(data_dir)
        else:
            console.print("\n[dim]Run 'mtg update' to download card data from Scryfall.[/dim]")
    else:
        console.print("\n[green]✓[/green] All data files present")
        
        # Offer to update to latest cards
        if Confirm.ask("\n[bold]Update to latest cards?[/bold]", default=False):
            _run_incremental_update(data_dir)


def _test_configuration(config, factory) -> None:
    """Test the LLM provider configuration."""
    console.print("\n[bold cyan]🧪 Step 4: Testing Configuration[/bold cyan]")

    provider = config.get("llm.provider", "ollama")

    if not factory.is_provider_available(provider):
        console.print(f"[yellow]⚠ {provider.capitalize()} is not installed. Skipping test.[/yellow]")
        return

    try:
        with console.status(f"[cyan]Testing {provider} connection...[/cyan]", spinner="dots"):
            # Try to create the service
            service = factory.create_provider(provider)
            model = service.get_model_name()

        console.print(f"[green]✓[/green] Successfully connected to {provider.capitalize()}")
        console.print(f"  Model: [bold]{model}[/bold]")

        # Optionally test generation
        if Confirm.ask("\nTest with a sample query?", default=False):
            try:
                with console.status("[cyan]Generating response...[/cyan]", spinner="dots"):
                    response = service.generate("What is a mana curve in Magic: The Gathering? Answer in one sentence.")

                console.print("\n[bold]Sample Response:[/bold]")
                console.print(Panel(response[:200] + ("..." if len(response) > 200 else ""), border_style="green"))
                console.print("[green]✓[/green] Generation test successful!")

            except Exception as e:
                console.print(f"[red]✗ Generation failed:[/red] {e}")
                console.print("[dim]The provider is available but may need configuration.[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Connection failed:[/red] {e}")
        console.print("\n[bold]Troubleshooting tips:[/bold]")

        if provider == "ollama":
            console.print("• Make sure Ollama is running: [bold]ollama serve[/bold]")
            console.print("• Check if the model is pulled: [bold]ollama pull llama3[/bold]")
        else:
            console.print("• Verify your API key is set correctly")
            console.print("• Check your internet connection")
            console.print("• Make sure you have API credits available")


def _download_and_extract_bundle(data_dir: Path) -> None:
    """Download and extract the pre-built data bundle.

    Args:
        data_dir: Directory where data should be extracted

    """
    import json
    import tarfile
    import tempfile

    import requests
    from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, TimeRemainingColumn, TransferSpeedColumn

    console.print("\n[bold cyan]📦 Downloading Data Bundle[/bold cyan]")

    # GitHub release URL (this will need to be updated with actual release)
    # For now, we'll use a placeholder - in production this would point to latest release
    bundle_url = "https://github.com/topherhaynie/mtg_card_app/releases/latest/download/mtg-card-app-data-bundle-latest.tar.xz"

    console.print(f"[dim]Source: {bundle_url}[/dim]")
    console.print("[yellow]Note:[/yellow] Using latest release bundle. You may want to update after extraction.")

    try:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bundle_file = temp_path / "bundle.tar.xz"

            # Download bundle with progress
            console.print("\n[cyan]Downloading...[/cyan]")
            with Progress(
                SpinnerColumn(),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                response = requests.get(bundle_url, stream=True, timeout=60)
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                task = progress.add_task("Downloading bundle...", total=total_size)

                with open(bundle_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

            console.print("[green]✓[/green] Download complete")

            # Extract bundle
            console.print("\n[cyan]Extracting...[/cyan]")
            data_dir.mkdir(parents=True, exist_ok=True)

            with tarfile.open(bundle_file, "r:xz") as tar:
                # Extract all files
                tar.extractall(path=data_dir.parent, filter="data")

            console.print("[green]✓[/green] Extraction complete")

            # Read and display manifest
            manifest_path = data_dir / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)

                console.print("\n[bold]Bundle Info:[/bold]")
                console.print(f"  Version: [cyan]{manifest.get('version', 'unknown')}[/cyan]")
                console.print(f"  Built: [cyan]{manifest.get('build_date', 'unknown')[:10]}[/cyan]")
                console.print(f"  Cards: [cyan]{manifest.get('card_count', 0):,}[/cyan]")
                console.print(f"  Embeddings: [cyan]{manifest.get('embedding_count', 0):,}[/cyan]")

                # Offer incremental update
                console.print("\n[green]✓[/green] Data bundle installed successfully!")

                if Confirm.ask("\n[bold]Update to latest cards now?[/bold]", default=True):
                    _run_incremental_update(data_dir, since_date=manifest.get("last_card_date"))

    except requests.exceptions.RequestException as e:
        console.print(f"\n[red]✗ Download failed:[/red] {e}")
        console.print("\n[bold]Troubleshooting:[/bold]")
        console.print("• Check your internet connection")
        console.print("• The release may not exist yet - run 'mtg update' to build from scratch")
        console.print("• Try again later")
    except Exception as e:
        console.print(f"\n[red]✗ Installation failed:[/red] {e}")
        console.print("\n[bold]Fallback option:[/bold]")
        console.print("  Run 'mtg update' to download cards from Scryfall")


def _run_incremental_update(data_dir: Path, since_date: str | None = None) -> None:
    """Run an incremental update to get the latest cards.

    Args:
        data_dir: Data directory
        since_date: Optional date to update from (YYYY-MM-DD format)

    """
    import subprocess

    console.print("\n[bold cyan]🔄 Running Incremental Update[/bold cyan]")

    # Determine since date
    if not since_date:
        # Try to get from database
        try:
            from mtg_card_app.managers.db.manager import DatabaseManager

            db_manager = DatabaseManager(data_dir=str(data_dir))
            since_date = db_manager.card_service.get_last_update_date()
        except Exception:
            pass

    if since_date:
        console.print(f"[cyan]Updating cards since: {since_date}[/cyan]")
        cmd = ["mtg", "update", "--since", since_date, "--cards-only"]
    else:
        console.print("[cyan]Running full update...[/cyan]")
        cmd = ["mtg", "update"]

    try:
        # Run the update command
        result = subprocess.run(cmd, capture_output=False, check=True)  # noqa: S603

        if result.returncode == 0:
            console.print("[green]✓[/green] Update complete!")
        else:
            console.print("[yellow]⚠[/yellow] Update completed with warnings")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Update failed:[/red] {e}")
        console.print("\n[dim]You can run 'mtg update' manually later.[/dim]")
    except FileNotFoundError:
        console.print("[yellow]⚠[/yellow] Could not run update command")
        console.print("[dim]Run 'mtg update' manually after setup completes.[/dim]")
