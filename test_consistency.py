#!/usr/bin/env python3
"""Test consistency of Dramatic Reversal appearing in top N results."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

logging.basicConfig(level=logging.WARNING)

def test_consistency(num_trials=5):
    """Run multiple trials to check Dramatic Reversal consistency."""
    
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    print("="*80)
    print(f"CONSISTENCY TEST: Isochron Scepter → Dramatic Reversal")
    print(f"Running {num_trials} trials with optimized weights (25/35/40)")
    print("="*80)
    
    results = {
        'found_top_5': 0,
        'found_top_10': 0,
        'found_top_20': 0,
        'not_found': 0,
        'ranks': [],
        'scores': []
    }
    
    for trial in range(1, num_trials + 1):
        print(f"\n--- Trial {trial}/{num_trials} ---")
        
        # Get top 20 to check ranking
        card = interactor.fetch_card('Isochron Scepter')
        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)
        
        # Get all three strategies
        semantic_candidates = {}
        for search_query in llm_analysis['search_queries'][:6]:
            if not search_query or len(search_query) < 3:
                continue
            results_list = interactor.rag_manager.search_similar(query=search_query, n_results=5)
            for card_id, score, _metadata in results_list:
                if card_id == card.id:
                    continue
                if card_id not in semantic_candidates or score > semantic_candidates[card_id][1]:
                    combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                    if combo_card:
                        semantic_candidates[card_id] = (combo_card, score, f"semantic")
        
        exact_candidates = {}
        for query in llm_analysis['search_queries'][:6]:
            if not query or len(query) < 5:
                continue
            results_list = interactor.rag_manager.search_similar(query=query, n_results=10)
            for card_id, score, _metadata in results_list:
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
                    exact_candidates[card_id] = (combo_card, boosted_score, f"exact")
        
        mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)
        
        # Merge
        WEIGHT_SEMANTIC = 0.25
        WEIGHT_EXACT = 0.35
        WEIGHT_MECHANICAL = 0.40
        
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
        
        # Sort and find Dramatic Reversal
        sorted_candidates = sorted(all_candidates.values(), key=lambda x: x[1], reverse=True)
        
        dramatic_rank = None
        dramatic_score = None
        for rank, (combo_card, score) in enumerate(sorted_candidates[:20], 1):
            if 'Dramatic Reversal' in combo_card.name:
                dramatic_rank = rank
                dramatic_score = score
                break
        
        if dramatic_rank:
            print(f"✓ Dramatic Reversal: Rank #{dramatic_rank}, Score: {dramatic_score:.3f}")
            results['ranks'].append(dramatic_rank)
            results['scores'].append(dramatic_score)
            if dramatic_rank <= 5:
                results['found_top_5'] += 1
            if dramatic_rank <= 10:
                results['found_top_10'] += 1
            if dramatic_rank <= 20:
                results['found_top_20'] += 1
        else:
            print("✗ Dramatic Reversal: NOT in top 20")
            results['not_found'] += 1
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Found in top 5:  {results['found_top_5']}/{num_trials} ({results['found_top_5']/num_trials*100:.0f}%)")
    print(f"Found in top 10: {results['found_top_10']}/{num_trials} ({results['found_top_10']/num_trials*100:.0f}%)")
    print(f"Found in top 20: {results['found_top_20']}/{num_trials} ({results['found_top_20']/num_trials*100:.0f}%)")
    print(f"Not found:       {results['not_found']}/{num_trials} ({results['not_found']/num_trials*100:.0f}%)")
    
    if results['ranks']:
        avg_rank = sum(results['ranks']) / len(results['ranks'])
        avg_score = sum(results['scores']) / len(results['scores'])
        print(f"\nAverage rank: {avg_rank:.1f}")
        print(f"Average score: {avg_score:.3f}")
        print(f"Rank range: {min(results['ranks'])} to {max(results['ranks'])}")

if __name__ == "__main__":
    test_consistency(num_trials=5)
