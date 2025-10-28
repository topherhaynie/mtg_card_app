"""Interactive chat mode for MTG Card App.

This module provides a conversational REPL interface where users can ask
questions and get responses powered by the LLM and RAG system.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from mtg_card_app.core.conversation import ConversationHistory
from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.ui.cli.card_display import (
    create_card_reference_guide,
    display_card_results,
)

console = Console()


def start_chat(single_query: str | None = None) -> None:
    """Start interactive chat mode.

    Args:
        single_query: If provided, ask this question and exit (single-shot mode)

    """
    # Initialize the interactor
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    # Initialize conversation history
    conversation = ConversationHistory(max_turns=5)

    # Get system stats for welcome message
    stats = interactor.get_system_stats()

    if single_query:
        # Single-shot mode
        _handle_query(interactor, single_query, conversation)
        return

    # Interactive mode - show welcome
    _show_welcome(stats)

    try:
        while True:
            # Get user input
            try:
                user_input = Prompt.ask("\n[bold cyan]>[/bold cyan]", console=console)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Goodbye! ✨[/yellow]")
                break

            # Handle empty input
            if not user_input.strip():
                continue

            # Handle special commands
            if user_input.startswith("/"):
                if _handle_special_command(user_input, conversation):
                    break  # Exit if command returns True
                continue

            # Handle regular query
            _handle_query(interactor, user_input, conversation)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("[yellow]Chat session ended.[/yellow]")


def _show_welcome(stats: dict) -> None:
    """Show welcome message with system info.

    Args:
        stats: System statistics from interactor

    """
    # Extract nested stats
    llm_stats = stats.get("llm", {})
    card_stats = stats.get("card_data", {})

    llm_provider = llm_stats.get("provider", "Unknown")
    llm_model = llm_stats.get("model", "Unknown")
    total_cards = card_stats.get("total_cards", 0) if card_stats else 0

    welcome_text = f"""
🎴 **MTG Card App - Chat Mode**

Connected to: **{llm_provider}** ({llm_model})
Cards loaded: **{total_cards:,}**

Ask me anything about Magic: The Gathering cards!
Type `/help` for commands, `/exit` to quit.
    """

    console.print(Panel(Markdown(welcome_text.strip()), border_style="cyan"))


def _handle_query(interactor: Interactor, query: str, conversation: ConversationHistory) -> None:
    """Handle a user query and display the response.

    Args:
        interactor: The interactor instance
        query: User's question
        conversation: Conversation history manager

    """
    try:
        # Add user message to history
        conversation.add_user_message(query)
        
        with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
            cards_with_scores, response = interactor.answer_query_with_cards(
                query,
                conversation_history=conversation.get_messages()
            )

        # Display cards first if any were found
        if cards_with_scores:
            display_card_results(cards_with_scores, console, title="Found Cards")
            create_card_reference_guide(len(cards_with_scores), console)

        # Display the LLM response
        console.print("[bold green]Response:[/bold green]")
        console.print(Markdown(response))
        
        # Add assistant response to history
        conversation.add_assistant_message(response)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")


def _handle_special_command(command: str, conversation: ConversationHistory) -> bool:
    """Handle special slash commands.

    Args:
        command: The command string (starting with /)
        conversation: Conversation history manager

    Returns:
        True if should exit chat, False otherwise

    """
    cmd = command.lower().strip()

    if cmd in ["/exit", "/quit", "/q"]:
        console.print("[yellow]Goodbye! ✨[/yellow]")
        return True

    if cmd == "/help":
        _show_help()
        return False

    if cmd == "/clear":
        console.clear()
        conversation.clear()
        console.print("[green]Screen and conversation history cleared![/green]")
        return False
    
    if cmd == "/history":
        _show_history(conversation)
        return False

    console.print(f"[yellow]Unknown command: {command}[/yellow]")
    console.print("Type [bold]/help[/bold] for available commands.")
    return False


def _show_help() -> None:
    """Show help message with available commands."""
    help_text = """
**Available Commands:**

- `/help` - Show this help message
- `/history` - Show conversation history
- `/clear` - Clear the screen and conversation history
- `/exit` or `/quit` - Exit chat mode

**Example Questions:**

- "Show me blue counterspells under $5"
- "What combos work with Thassa's Oracle?"
- "Find cards similar to Sol Ring"
- "What's the best removal in black?"

**Follow-up Questions:**

The assistant remembers your last 5 conversation turns, so you can ask follow-up questions:
- "Tell me more about that first card"
- "How does that combo work?"
- "What other cards work with it?"
    """

    console.print(Panel(Markdown(help_text.strip()), title="Help", border_style="yellow"))


def _show_history(conversation: ConversationHistory) -> None:
    """Show conversation history.
    
    Args:
        conversation: Conversation history manager
    """
    messages = conversation.get_messages()
    
    if not messages:
        console.print("[yellow]No conversation history yet. Start asking questions![/yellow]")
        return
    
    turn_count = conversation.get_turn_count()
    max_turns = conversation.max_turns
    
    history_lines = [f"**Conversation History** ({turn_count} of {max_turns} turns)\n"]
    
    for idx, msg in enumerate(messages, 1):
        role = msg["role"].capitalize()
        content = msg["content"]
        
        # Truncate long messages for display
        if len(content) > 150:
            content = content[:147] + "..."
        
        history_lines.append(f"**{idx}. {role}:** {content}\n")
    
    console.print(Panel(
        Markdown("\n".join(history_lines)), 
        title="History", 
        border_style="blue"
    ))
