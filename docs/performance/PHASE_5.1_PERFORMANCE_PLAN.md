# Phase 5.1: Performance Optimization Plan

**Date:** October 21, 2025  
**Status:** 🚧 In Progress  
**Goal:** Optimize deck suggestion performance with caching, batching, and async operations

---

## Current Performance Baseline

### Known Metrics (from development)
- **Basic suggestion** (RAG search only): ~100-500ms
- **With combo detection**: ~500-2000ms (depends on deck size)
- **With LLM explanations**: +1-3s per combo (sequential)
- **Export operations**: 1-10ms (negligible)

### Performance Bottlenecks (Expected)

1. **Combo Detection** - O(n*m) where n=suggestions, m=deck cards
   - Searches database for each card combination
   - No caching of results
   - Sequential processing

2. **LLM Explanations** - Blocking sequential calls
   - Each combo explanation takes 1-3s
   - Blocks entire suggestion process
   - No batching or async

3. **RAG Searches** - Multiple embedding lookups
   - No result caching
   - Repeated queries for same cards
   - No batch operations

4. **Database Queries** - Multiple round trips
   - Card lookups one at a time
   - Combo searches not batched
   - No query result caching

---

## Optimization Strategy

### Phase 1: Benchmarking (First)
- Create performance test suite
- Measure current baseline accurately
- Identify actual bottlenecks with profiling
- Validate assumptions about slow operations

### Phase 2: Quick Wins (High Impact, Low Effort)
1. **Result Caching**
   - Cache combo search results by card pair
   - Cache RAG search results by query
   - LRU cache with configurable size
   - Deck hash for cache invalidation

2. **Query Batching**
   - Batch card lookups
   - Batch combo searches where possible
   - Reduce database round trips

### Phase 3: Async Operations (Medium Effort)
1. **Async LLM Calls**
   - Generate explanations in parallel
   - Don't block suggestion flow
   - Configurable concurrency limit

2. **Async Combo Detection**
   - Parallel combo searches
   - Gather results asynchronously
   - Much faster for large decks

### Phase 4: Advanced Optimizations (If Needed)
1. **Precomputation**
   - Popular combo index
   - Format-specific combo caches
   - Commander synergy maps

2. **Streaming Results**
   - Return top-N immediately
   - Continue processing in background
   - Progressive enhancement

3. **Smart Limiting**
   - Early termination when enough results
   - Configurable depth vs speed trade-off
   - User-controlled performance profile

---

## Performance Targets

### Before Optimization (Current)
- Suggest 10 cards: 500-2000ms
- With explanations: 2000-5000ms
- Large deck (100 cards): 3000-6000ms

### After Optimization (Target)
- Suggest 10 cards: 200-500ms (2-4x faster)
- With explanations: 800-1500ms (2-3x faster)
- Large deck (100 cards): 1000-2000ms (3x faster)
- Cached queries: <100ms (10x faster)

### Stretch Goals
- Sub-second suggestions (cached): <100ms
- First results streaming: <200ms
- Background explanation generation: Non-blocking

---

## Implementation Plan

### Step 1: Benchmarking Infrastructure ⏳
- [ ] Create `scripts/benchmark_performance.py`
- [ ] Add performance test fixtures
- [ ] Measure baseline performance
- [ ] Profile with cProfile
- [ ] Identify actual bottlenecks

### Step 2: Caching Layer ⏳
- [ ] Create `utils/suggestion_cache.py`
- [ ] Implement LRU cache for combo results
- [ ] Add deck hash for cache keys
- [ ] Cache RAG search results
- [ ] Add cache statistics/monitoring

### Step 3: Query Batching ⏳
- [ ] Batch card lookups in `suggest_cards`
- [ ] Batch combo searches where possible
- [ ] Optimize database queries
- [ ] Add query timing logs

### Step 4: Async Operations ⏳
- [ ] Make LLM explanation generation async
- [ ] Parallel combo detection
- [ ] Async RAG searches
- [ ] Add concurrency controls

### Step 5: Validation & Documentation ⏳
- [ ] Re-run benchmarks
- [ ] Validate performance improvements
- [ ] Update documentation
- [ ] Add performance tuning guide

---

## Success Metrics

- [ ] 2-4x faster suggestions (measured)
- [ ] <100ms for cached queries
- [ ] LLM explanations don't block
- [ ] All existing tests still pass
- [ ] No breaking API changes
- [ ] Performance tuning guide written

---

## Risk Management

### Technical Risks
1. **Cache Invalidation** - Stale results if not handled properly
   - Mitigation: Use deck hash, TTL expiration
   
2. **Memory Usage** - Large caches could consume too much memory
   - Mitigation: LRU eviction, configurable size limits
   
3. **Race Conditions** - Async operations could cause issues
   - Mitigation: Proper locking, immutable data structures

4. **Complexity** - Added complexity could introduce bugs
   - Mitigation: Comprehensive testing, gradual rollout

---

## Next Steps

1. Create benchmarking script
2. Establish baseline metrics
3. Profile to identify bottlenecks
4. Implement caching layer (Quick Win #1)
5. Add batching (Quick Win #2)
6. Async operations (if needed)

Let's start with Step 1: Benchmarking! 🚀
