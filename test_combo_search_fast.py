#!/usr/bin/env python3
"""Fast combo search test - checks if cards are found WITHOUT full LLM validation.

This isolates the SEARCH phase from the VALIDATION phase, making it quick to:
1. Verify tri-hybrid search is returning expected cards
2. Check if dependencies are loaded correctly
3. Debug search issues without waiting for LLM validation
"""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

# Minimal logging
logging.basicConfig(level=logging.WARNING)

def quick_search_test(base_card_name: str, expected_card_name: str, max_retries: int = 3) -> dict:
    """Quick test that only runs the search phase, no LLM validation.
    
    Args:
        base_card_name: The seed card to search from
        expected_card_name: The card we expect to find
        max_retries: Number of attempts (LLM non-determinism)
        
    Returns:
        Dict with test results
    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    for attempt in range(1, max_retries + 1):
        print(f"  Attempt {attempt}/{max_retries}...", end=" ")
        
        # Fetch the base card
        card = interactor.fetch_card(base_card_name)
        if not card:
            print(f"❌ Base card '{base_card_name}' not found!")
            return {"found": False, "error": "base_card_not_found"}
        
        # Run Step 1: LLM analyzes mechanics
        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)
        
        # Run Step 2: Tri-hybrid search (no validation)
        semantic_candidates = {}
        for search_query in llm_analysis['search_queries'][:6]:
            if not search_query or len(search_query) < 3:
                continue
            results = interactor.rag_manager.search_similar(query=search_query, n_results=5)
            for card_id, score, _metadata in results:
                if card_id == card.id:
                    continue
                if card_id not in semantic_candidates or score > semantic_candidates[card_id][1]:
                    combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                    if combo_card:
                        semantic_candidates[card_id] = (combo_card, score, f"semantic:{search_query[:30]}")
        
        # Exact phrase search
        exact_candidates = {}
        for query in llm_analysis['search_queries'][:6]:
            if not query or len(query) < 5:
                continue
            results = interactor.rag_manager.search_similar(query=query, n_results=10)
            for card_id, score, _metadata in results:
                if card_id == card.id:
                    continue
                combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                if not combo_card or not combo_card.oracle_text:
                    continue
                query_words = set(query.lower().split())
                oracle_words = set(combo_card.oracle_text.lower().split())
                word_overlap = len(query_words & oracle_words) / len(query_words) if query_words else 0
                boosted_score = score * (1.0 + word_overlap)
                if card_id not in exact_candidates or boosted_score > exact_candidates[card_id][1]:
                    exact_candidates[card_id] = (combo_card, boosted_score, f"exact:{query[:30]}")
        
        # Mechanical search
        mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)
        
        # Merge with tri-hybrid scoring
        WEIGHT_SEMANTIC = 0.25
        WEIGHT_EXACT = 0.25
        WEIGHT_MECHANICAL = 0.50
        
        all_candidates = {}
        all_card_ids = set(semantic_candidates.keys()) | set(exact_candidates.keys()) | set(mechanical_candidates.keys())
        
        for card_id in all_card_ids:
            semantic_score = semantic_candidates[card_id][1] if card_id in semantic_candidates else 0.0
            exact_score = exact_candidates[card_id][1] if card_id in exact_candidates else 0.0
            mechanical_score = mechanical_candidates[card_id][1] if card_id in mechanical_candidates else 0.0
            
            weighted_score = (
                semantic_score * WEIGHT_SEMANTIC +
                exact_score * WEIGHT_EXACT +
                mechanical_score * WEIGHT_MECHANICAL
            )
            
            combo_card = None
            if card_id in semantic_candidates:
                combo_card = semantic_candidates[card_id][0]
            elif card_id in exact_candidates:
                combo_card = exact_candidates[card_id][0]
            elif card_id in mechanical_candidates:
                combo_card = mechanical_candidates[card_id][0]
            
            if combo_card:
                all_candidates[card_id] = (combo_card, weighted_score)
        
        # Sort and get top 10
        sorted_candidates = sorted(all_candidates.values(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_candidates[:10]
        
        # Check if expected card is in top 10
        found_cards = [c.name for c, _ in top_10]
        if expected_card_name in found_cards:
            rank = found_cards.index(expected_card_name) + 1
            score = next(s for c, s in top_10 if c.name == expected_card_name)
            print(f"✅ Found at rank #{rank} (score: {score:.3f})")
            return {
                "found": True,
                "rank": rank,
                "score": score,
                "attempt": attempt,
                "top_10": found_cards
            }
        else:
            print(f"❌ Not in top 10")
            if attempt < max_retries:
                print(f"    Top 10: {', '.join(found_cards[:3])}...")
    
    print(f"  ⚠️  Failed after {max_retries} attempts")
    return {
        "found": False,
        "attempts": max_retries,
        "last_top_10": found_cards
    }


def main():
    print("="*80)
    print("FAST Combo Search Test (Search Only, No Validation)")
    print("="*80)
    
    test_cases = [
        {
            "name": "Copy + Untap Loop (OPTIMIZED)",
            "base": "Isochron Scepter",
            "expected": "Dramatic Reversal",
        },
        {
            "name": "Instant Win Condition (NON-OPTIMIZED)",
            "base": "Thassa's Oracle",
            "expected": "Demonic Consultation",
        },
        {
            "name": "Creature Copy Loop (NON-OPTIMIZED)",
            "base": "Kiki-Jiki, Mirror Breaker",
            "expected": "Zealous Conscripts",
        },
    ]
    
    results = []
    for test in test_cases:
        print(f"\n📋 {test['name']}")
        print(f"   {test['base']} → {test['expected']}")
        result = quick_search_test(test['base'], test['expected'], max_retries=3)
        results.append({**test, **result})
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    found_count = sum(1 for r in results if r['found'])
    print(f"\n✅ Found: {found_count}/3 ({found_count/3*100:.0f}%)")
    print(f"❌ Not Found: {3-found_count}/3")
    
    for r in results:
        status = "✅" if r['found'] else "❌"
        if r['found']:
            print(f"{status} {r['name']}: Found at rank #{r['rank']} (attempt {r['attempt']}, score {r['score']:.3f})")
        else:
            print(f"{status} {r['name']}: Not found after {r.get('attempts', 0)} attempts")
    
    print("\n" + "="*80)
    if found_count >= 2:
        print("✅ PASS: System generalizes (≥2/3 combos found)")
    else:
        print("⚠️  CAUTION: May be overfitting to specific patterns")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
