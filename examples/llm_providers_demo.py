"""Demo script for LLM provider system.

This script demonstrates how to use different LLM providers with the MTG Card App.
Run with different providers installed to see the flexibility of the system.

Usage:
    # With only Ollama (default - no extra deps)
    python examples/llm_providers_demo.py

    # With OpenAI installed
    pip install mtg-card-app[openai]
    export OPENAI_API_KEY="sk-..."
    python examples/llm_providers_demo.py --provider openai

    # With all providers
    pip install mtg-card-app[all-providers]
    python examples/llm_providers_demo.py --list
"""

import sys

# Check what providers are available
try:
    from mtg_card_app.managers.llm.services import (
        LLMService,
        OllamaLLMService,
    )

    available_providers = {"ollama": OllamaLLMService}
    print("✅ Base provider (Ollama) is available")
except ImportError as e:
    print(f"❌ Error importing base services: {e}")
    sys.exit(1)

# Try to import optional providers
try:
    from mtg_card_app.managers.llm.services import OpenAILLMService

    available_providers["openai"] = OpenAILLMService
    print("✅ OpenAI provider is available")
except ImportError:
    print("ℹ️  OpenAI provider not installed (pip install mtg-card-app[openai])")

try:
    from mtg_card_app.managers.llm.services import AnthropicLLMService

    available_providers["anthropic"] = AnthropicLLMService
    print("✅ Anthropic provider is available")
except ImportError:
    print("ℹ️  Anthropic provider not installed (pip install mtg-card-app[anthropic])")

try:
    from mtg_card_app.managers.llm.services import GeminiLLMService

    available_providers["gemini"] = GeminiLLMService
    print("✅ Gemini provider is available")
except ImportError:
    print("ℹ️  Gemini provider not installed (pip install mtg-card-app[gemini])")

try:
    from mtg_card_app.managers.llm.services import GroqLLMService

    available_providers["groq"] = GroqLLMService
    print("✅ Groq provider is available")
except ImportError:
    print("ℹ️  Groq provider not installed (pip install mtg-card-app[groq])")


def list_providers():
    """List all available providers."""
    print("\n" + "=" * 60)
    print("Available LLM Providers:")
    print("=" * 60)

    for name, service_class in available_providers.items():
        print(f"\n{name.upper()}")
        print(f"  Class: {service_class.__name__}")
        print(f"  Module: {service_class.__module__}")

        # Try to create instance and get info
        try:
            if name == "ollama":
                service = service_class()
            else:
                # Other providers need API keys, skip instantiation
                print("  Status: Available (requires API key to use)")
                continue

            print(f"  Service: {service.get_service_name()}")
            print(f"  Model: {service.get_model_name()}")
            print(f"  Stats: {service.get_stats()}")
        except Exception as e:
            print("  Status: Import available, instantiation requires configuration")
            print(f"  Error: {e}")


def test_provider(provider_name: str):
    """Test a specific provider with a simple query."""
    if provider_name not in available_providers:
        print(f"❌ Provider '{provider_name}' is not available.")
        print(f"Available providers: {', '.join(available_providers.keys())}")
        return

    print(f"\n{'=' * 60}")
    print(f"Testing {provider_name.upper()} Provider")
    print("=" * 60)

    service_class = available_providers[provider_name]

    try:
        # Create service instance
        if provider_name == "ollama":
            service = service_class(model="llama3")
        elif provider_name == "openai":
            service = service_class(model="gpt-4o-mini")
        elif provider_name == "anthropic":
            service = service_class(model="claude-3-5-sonnet-20241022")
        elif provider_name == "gemini":
            service = service_class(model="gemini-1.5-flash")
        elif provider_name == "groq":
            service = service_class(model="llama-3.1-70b-versatile")
        else:
            service = service_class()

        print(f"✅ Created {service.get_service_name()} service")
        print(f"   Model: {service.get_model_name()}")
        print(f"   Stats: {service.get_stats()}")

        # Test generation
        print("\n🧪 Testing generation...")
        prompt = "What is a mana curve in Magic: The Gathering? (Answer in 1 sentence)"

        response = service.generate(prompt, max_tokens=100)
        print("\n📝 Response:")
        print(f"   {response}")

    except Exception as e:
        print(f"❌ Error testing provider: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Demo LLM provider system")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available providers",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="ollama",
        help="Provider to test (ollama, openai, anthropic, gemini, groq)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test the specified provider",
    )

    args = parser.parse_args()

    if args.list or not args.test:
        list_providers()

    if args.test:
        test_provider(args.provider)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
