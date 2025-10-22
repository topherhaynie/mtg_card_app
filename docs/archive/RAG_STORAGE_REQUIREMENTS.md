# Phase 2: RAG Integration - Storage Requirements

## Overview

RAG (Retrieval-Augmented Generation) will enable semantic search across MTG cards using vector embeddings. This document provides detailed storage estimates.

## Storage Components

### 1. Vector Database (ChromaDB)

**What it stores:**
- Card embeddings (vector representations of card text)
- Metadata (card names, IDs, types, etc.)
- Index structures for fast similarity search

**Storage Calculation:**

```
For a single card:
- Embedding vector: ~3,072 floats (using sentence-transformers/all-MiniLM-L6-v2)
  - 3,072 * 4 bytes = 12,288 bytes = 12 KB per card
- Metadata: ~1 KB per card (names, IDs, types, colors)
- Index overhead: ~20% additional

Total per card: ~16 KB
```

**Estimates by collection size:**

| # of Cards | Embeddings | Metadata | Index | **Total** |
|------------|------------|----------|-------|-----------|
| 100        | 1.2 MB     | 0.1 MB   | 0.3 MB | **~1.6 MB** |
| 1,000      | 12 MB      | 1 MB     | 2.6 MB | **~16 MB** |
| 10,000     | 120 MB     | 10 MB    | 26 MB  | **~156 MB** |
| 27,000     | 324 MB     | 27 MB    | 70 MB  | **~421 MB** |

*Note: MTG has ~27,000 unique cards (oracle), ~90,000 total printings*

**Recommended allocations:**
- **Development/Testing**: 50 MB (store ~100-1000 cards)
- **Small Collection**: 200 MB (store ~2,000-3,000 popular cards)
- **Full Oracle Cards**: 500 MB (all unique cards)
- **All Printings**: 2 GB (every printing variation)

### 2. Embedding Model

**Model: sentence-transformers/all-MiniLM-L6-v2**
- Model size: **~80 MB** (one-time download)
- Cached in: `~/.cache/huggingface/` or `.venv/`
- Fast, efficient, runs on CPU

**Alternative models:**
- `all-MiniLM-L12-v2`: 120 MB (more accurate)
- `all-mpnet-base-v2`: 420 MB (best quality)

### 3. ChromaDB Data Directory

**Structure:**
```
data/
├── chroma/                    # ChromaDB data
│   ├── chroma.sqlite3         # Metadata database (~5-50 MB)
│   └── [collection_id]/       # Vector storage
│       ├── data_level0.bin    # Embeddings
│       ├── index_metadata.pkl # Index info
│       └── ...
```

**Growth pattern:**
- Starts at ~1 MB (empty)
- Grows ~16 KB per card added
- Plateaus once all cards are embedded

### 4. Card Data Cache (JSON)

**Already exists:**
```
data/
├── cards.json                 # ~2 KB per card
└── combos.json               # ~1 KB per combo
```

**Current usage:**
- 10 cards = ~20 KB
- 1,000 cards = ~2 MB
- 27,000 cards = ~54 MB

## Total Storage Estimates

### Minimal Setup (Development)
```
Component                    Size
─────────────────────────────────
Embedding Model              80 MB
ChromaDB (100 cards)         2 MB
Card Cache (100 cards)       0.2 MB
Python Dependencies          50 MB
─────────────────────────────────
TOTAL                        ~132 MB
```

### Recommended Setup (Small Collection)
```
Component                    Size
─────────────────────────────────
Embedding Model              80 MB
ChromaDB (3,000 cards)       50 MB
Card Cache (3,000 cards)     6 MB
Python Dependencies          50 MB
─────────────────────────────────
TOTAL                        ~186 MB
```

### Full Oracle Setup
```
Component                    Size
─────────────────────────────────
Embedding Model              80 MB
ChromaDB (27,000 cards)      421 MB
Card Cache (27,000 cards)    54 MB
Python Dependencies          50 MB
─────────────────────────────────
TOTAL                        ~605 MB
```

### All Printings (Maximum)
```
Component                    Size
─────────────────────────────────
Embedding Model              80 MB
ChromaDB (90,000 cards)      1.4 GB
Card Cache (90,000 cards)    180 MB
Python Dependencies          50 MB
─────────────────────────────────
TOTAL                        ~1.7 GB
```

## Disk Space Recommendations

### Available Space Check

```bash
# Check available disk space
df -h /Users/christopherhaynie/Developer/mtg_card_app

# Check current project size
du -sh /Users/christopherhaynie/Developer/mtg_card_app
```

### Recommended Free Space

| Use Case | Recommended Free Space |
|----------|------------------------|
| Development/Testing | 500 MB |
| Small collection (3K cards) | 1 GB |
| Full oracle cards (27K) | 2 GB |
| All printings (90K) | 5 GB |

**Safety margin:** Always keep 2-3x the estimated space for:
- Temporary files during embedding generation
- Index rebuilding
- Backups
- Future growth

## Performance Considerations

### Embedding Generation Speed

**CPU (Apple Silicon M1/M2):**
- ~50-100 cards/second
- 1,000 cards: ~10-20 seconds
- 27,000 cards: ~5-10 minutes (one-time operation)

**Memory Usage During Embedding:**
- Model loaded: 80 MB RAM
- Batch processing: ~200 MB RAM
- ChromaDB: ~100 MB RAM
- **Total peak**: ~400 MB RAM

### Query Performance

**Vector similarity search:**
- Search 1,000 cards: <10ms
- Search 10,000 cards: <50ms
- Search 27,000 cards: <100ms
- Search 90,000 cards: <200ms

**Scales well** - ChromaDB uses HNSW index for fast approximate nearest neighbor search.

## Implementation Strategy

### Phase 2A: Basic Setup (We'll start here)
```
✓ Install dependencies (chromadb, sentence-transformers)
✓ Create RAG manager (~100 cards for testing)
✓ Test embedding generation
  Storage: ~150 MB
  Time: 5 minutes
```

### Phase 2B: Popular Cards Collection (Optional)
```
✓ Embed ~3,000 most-played cards
✓ Test semantic search
  Storage: ~200 MB
  Time: 10 minutes
```

### Phase 2C: Full Oracle (Optional)
```
✓ Embed all unique cards (~27K)
✓ Production-ready search
  Storage: ~600 MB
  Time: 30 minutes
```

### Phase 2D: All Printings (Future)
```
✓ Embed every printing variation
✓ Complete card database
  Storage: ~2 GB
  Time: 2 hours
```

## Storage Optimization Tips

### 1. Start Small
Begin with 100-1000 cards, expand as needed.

### 2. Selective Embedding
Only embed cards you need:
- Commander staples (~2,000 cards)
- Format-specific cards (Standard, Modern, etc.)
- User's collection

### 3. Compression
ChromaDB supports quantization:
- Reduce embedding size from 12 KB to 3 KB per card
- 75% space savings with minimal accuracy loss

### 4. Cleanup
```bash
# Remove unused embeddings
rm -rf data/chroma/

# Clear model cache if needed
rm -rf ~/.cache/huggingface/
```

## Monitoring Storage

We'll add monitoring to track:
```python
# Storage stats
stats = rag_manager.get_stats()
print(f"Embeddings: {stats['total_embeddings']}")
print(f"Disk usage: {stats['disk_usage_mb']} MB")
print(f"Memory usage: {stats['memory_mb']} MB")
```

## Next Steps

Let's start with **Phase 2A** (basic setup):
1. Install dependencies: ~50 MB
2. Download embedding model: ~80 MB
3. Create RAG manager
4. Embed 100 test cards: ~2 MB
5. Test semantic search

**Total initial requirement: ~150 MB**

Sound good? This is well within typical development constraints and we can expand later as needed!
