"""Demo script for configuration system and provider factory.

This script demonstrates:
1. Configuration management (reading/writing config files)
2. Provider factory (creating LLM providers from config)
3. Environment variable support for API keys
4. Checking available providers

Usage:
    # Show current configuration
    python examples/config_demo.py --show

    # Set provider
    python examples/config_demo.py --set-provider ollama

    # Test provider creation
    python examples/config_demo.py --test

    # List available providers
    python examples/config_demo.py --list

"""

import argparse
import sys

from mtg_card_app.config import ProviderFactory, get_config


def show_config():
    """Display current configuration."""
    config = get_config()

    print("\n" + "=" * 60)
    print("Current Configuration")
    print("=" * 60)
    print(f"Config file: {config.config_path}")
    print(f"Exists: {config.config_path.exists()}")

    print("\n[LLM Provider Settings]")
    provider = config.get("llm.provider")
    print(f"Active provider: {provider}")

    print("\n[Provider Configurations]")
    providers = ["ollama", "openai", "anthropic", "gemini", "groq"]
    for p in providers:
        print(f"\n{p.upper()}:")
        provider_config = config.get_provider_config(p)
        for key, value in provider_config.items():
            # Mask API keys for security
            if "api_key" in key and value:
                if value.startswith("${"):
                    print(f"  {key}: {value} (from environment)")
                else:
                    print(f"  {key}: {'*' * 10} (set)")
            else:
                print(f"  {key}: {value}")

    print("\n[Cache Settings]")
    print(f"Enabled: {config.get('cache.enabled')}")
    print(f"Max size: {config.get('cache.maxsize')}")

    print("\n[Data Settings]")
    print(f"Directory: {config.get('data.directory')}")


def list_available_providers():
    """List providers that are available (dependencies installed)."""
    config = get_config()
    factory = ProviderFactory(config)

    available = factory.get_available_providers()

    print("\n" + "=" * 60)
    print("Available LLM Providers")
    print("=" * 60)

    all_providers = ["ollama", "openai", "anthropic", "gemini", "groq"]

    for provider in all_providers:
        is_available = provider in available
        status = "✅ Available" if is_available else "❌ Not installed"

        print(f"\n{provider.upper()}: {status}")

        if not is_available and provider != "ollama":
            print(f"  Install with: pip install mtg-card-app[{provider}]")

        # Show if it's configured
        provider_config = config.get_provider_config(provider)
        api_key = provider_config.get("api_key")
        if api_key and not api_key.startswith("${"):
            print("  API key: configured")
        elif api_key and api_key.startswith("${"):
            import os

            env_var = api_key[2:-1]
            if os.environ.get(env_var):
                print(f"  API key: found in ${env_var}")
            else:
                print(f"  API key: ${env_var} not set")


def set_provider(provider: str):
    """Set the active LLM provider."""
    valid_providers = ["ollama", "openai", "anthropic", "gemini", "groq"]

    if provider not in valid_providers:
        print(f"❌ Error: Invalid provider '{provider}'")
        print(f"Valid providers: {', '.join(valid_providers)}")
        sys.exit(1)

    config = get_config()
    config.set("llm.provider", provider)

    print(f"✅ Set active provider to: {provider}")
    print(f"Config saved to: {config.config_path}")


def test_provider_creation():
    """Test creating the configured provider."""
    config = get_config()
    factory = ProviderFactory(config)

    provider_name = config.get("llm.provider")

    print("\n" + "=" * 60)
    print(f"Testing Provider: {provider_name.upper()}")
    print("=" * 60)

    try:
        print(f"\n🔨 Creating {provider_name} service...")
        service = factory.create_provider()

        print(f"✅ Successfully created {service.get_service_name()} service")
        print(f"   Model: {service.get_model_name()}")
        print(f"   Stats: {service.get_stats()}")

        # Try to generate (with timeout to avoid hanging)
        print("\n🧪 Testing generation...")
        print("   Prompt: 'What is a mana curve?' (50 tokens max)")

        try:
            response = service.generate(
                "What is a mana curve in Magic: The Gathering? Answer in 1 sentence.",
                max_tokens=50,
            )
            print("\n📝 Response:")
            print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
            print("\n✅ Provider test successful!")
        except Exception as e:
            print(f"\n⚠️  Generation failed: {e}")
            print("   (This may be expected if service is not running or API key is missing)")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Install the provider with:")
        print(f"   pip install mtg-card-app[{provider_name}]")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error creating provider: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def reset_config():
    """Reset configuration to defaults."""
    config = get_config()
    config.reset_to_defaults()

    print("✅ Configuration reset to defaults")
    print(f"Config file: {config.config_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Demo configuration system and provider factory",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available providers",
    )
    parser.add_argument(
        "--set-provider",
        type=str,
        metavar="PROVIDER",
        help="Set active provider (ollama, openai, anthropic, gemini, groq)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test creating and using the configured provider",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to defaults",
    )

    args = parser.parse_args()

    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    # Execute commands
    if args.show:
        show_config()

    if args.list:
        list_available_providers()

    if args.set_provider:
        set_provider(args.set_provider)

    if args.test:
        test_provider_creation()

    if args.reset:
        reset_config()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
