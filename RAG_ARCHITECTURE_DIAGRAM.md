# RAG Architecture Diagram

## Before Refactoring (Tightly Coupled)

```
┌─────────────────────────────────────────────────┐
│              RAG Manager                        │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Direct ChromaDB imports                  │  │
│  │ Direct SentenceTransformer imports       │  │
│  │ _chroma_client: chromadb.Client          │  │
│  │ _embedding_model: SentenceTransformer    │  │
│  │ _collection: chromadb.Collection         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│         ↓ Tightly Coupled ↓                     │
│                                                 │
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │  ChromaDB    │    │ SentenceTransformers │  │
│  └──────────────┘    └──────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## After Refactoring (Loosely Coupled)

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Manager                              │
│                                                                 │
│  Uses service abstractions instead of concrete implementations │
│                                                                 │
│  ┌──────────────────────┐    ┌───────────────────────────┐    │
│  │  embedding_service   │    │    vector_store           │    │
│  │  (EmbeddingService)  │    │  (VectorStoreService)     │    │
│  └──────────────────────┘    └───────────────────────────┘    │
│            │                              │                     │
└────────────┼──────────────────────────────┼─────────────────────┘
             │                              │
             │ Protocol/Interface           │ Protocol/Interface
             ↓                              ↓
             
┌────────────┴──────────────┐    ┌─────────┴──────────────────┐
│   EmbeddingService         │    │   VectorStoreService       │
│   (Protocol)               │    │   (Protocol)               │
│                            │    │                            │
│  • embed_text()            │    │  • add_embedding()         │
│  • embed_texts()           │    │  • search_similar()        │
│  • get_embedding_dimension│    │  • get_embedding()         │
│  • get_model_name()        │    │  • exists()                │
│  • get_stats()             │    │  • delete()                │
│  • get_service_name()      │    │  • clear_all()             │
└────────────┬──────────────┘    └─────────┬──────────────────┘
             │                              │
             │ Implemented by               │ Implemented by
             ↓                              ↓
             
┌────────────┴─────────────────────────────┐
│ SentenceTransformerEmbeddingService      │
│                                          │
│  • Uses HuggingFace models               │
│  • Default: all-MiniLM-L6-v2            │
│  • 384-dimensional embeddings            │
│  • Lazy loading                          │
│  • CPU/GPU support                       │
└──────────────────────────────────────────┘

           ┌────────────┴──────────────────────────┐
           │ ChromaVectorStoreService              │
           │                                       │
           │  • Persistent ChromaDB client         │
           │  • HNSW indexing                      │
           │  • Lazy initialization                │
           │  • Metadata filtering                 │
           │  • Disk-based storage                 │
           └───────────────────────────────────────┘
```

## Service Interaction Flow

```
User Code
   │
   │ rag = RAGManager()
   ↓
RAG Manager (Orchestrator)
   │
   ├─→ embed_card(card)
   │    │
   │    ├─→ embedding_service.embed_text(text)
   │    │    └─→ SentenceTransformerEmbeddingService
   │    │         └─→ Returns: [0.123, 0.456, ...] (384 dims)
   │    │
   │    └─→ vector_store.add_embedding(id, embedding, metadata, doc)
   │         └─→ ChromaVectorStoreService
   │              └─→ Stores in ChromaDB with HNSW index
   │
   └─→ search_similar(query)
        │
        ├─→ embedding_service.embed_text(query)
        │    └─→ Returns query vector
        │
        └─→ vector_store.search_similar(query_vector, n_results, filters)
             └─→ Returns: [(id, similarity, metadata), ...]
```

## Benefits Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    FLEXIBILITY                              │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │ OpenAI       │   │ Cohere       │   │ Custom Model │  │
│  │ Embeddings   │   │ Embeddings   │   │              │  │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘  │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            ↓                                │
│                  EmbeddingService Protocol                  │
│                            ↑                                │
│                    RAG Manager                              │
│                            ↓                                │
│                 VectorStoreService Protocol                 │
│                            ↑                                │
│         ┌──────────────────┴──────────────────┐            │
│         │                  │                  │            │
│  ┌──────┴───────┐   ┌──────┴───────┐   ┌──────┴───────┐  │
│  │   Pinecone   │   │   Weaviate   │   │   Qdrant     │  │
│  │              │   │              │   │              │  │
│  └──────────────┘   └──────────────┘   └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Comparison with Card Data Architecture

```
Card Data Layer                  RAG Layer
─────────────────                ─────────

┌─────────────────┐            ┌─────────────────┐
│ Card Manager    │            │  RAG Manager    │
└────────┬────────┘            └────────┬────────┘
         │                              │
         │ uses                         │ uses
         ↓                              ↓
┌─────────────────┐            ┌─────────────────┐
│ CardDataService │            │ EmbeddingService│
│   (Protocol)    │            │   (Protocol)    │
└────────┬────────┘            └────────┬────────┘
         │                              │
         │ implemented by               │ implemented by
         ↓                              ↓
┌─────────────────┐            ┌─────────────────┐
│   Scryfall      │            │ SentenceTransf. │
│     Service     │            │     Service     │
└─────────────────┘            └─────────────────┘

                                        +
                                        
                               ┌─────────────────┐
                               │ VectorStoreServ.│
                               │   (Protocol)    │
                               └────────┬────────┘
                                        │
                                        │ implemented by
                                        ↓
                               ┌─────────────────┐
                               │    ChromaDB     │
                               │     Service     │
                               └─────────────────┘

Same Pattern, Consistent Architecture Throughout!
```

## Testing Benefits

```
Production:                    Testing:
───────────                    ─────────

RAG Manager                    RAG Manager
    │                              │
    ├─→ Real Embedding Svc         ├─→ Mock Embedding Svc
    │    (SentenceTransf.)         │    (Returns fake vectors)
    │                              │
    └─→ Real Vector Store          └─→ Mock Vector Store
         (ChromaDB)                     (In-memory dict)

Fast, reliable tests without external dependencies!
```
