#!/usr/bin/env python3
"""Test re-vectorization results - does it find Dramatic Reversal now?"""

from mtg_card_app.core.manager_registry import ManagerRegistry

def test_dramatic_reversal_findability():
    """Test if enriched embeddings help find Dramatic Reversal."""
    print("=" * 80)
    print("TESTING RE-VECTORIZATION RESULTS")
    print("=" * 80)
    
    registry = ManagerRegistry.get_instance()
    
    test_queries = [
        "instant untap permanents",
        "instant mass untap",
        "instant untap mana value 2",
        "instant untap nonland",
        "Dramatic Reversal untap",
    ]
    
    total_tests = len(test_queries)
    found_count = 0
    
    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 80)
        
        results = registry.rag_manager.search_similar(query=query, n_results=5)
        found_in_top_5 = False
        
        for i, (card_id, score, _meta) in enumerate(results, 1):
            card = registry.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if card:
                is_dramatic = "dramatic reversal" in card.name.lower()
                marker = " ⭐⭐⭐ FOUND!" if is_dramatic else ""
                print(f"  {i}. {card.name} (score={score:.3f}){marker}")
                if is_dramatic:
                    found_in_top_5 = True
                    found_count += 1
        
        if not found_in_top_5:
            print("  ❌ Dramatic Reversal NOT in top 5")
    
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Queries tested: {total_tests}")
    print(f"Dramatic Reversal found: {found_count}/{total_tests} ({found_count/total_tests*100:.0f}%)")
    
    if found_count >= total_tests * 0.6:  # 60% success rate
        print("\n✅ SUCCESS! Re-vectorization significantly improved findability!")
    elif found_count >= total_tests * 0.4:  # 40% success rate
        print("\n⚠️  PARTIAL SUCCESS: Improvement but still needs work")
    else:
        print("\n❌ FAILED: Re-vectorization did not improve findability enough")
    
    # Now test the full combo search
    print("\n" + "=" * 80)
    print("TESTING FULL COMBO SEARCH: Isochron Scepter")
    print("=" * 80)
    
    from mtg_card_app.core.interactor import Interactor
    
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        query_cache=registry.query_cache,
    )
    
    result = interactor.find_combo_pieces("Isochron Scepter", n_results=5, use_cache=False)
    
    if "dramatic reversal" in result.lower():
        print("\n✅ DRAMATIC REVERSAL FOUND IN COMBO RESULTS!")
        print("\nExtract mentioning Dramatic Reversal:")
        # Find the section mentioning Dramatic Reversal
        lines = result.split('\n')
        for i, line in enumerate(lines):
            if 'dramatic reversal' in line.lower():
                # Print context around the match
                start = max(0, i-2)
                end = min(len(lines), i+8)
                print('\n'.join(lines[start:end]))
                break
    else:
        print("\n❌ Dramatic Reversal STILL NOT in combo results")
        print("\nShowing first few results:")
        print(result[:500] + "...")

if __name__ == "__main__":
    test_dramatic_reversal_findability()
