#!/usr/bin/env python3
"""Test script for hybrid scoring implementation."""

import sys
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

def test_isochron_scepter():
    """Test if hybrid scoring finds Dramatic Reversal for Isochron Scepter."""
    print("=" * 80)
    print("TESTING HYBRID SCORING - Phase 4.1")
    print("=" * 80)
    print("\nTest Case: Isochron Scepter")
    print("Expected: Should find Dramatic Reversal in top results")
    print("Strategy: 40% semantic + 40% exact phrase + 20% name similarity")
    print("-" * 80)
    
    # Initialize registry and interactor
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        query_cache=registry.query_cache,
    )
    
    # Test combo search
    print("\nSearching for combo pieces...")
    result = interactor.find_combo_pieces(
        card_name="Isochron Scepter",
        n_results=5,
        use_cache=False  # Don't use cache to test fresh results
    )
    
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(result)
    print("\n" + "=" * 80)
    
    # Check if Dramatic Reversal is mentioned
    if "dramatic reversal" in result.lower():
        print("\n✅ SUCCESS: Found Dramatic Reversal!")
    else:
        print("\n⚠️  WARNING: Dramatic Reversal not found in results")
        print("This may indicate exact phrase matching needs tuning.")

if __name__ == "__main__":
    test_isochron_scepter()
