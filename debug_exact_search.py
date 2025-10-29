#!/usr/bin/env python3
"""Debug script for exact phrase search."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def debug_isochron_scepter():
    """Debug exact phrase search for Isochron Scepter."""
    print("=" * 80)
    print("DEBUG: Exact Phrase Search for Isochron Scepter")
    print("=" * 80)
    
    # Initialize
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        query_cache=registry.query_cache,
    )
    
    # Fetch Isochron Scepter
    card = interactor.fetch_card("Isochron Scepter")
    if not card:
        print("ERROR: Could not fetch Isochron Scepter")
        return
    
    print(f"\nCard: {card.name}")
    print(f"Oracle Text:\n{card.oracle_text}\n")
    
    # Run exact phrase search
    print("Running _exact_phrase_search()...")
    print("-" * 80)
    results = interactor._exact_phrase_search(card, n_results=10)
    
    print(f"\nFound {len(results)} results:")
    for i, (result_card, score, phrase) in enumerate(results[:10], 1):
        print(f"\n{i}. {result_card.name} (score: {score:.3f})")
        print(f"   Matched phrase: {phrase}")
        print(f"   Oracle: {result_card.oracle_text[:100]}...")

if __name__ == "__main__":
    debug_isochron_scepter()
