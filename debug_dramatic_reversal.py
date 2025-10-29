#!/usr/bin/env python3
"""Debug: Check if Dramatic Reversal appears in ANY of the search strategies."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry  
from mtg_card_app.core.interactor import Interactor

logging.basicConfig(level=logging.INFO, format='%(message)s')

def check_for_dramatic_reversal():
    print("=" * 80)
    print("Checking if Dramatic Reversal appears in search results...")
    print("=" * 80)
    
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    card = interactor.fetch_card("Isochron Scepter")
    
    # Get LLM analysis
    analysis = interactor._analyze_card_mechanics_with_llm(card)
    print(f"\nLLM Queries: {analysis['search_queries'][:6]}\n")
    
    # Test each query to see if it finds Dramatic Reversal
    print("Testing each LLM query...")
    print("-" * 80)
    
    for i, query in enumerate(analysis['search_queries'][:6], 1):
        print(f"\n{i}. Query: \"{query}\"")
        results = registry.rag_manager.search_similar(query=query, n_results=20)
        
        found_dramatic = False
        for card_id, score, _meta in results:
            test_card = registry.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if test_card and "dramatic reversal" in test_card.name.lower():
                print(f"   ✅ FOUND Dramatic Reversal! (rank in top 20, score={score:.3f})")
                found_dramatic = True
                break
        
        if not found_dramatic:
            print(f"   ❌ Dramatic Reversal NOT in top 20")
    
    # Also test direct search
    print("\n" + "=" * 80)
    print("Direct test: Searching for 'untap all nonland permanents'")
    print("=" * 80)
    results = registry.rag_manager.search_similar(query="untap all nonland permanents", n_results=10)
    for i, (card_id, score, _meta) in enumerate(results, 1):
        test_card = registry.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
        if test_card:
            print(f"{i}. {test_card.name} (score={score:.3f})")
            if "dramatic reversal" in test_card.name.lower():
                print("   ⭐ THIS IS DRAMATIC REVERSAL!")

if __name__ == "__main__":
    check_for_dramatic_reversal()
