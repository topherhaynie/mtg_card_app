# Phase 7: Web UI

**Status:** 📋 Planning  
**Prerequisites:** Phase 6 Complete (CLI + LLM Providers + Installation)  
**Duration:** 3-4 weeks  
**Scope:** Local web interface with conversational chat + quick actions

---

## Executive Summary

Phase 7 creates a browser-based interface that mirrors the CLI's conversational-first design:

**Primary Goal:** Chat interface for natural MTG queries (like talking to Claude)  
**Secondary Goal:** Quick action buttons for common tasks  
**Hosting:** Local-only at `localhost:3000` or `mtg.local:3000`

**Philosophy:** Same UX pattern as CLI - chat is primary, buttons are shortcuts

---

## User Experience Vision

### Landing Page
```
┌─────────────────────────────────────────────────────────────┐
│  🎴 MTG Card App                            [Settings] [?]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Connected to: Ollama (llama3) | 35,402 cards loaded        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Quick Actions                                          │ │
│  │  [Search Cards] [Find Combos] [Build Deck]            │ │
│  │  [Analyze Deck] [Budget Cards] [System Stats]         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Chat                                                   │ │
│  │ ───────────────────────────────────────────────────    │ │
│  │                                                        │ │
│  │  [Chat history appears here...]                       │ │
│  │                                                        │ │
│  │  User: show me blue counterspells under $5            │ │
│  │                                                        │ │
│  │  Assistant: I found 15 blue counterspells...          │ │
│  │    1. Counterspell - $3.50                            │ │
│  │       [View Card] [Add to Deck]                       │ │
│  │    2. Negate - $0.25                                  │ │
│  │       [View Card] [Add to Deck]                       │ │
│  │                                                        │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Ask me anything about MTG cards...          [Send ↑] │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Conversational First** - Chat box is prominent, buttons are helpers
2. **Contextual Actions** - Cards and combos have inline action buttons
3. **Responsive** - Works on desktop, tablet, mobile
4. **Fast** - <100ms UI interactions, streaming LLM responses
5. **Local-Only** - No cloud hosting, no telemetry, no tracking

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser (localhost:3000)                               │
│  ┌─────────────────────┐                                │
│  │  React Frontend     │                                │
│  │  • Chat UI          │                                │
│  │  • Card Display     │                                │
│  │  • Deck Builder     │                                │
│  │  • Settings Panel   │                                │
│  └──────────┬──────────┘                                │
└─────────────┼───────────────────────────────────────────┘
              │ WebSocket (chat streaming)
              │ HTTP REST API (data fetching)
┌─────────────▼───────────────────────────────────────────┐
│  FastAPI Backend (localhost:8000)                       │
│  ┌─────────────────────┐                                │
│  │  API Routes         │                                │
│  │  • /api/chat        │ ← WebSocket for streaming      │
│  │  • /api/cards       │ ← REST endpoints               │
│  │  • /api/combos      │                                │
│  │  • /api/decks       │                                │
│  │  • /api/system      │                                │
│  └──────────┬──────────┘                                │
│             │                                            │
│  ┌──────────▼──────────┐                                │
│  │   Interactor        │ ← Reuses Phase 6 core          │
│  │   (Business Logic)  │                                │
│  └─────────────────────┘                                │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend: FastAPI
- **Why:** Async/await support, WebSocket support, fast, type-safe
- **Endpoints:** REST for data, WebSocket for streaming chat
- **Port:** 8000 (internal), proxied through frontend at 3000

### Frontend: React + Tailwind + shadcn/ui
- **React:** Component-based, mature ecosystem
- **Tailwind CSS:** Utility-first styling, fast development
- **shadcn/ui:** Beautiful pre-built components (chat, modals, cards)
- **Vite:** Fast build tool, HMR for development
- **Port:** 3000 (serves frontend + proxies API to 8000)

### Hosting: Local Only
- **Dev Mode:** `mtg web --dev` (hot reload)
- **Prod Mode:** `mtg web` (optimized build)
- **URL:** `http://localhost:3000` or `http://mtg.local:3000`
- **Custom Alias:** Set via `/etc/hosts` or `sudo mtg web --alias mtg.local`

---

## Feature Breakdown

### Core Views

#### 1. Chat Interface (Primary)
- **Input:** Text box with auto-resize, send on Enter
- **Output:** Streaming LLM responses (word-by-word)
- **History:** Scrollable conversation history
- **Context:** Cards/combos shown inline with action buttons
- **Special Commands:** `/clear`, `/help`, `/settings`

**Implementation:**
- WebSocket connection for bi-directional streaming
- Markdown rendering for LLM responses
- Card preview on hover
- Copy/share conversation

#### 2. Quick Action Buttons (Secondary)
- **Search Cards** → Opens pre-filled chat: "search for..."
- **Find Combos** → Opens pre-filled chat: "find combos with..."
- **Build Deck** → Opens deck builder modal
- **Analyze Deck** → File upload + analysis
- **Budget Cards** → Opens pre-filled chat: "show budget cards under..."
- **System Stats** → Opens stats modal

**Implementation:**
- Buttons populate chat input
- User can edit before sending
- Maintains conversational flow

#### 3. Card Display
- **Grid View:** Card images (hover for details)
- **List View:** Name, type, mana cost, price, actions
- **Detail Modal:** Full card info, prices, legality, combos
- **Actions:** Add to deck, find combos, compare

**Implementation:**
- Lazy-load card images (Scryfall API)
- Cache images in browser
- Responsive grid (1-4 columns based on screen size)

#### 4. Deck Builder
- **Drag-and-Drop:** Cards to deck sections
- **Visual Mana Curve:** Bar chart
- **Budget Tracker:** Current total vs budget
- **Suggestions Panel:** AI-powered recommendations
- **Export:** Download as moxfield/arena/json

**Implementation:**
- React DnD library
- Recharts for mana curve
- Auto-save to localStorage
- Export generates file download

#### 5. Settings Panel
- **LLM Provider Selection:** Dropdown (Ollama, OpenAI, Anthropic, Gemini, Groq)
- **API Key Management:** Secure input (masked)
- **Theme:** Light/Dark mode
- **Cache Settings:** Enable/disable, clear cache
- **Data Updates:** Check for updates, download latest

**Implementation:**
- Settings stored in `~/.mtg/config.toml`
- API keys encrypted
- Theme persisted in localStorage

### Advanced Features (Optional)

#### Collection Manager
- **Track Owned Cards:** Mark cards you own
- **Value Tracking:** Total collection value
- **Want List:** Cards to acquire
- **Trade Helper:** Find tradeable cards

#### Visual Combo Graph
- **Graph Visualization:** Nodes = cards, edges = synergies
- **Interactive:** Click node to see combos
- **Filters:** By power level, budget, complexity

#### Price Alerts
- **Watch List:** Track card prices
- **Notifications:** When card drops below threshold
- **Price History:** Graph of price over time

---

## API Design

### REST Endpoints

```
GET  /api/cards                      # List all cards (paginated)
GET  /api/cards/:id                  # Get card by ID
GET  /api/cards/search?q=...         # Search cards
GET  /api/cards/budget?max=...       # Budget cards

GET  /api/combos                     # List all combos
GET  /api/combos/:id                 # Get combo by ID
GET  /api/combos/search?card=...     # Find combos with card
GET  /api/combos/budget?max=...      # Budget combos

POST /api/decks                      # Create deck
GET  /api/decks/:id                  # Get deck
POST /api/decks/:id/validate         # Validate deck
POST /api/decks/:id/analyze          # Analyze deck
POST /api/decks/:id/suggest          # Get suggestions
POST /api/decks/:id/export?format=... # Export deck

GET  /api/system/stats               # System statistics
GET  /api/system/version             # App version
POST /api/system/update              # Check for updates

GET  /api/config                     # Get config
PUT  /api/config/:key                # Set config value
```

### WebSocket Endpoint

```
WS   /api/chat                       # Streaming chat

Client → Server:
{
  "type": "query",
  "message": "show me blue counterspells",
  "context": {...}  // Optional conversation context
}

Server → Client (streaming):
{
  "type": "token",
  "content": "I"
}
{
  "type": "token",
  "content": " found"
}
...
{
  "type": "complete",
  "full_response": "...",
  "metadata": {
    "cards": [...],
    "combos": [...],
    "duration_ms": 1234
  }
}
```

---

## Implementation Plan

### Week 1: Backend API
**Days 1-2: FastAPI Setup**
- [ ] Create `mtg_card_app/ui/web/backend/` module
- [ ] FastAPI app with CORS
- [ ] Basic REST routes for cards, combos, decks
- [ ] Wire to existing Interactor
- [ ] API documentation (Swagger)

**Days 3-4: WebSocket Chat**
- [ ] WebSocket endpoint for chat
- [ ] Streaming LLM responses
- [ ] Conversation context management
- [ ] Error handling

**Days 5-7: Advanced Endpoints**
- [ ] Deck operations (build, validate, analyze, suggest)
- [ ] System endpoints (stats, config, update)
- [ ] Authentication (optional, for multi-user)
- [ ] Rate limiting

### Week 2: Frontend Foundation
**Days 1-2: React Setup**
- [ ] Vite + React + TypeScript
- [ ] Tailwind CSS + shadcn/ui
- [ ] Routing (React Router)
- [ ] API client (fetch wrapper)

**Days 3-4: Chat Interface**
- [ ] Chat UI component
- [ ] WebSocket connection
- [ ] Streaming text display
- [ ] Message history

**Days 5-7: Card Display**
- [ ] Card grid component
- [ ] Card detail modal
- [ ] Image lazy loading
- [ ] Search/filter UI

### Week 3: Core Features
**Days 1-3: Deck Builder**
- [ ] Deck editor component
- [ ] Drag-and-drop
- [ ] Mana curve visualization
- [ ] Budget tracker
- [ ] Export functionality

**Days 4-5: Quick Actions**
- [ ] Quick action buttons
- [ ] Pre-fill chat input
- [ ] System stats modal
- [ ] Settings panel

**Days 6-7: Polish**
- [ ] Responsive design
- [ ] Dark mode
- [ ] Loading states
- [ ] Error handling

### Week 4: Integration & Testing
**Days 1-2: Integration**
- [ ] Connect frontend to backend
- [ ] End-to-end workflows
- [ ] Performance optimization

**Days 3-4: Testing**
- [ ] Unit tests (frontend)
- [ ] API tests (backend)
- [ ] E2E tests (Playwright)
- [ ] Manual testing

**Days 5-7: Launch Prep**
- [ ] Documentation
- [ ] User guide
- [ ] Demo video
- [ ] Release notes

---

## Startup Flow

**Development Mode:**
```bash
mtg web --dev
Starting web server...
  Backend:  http://localhost:8000
  Frontend: http://localhost:3000 (proxied to backend)
  
Open http://localhost:3000 in your browser
Press Ctrl+C to stop
```

**Production Mode:**
```bash
mtg web
Building frontend... ✓
Starting web server... ✓

🎴 MTG Card App Web UI
  URL: http://localhost:3000
  Alternative: http://mtg.local:3000
  
  Press Ctrl+C to stop
```

**Custom Alias:**
```bash
sudo mtg web --alias mtg.local
Adding mtg.local to /etc/hosts... ✓
Starting web server... ✓

Open http://mtg.local:3000 in your browser
```

---

## Success Criteria

- [ ] ✅ Chat interface works smoothly
- [ ] ✅ Streaming responses feel instant
- [ ] ✅ All Interactor methods accessible
- [ ] ✅ Card display is beautiful
- [ ] ✅ Deck builder is intuitive
- [ ] ✅ Responsive on mobile/tablet/desktop
- [ ] ✅ Dark mode works perfectly
- [ ] ✅ <100ms UI interactions
- [ ] ✅ Works offline (local data)
- [ ] ✅ User testing with 3+ people

---

## Open Questions

1. **Authentication:** Multi-user support or single-user?  
   **Recommendation:** Single-user for Phase 7, multi-user in 7.1

2. **Offline Mode:** PWA with service workers?  
   **Recommendation:** Basic offline (cached data), full PWA in 7.2

3. **Mobile App:** Electron wrapper for desktop app?  
   **Recommendation:** Web-only initially, Electron in 7.3

4. **Telemetry:** Anonymous usage stats?  
   **Recommendation:** No telemetry (privacy-first)

5. **Sharing:** Export conversation as markdown?  
   **Recommendation:** Yes, simple export feature

---

## Dependencies

**Backend:**
```toml
fastapi = "~=0.109"
uvicorn = "~=0.27"
websockets = "~=12.0"
python-multipart = "~=0.0.6"  # File uploads
```

**Frontend:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",  // shadcn/ui
    "recharts": "^2.10.0",
    "react-dnd": "^16.0.1"
  }
}
```

---

**Status:** Awaiting Phase 6 completion  
**Last Updated:** October 21, 2025  
**Next Review:** After Phase 6 ships
