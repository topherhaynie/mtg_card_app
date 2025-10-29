#!/usr/bin/env python3
"""Debug LLM query generation."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

# Enable info logging only
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def debug_llm_queries():
    """Check what queries the LLM generates for Isochron Scepter."""
    print("=" * 80)
    print("DEBUG: LLM Query Generation for Isochron Scepter")
    print("=" * 80)
    
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    card = interactor.fetch_card("Isochron Scepter")
    print(f"\nCard: {card.name}")
    print(f"Oracle Text: {card.oracle_text}\n")
    
    print("Running LLM analysis...")
    print("-" * 80)
    analysis = interactor._analyze_card_mechanics_with_llm(card)
    
    print(f"\nLLM Generated {len(analysis['search_queries'])} queries:\n")
    for i, query in enumerate(analysis['search_queries'], 1):
        print(f"{i}. \"{query}\"")
    
    print("\n" + "=" * 80)
    print("CHECKING: Does any query contain 'untap all' or 'untap nonland'?")
    print("=" * 80)
    
    found_untap = False
    for query in analysis['search_queries']:
        if 'untap all' in query.lower() or 'untap nonland' in query.lower():
            print(f"✅ FOUND: \"{query}\"")
            found_untap = True
    
    if not found_untap:
        print("⚠️  NO untap-all queries generated!")
        print("The LLM needs to understand that Isochron Scepter combos with cards that untap it.")

if __name__ == "__main__":
    debug_llm_queries()
