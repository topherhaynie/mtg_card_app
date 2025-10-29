#!/usr/bin/env python3
"""Debug why mechanical search sometimes fails."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def debug_mechanical_search():
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    card = interactor.fetch_card('Isochron Scepter')
    
    print("\n" + "="*80)
    print("DEBUGGING MECHANICAL SEARCH")
    print("="*80)
    print(f"\nCard: {card.name}")
    print(f"Type: {card.type_line}")
    print(f"Oracle Text: {card.oracle_text}")
    
    # Run mechanical search 3 times
    for attempt in range(1, 4):
        print(f"\n--- Attempt {attempt} ---")
        
        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)
        print(f"\nLLM Queries generated: {len(llm_analysis['search_queries'])}")
        for i, q in enumerate(llm_analysis['search_queries'][:6], 1):
            print(f"  {i}. {q[:70]}")
        
        mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)
        
        if mechanical_candidates:
            print(f"\n✓ Mechanical search succeeded: {len(mechanical_candidates)} candidates")
            # Check if Dramatic Reversal is in there
            for card_id, (c, score, source) in mechanical_candidates.items():
                if 'Dramatic Reversal' in c.name:
                    print(f"  ✓ Dramatic Reversal found! Score: {score:.3f}")
                    break
            else:
                print(f"  ✗ Dramatic Reversal NOT in candidates")
        else:
            print(f"\n✗ Mechanical search FAILED (returned empty dict)")

if __name__ == "__main__":
    debug_mechanical_search()
