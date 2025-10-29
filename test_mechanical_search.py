#!/usr/bin/env python3
"""Test the new mechanical requirements search for finding Dramatic Reversal with Isochron Scepter."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_mechanical_search():
    """Test that Isochron Scepter finds Dramatic Reversal via mechanical requirements."""
    
    print("="*80)
    print("Testing Mechanical Requirements Search")
    print("="*80)
    
    # Initialize
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    # Test with Isochron Scepter
    print("\n🔍 Searching for combos with Isochron Scepter...")
    print("-"*80)
    
    result = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)
    
    print("\n📊 RESULTS:")
    print("="*80)
    print(result)
    print("="*80)
    
    # Check if Dramatic Reversal is mentioned
    if "Dramatic Reversal" in result:
        print("\n✅ SUCCESS! Dramatic Reversal was found!")
    else:
        print("\n❌ FAILED! Dramatic Reversal was NOT found.")
        print("\nThis might mean:")
        print("1. The LLM didn't extract requirements correctly")
        print("2. The mechanical search didn't find it")
        print("3. It was found but scored too low to make top 10")

if __name__ == "__main__":
    test_mechanical_search()
