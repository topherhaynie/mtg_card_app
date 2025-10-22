"""Configuration management for MTG Card App.

This module handles reading and writing configuration files, including:
- LLM provider selection
- API keys (with environment variable support)
- Application settings
- Cache configuration
"""

import copy
import os
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10

import tomli_w  # For writing TOML


class Config:
    """Configuration manager for MTG Card App.

    Manages application configuration stored in ~/.mtg/config.toml.
    Supports environment variable substitution for sensitive values like API keys.

    Example config.toml:
        [llm]
        provider = "ollama"
        model = "llama3"

        [llm.ollama]
        base_url = "http://localhost:11434"
        model = "llama3"

        [llm.openai]
        api_key = "${OPENAI_API_KEY}"
        model = "gpt-4o-mini"

        [cache]
        enabled = true
        maxsize = 128

    """

    DEFAULT_CONFIG = {
        "llm": {
            "provider": "ollama",
            "ollama": {
                "base_url": "http://localhost:11434/api/generate",
                "model": "llama3",
            },
            "openai": {
                "api_key": "${OPENAI_API_KEY}",
                "model": "gpt-4o-mini",
                "max_tokens": 1000,
            },
            "anthropic": {
                "api_key": "${ANTHROPIC_API_KEY}",
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
            },
            "gemini": {
                "api_key": "${GOOGLE_API_KEY}",
                "model": "gemini-1.5-flash",
            },
            "groq": {
                "api_key": "${GROQ_API_KEY}",
                "model": "llama-3.1-70b-versatile",
            },
        },
        "cache": {
            "enabled": True,
            "maxsize": 128,
        },
        "data": {
            "directory": "data",
        },
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. If None, uses ~/.mtg/config.toml

        """
        if config_path is None:
            config_path = Path.home() / ".mtg" / "config.toml"

        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file, or create default if not exists."""
        if not self.config_path.exists():
            # Create default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config = copy.deepcopy(self.DEFAULT_CONFIG)
            self._save_config()
        else:
            # Load existing config
            with open(self.config_path, "rb") as f:
                self._config = tomllib.load(f)

    def _save_config(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "wb") as f:
            tomli_w.dump(self._config, f)

    def _resolve_env_var(self, value: Any) -> Any:
        """Resolve environment variable references in config values.

        Supports ${VAR_NAME} syntax.

        Args:
            value: Config value to resolve

        Returns:
            Resolved value with env vars substituted

        Example:
            >>> config._resolve_env_var("${OPENAI_API_KEY}")
            "sk-..."  # Value from environment

        """
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var)
        if isinstance(value, dict):
            return {k: self._resolve_env_var(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_env_var(v) for v in value]
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dotted key path.

        Args:
            key: Dotted key path (e.g., "llm.provider", "llm.openai.api_key")
            default: Default value if key not found

        Returns:
            Configuration value with environment variables resolved

        Example:
            >>> config.get("llm.provider")
            "ollama"
            >>> config.get("llm.openai.api_key")
            "sk-..."  # From environment variable

        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return self._resolve_env_var(value)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dotted key path.

        Args:
            key: Dotted key path (e.g., "llm.provider")
            value: Value to set

        Example:
            >>> config.set("llm.provider", "openai")
            >>> config.set("llm.openai.api_key", "sk-...")

        """
        keys = key.split(".")
        current = self._config

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value
        self._save_config()

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values.

        Returns:
            Deep copy of complete configuration dict

        """
        return copy.deepcopy(self._config)

    def get_provider_config(self, provider: str | None = None) -> dict[str, Any]:
        """Get configuration for a specific LLM provider.

        Args:
            provider: Provider name (e.g., "ollama", "openai").
                     If None, uses the configured default provider.

        Returns:
            Provider-specific configuration with env vars resolved

        Example:
            >>> config.get_provider_config("openai")
            {
                "api_key": "sk-...",
                "model": "gpt-4o-mini",
                "max_tokens": 1000
            }

        """
        if provider is None:
            provider = self.get("llm.provider", "ollama")

        provider_config = self.get(f"llm.{provider}", {})
        return self._resolve_env_var(provider_config)

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults and save."""
        self._config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._save_config()

    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config(path={self.config_path})"


# Global config instance
_config: Config | None = None


def get_config(config_path: Path | None = None) -> Config:
    """Get or create the global configuration instance.

    Args:
        config_path: Path to config file. If None, uses ~/.mtg/config.toml

    Returns:
        Global Config instance

    Example:
        >>> config = get_config()
        >>> provider = config.get("llm.provider")

    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
