"""Demo script showcasing combo detection capabilities.

Usage:
    python examples/combo_demo.py
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.core.orchestrator import QueryOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def demo_combo_detection():
    """Demonstrate combo detection functionality."""
    print("=" * 80)
    print("MTG CARD APP - COMBO DETECTION DEMO")
    print("=" * 80)
    print()

    # Initialize orchestrator
    orchestrator = QueryOrchestrator()

    # Demo 1: Famous infinite combo - Isochron Scepter + Dramatic Reversal
    print("🔥 DEMO 1: Isochron Scepter Combos")
    print("-" * 80)
    print("Finding combos for: Isochron Scepter")
    print()

    response = orchestrator.find_combos("Isochron Scepter", n_results=3)
    print(response)
    print()
    print("=" * 80)
    print()

    # Demo 2: cEDH win condition - Thassa's Oracle
    print("🏆 DEMO 2: Thassa's Oracle Combos")
    print("-" * 80)
    print("Finding combos for: Thassa's Oracle")
    print()

    response = orchestrator.find_combos("Thassa's Oracle", n_results=3)
    print(response)
    print()
    print("=" * 80)
    print()

    # Demo 3: Card advantage engine - Rhystic Study
    print("📚 DEMO 3: Rhystic Study Synergies")
    print("-" * 80)
    print("Finding synergies for: Rhystic Study")
    print()

    response = orchestrator.find_combos("Rhystic Study", n_results=3)
    print(response)
    print()
    print("=" * 80)
    print()

    # Demo 4: Interactive query - Counterspell
    print("🛡️ DEMO 4: Counterspell Support")
    print("-" * 80)
    print("Finding synergies for: Counterspell")
    print()

    response = orchestrator.find_combos("Counterspell", n_results=3)
    print(response)
    print()
    print("=" * 80)
    print()

    print("✅ COMBO DETECTION DEMO COMPLETE!")
    print()
    print("Key Features Demonstrated:")
    print("  • Semantic search for synergistic cards")
    print("  • LLM-powered combo explanation")
    print("  • Power level assessment")
    print("  • Additional pieces identification")
    print()


if __name__ == "__main__":
    demo_combo_detection()
