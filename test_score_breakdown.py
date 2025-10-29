#!/usr/bin/env python3
"""Analyze score breakdown for Dramatic Reversal in tri-hybrid search."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

# Minimal logging
logging.basicConfig(level=logging.WARNING)

def analyze_scores():
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    card = interactor.fetch_card('Isochron Scepter')
    llm_analysis = interactor._analyze_card_mechanics_with_llm(card)
    
    print("\n" + "="*80)
    print("SCORE BREAKDOWN ANALYSIS: Isochron Scepter → Dramatic Reversal")
    print("="*80)
    
    # Get all three strategy results
    print("\n1. SEMANTIC SEARCH:")
    semantic_candidates = {}
    for search_query in llm_analysis['search_queries'][:6]:
        if not search_query or len(search_query) < 3:
            continue
        results = interactor.rag_manager.search_similar(query=search_query, n_results=50)
        for card_id, score, _metadata in results:
            if card_id == card.id:
                continue
            combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if combo_card and 'Dramatic Reversal' in combo_card.name:
                if card_id not in semantic_candidates or score > semantic_candidates[card_id][1]:
                    semantic_candidates[card_id] = (combo_card, score, f"semantic:{search_query[:30]}")
                    print(f"   Query: \"{search_query[:50]}\"")
                    print(f"   → Score: {score:.3f}")
    
    if not semantic_candidates:
        print("   ❌ NOT FOUND in semantic search (top 50 per query)")
    
    # Exact phrase search
    print("\n2. EXACT PHRASE SEARCH:")
    exact_candidates = {}
    for query in llm_analysis['search_queries'][:6]:
        if not query or len(query) < 5:
            continue
        results = interactor.rag_manager.search_similar(query=query, n_results=50)
        for card_id, score, _metadata in results:
            if card_id == card.id:
                continue
            combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if not combo_card or not combo_card.oracle_text:
                continue
            if 'Dramatic Reversal' not in combo_card.name:
                continue
            
            query_words = set(query.lower().split())
            oracle_words = set(combo_card.oracle_text.lower().split())
            word_overlap = len(query_words & oracle_words) / len(query_words) if query_words else 0
            boosted_score = score * (1.0 + word_overlap)
            
            if card_id not in exact_candidates or boosted_score > exact_candidates[card_id][1]:
                exact_candidates[card_id] = (combo_card, boosted_score, f"exact:{query[:30]}")
                print(f"   Query: \"{query[:50]}\"")
                print(f"   → Base score: {score:.3f}, Word overlap: {word_overlap:.1%}, Boosted: {boosted_score:.3f}")
    
    if not exact_candidates:
        print("   ❌ NOT FOUND in exact phrase search")
    
    # Mechanical search
    print("\n3. MECHANICAL REQUIREMENTS SEARCH:")
    mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)
    found_mechanical = False
    for card_id, (combo_card, score, source) in mechanical_candidates.items():
        if 'Dramatic Reversal' in combo_card.name:
            found_mechanical = True
            print(f"   ✓ FOUND: {combo_card.name}")
            print(f"   → Score: {score:.3f}")
            print(f"   → Source: {source}")
    
    if not found_mechanical:
        print("   ❌ NOT FOUND in mechanical search")
    
    # Calculate weighted scores
    print("\n" + "="*80)
    print("WEIGHTED SCORE CALCULATION (Current: 40/30/30)")
    print("="*80)
    
    WEIGHT_SEMANTIC = 0.40
    WEIGHT_EXACT = 0.30
    WEIGHT_MECHANICAL = 0.30
    
    # Get scores for Dramatic Reversal
    for card_id in mechanical_candidates.keys():
        combo_card = mechanical_candidates[card_id][0]
        if 'Dramatic Reversal' not in combo_card.name:
            continue
        
        semantic_score = semantic_candidates[card_id][1] if card_id in semantic_candidates else 0.0
        exact_score = exact_candidates[card_id][1] if card_id in exact_candidates else 0.0
        mechanical_score = mechanical_candidates[card_id][1]
        
        weighted_score = (
            semantic_score * WEIGHT_SEMANTIC +
            exact_score * WEIGHT_EXACT +
            mechanical_score * WEIGHT_MECHANICAL
        )
        
        print(f"\n{combo_card.name}:")
        print(f"  Semantic:   {semantic_score:.3f} × {WEIGHT_SEMANTIC} = {semantic_score * WEIGHT_SEMANTIC:.3f}")
        print(f"  Exact:      {exact_score:.3f} × {WEIGHT_EXACT} = {exact_score * WEIGHT_EXACT:.3f}")
        print(f"  Mechanical: {mechanical_score:.3f} × {WEIGHT_MECHANICAL} = {mechanical_score * WEIGHT_MECHANICAL:.3f}")
        print(f"  ───────────────────────────────────────")
        print(f"  TOTAL:      {weighted_score:.3f}")
    
    # Now test alternative weights
    print("\n" + "="*80)
    print("ALTERNATIVE WEIGHT SCENARIOS")
    print("="*80)
    
    scenarios = [
        ("Current", 0.40, 0.30, 0.30),
        ("Mechanical Heavy", 0.20, 0.20, 0.60),
        ("Balanced", 0.33, 0.33, 0.34),
        ("Semantic Low", 0.25, 0.35, 0.40),
        ("Discovery Focus", 0.50, 0.25, 0.25),
    ]
    
    for card_id in mechanical_candidates.keys():
        combo_card = mechanical_candidates[card_id][0]
        if 'Dramatic Reversal' not in combo_card.name:
            continue
        
        semantic_score = semantic_candidates[card_id][1] if card_id in semantic_candidates else 0.0
        exact_score = exact_candidates[card_id][1] if card_id in exact_candidates else 0.0
        mechanical_score = mechanical_candidates[card_id][1]
        
        print(f"\nDramatic Reversal scores under different weights:")
        for name, w_sem, w_exact, w_mech in scenarios:
            weighted = semantic_score * w_sem + exact_score * w_exact + mechanical_score * w_mech
            print(f"  {name:20s} ({w_sem:.2f}/{w_exact:.2f}/{w_mech:.2f}): {weighted:.3f}")

if __name__ == "__main__":
    analyze_scores()
