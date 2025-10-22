# Phase 6 Track 3: Installation & Packaging - Detailed Plan

**Date:** October 22, 2025  
**Status:** 📋 PLANNING → 🚧 READY TO START  
**Estimated Duration:** 1-2 weeks  
**Prerequisites:** ✅ Tracks 1 & 2 Complete

---

## Executive Summary

Track 3 completes Phase 6 by making MTG Card App easy to install and distribute. We'll create:

1. **PyPI Package** - `pip install mtg-card-app` (Priority 1)
2. **Docker Image** - Pre-built container with data (Priority 2)
3. **CI/CD Pipeline** - Automated testing and releases (Priority 3)
4. **Pre-computed Data Bundle** - Fast first-time setup (Priority 4)
5. **Native Installers** - .dmg/.deb/.exe (Future - Phase 6.1)

**Key Principle:** Start simple, iterate. Get PyPI working first, then add Docker, then automation.

---

## Current State Analysis

### ✅ What Already Works

**Installation from Source:**
```bash
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app
pip install -e .
mtg setup
```

**Package Configuration:**
- ✅ `pyproject.toml` properly configured
- ✅ Entry point defined: `mtg = "mtg_card_app.ui.cli.main:cli"`
- ✅ Optional dependencies for providers
- ✅ Dependencies pinned with `~=` (compatible versions)

**Setup Process:**
- ✅ `mtg setup` wizard guides configuration
- ✅ `mtg update` downloads cards from Scryfall (~40 MB)
- ✅ Generates embeddings (takes ~5-10 minutes for 35K cards)
- ✅ Creates config at `~/.mtg/config.toml`

### ❌ What's Missing

**Distribution:**
- ❌ Not published to PyPI (can't `pip install mtg-card-app`)
- ❌ No Docker image available
- ❌ No pre-computed data bundle (users wait 10 minutes on first run)
- ❌ No CI/CD for automated releases

**Documentation:**
- ❌ No PyPI-ready README (needs badges, quick start)
- ❌ No Dockerfile
- ❌ No GitHub Actions workflows
- ❌ Installation docs assume source install

---

## Priority 1: Pre-computed Data Bundle 📊

**Goal:** Provide pre-built database + embeddings for fast setup, then incrementally update to latest.

### Why This is Priority 1

The data bundle is **foundational infrastructure** that everything else depends on:

- ✅ **PyPI users** get 2-minute setup instead of 10 minutes
- ✅ **Docker images** stay small by downloading bundle on first run
- ✅ **CI/CD tests** run faster using the bundle
- ✅ **Better UX** across all installation methods

### Architecture: Hybrid Approach

**Setup Flow:**
1. Download pre-computed bundle (~100 MB, ~35K cards as of bundle date)
2. Extract to `~/.mtg/data/` (~30 seconds)
3. Run incremental update (only new cards since bundle date, ~1-2 minutes)
4. **Total: ~2 minutes** vs 10+ minutes from scratch

**Benefits:**
- Always current (users get latest cards)
- Still fast (small incremental downloads)
- No stale data (bundle can be months old)
- Bandwidth efficient

### Step 1.1: Extend Data Service Protocols (1 hour)

**Add persistence methods to protocols:**

```python
# In mtg_card_app/domain/protocols.py (or similar)

class CardDataService(Protocol):
    # ... existing methods ...
    
    def export_to_path(self, path: Path) -> None:
        """Export database to specified path for bundling."""
        ...
    
    def import_from_path(self, path: Path) -> None:
        """Import database from specified path (bundle extraction)."""
        ...
    
    def get_last_update_date(self) -> datetime | None:
        """Get timestamp of last database update for incremental sync."""
        ...

class RAGService(Protocol):
    # ... existing methods ...
    
    def export_embeddings(self, path: Path) -> None:
        """Export ChromaDB embeddings to specified path."""
        ...
    
    def import_embeddings(self, path: Path) -> None:
        """Import ChromaDB embeddings from specified path."""
        ...
    
    def get_embedding_count(self) -> int:
        """Get count of embedded cards for validation."""
        ...
```

**Tasks:**
- [ ] Add export/import methods to CardDataService protocol
- [ ] Add export/import methods to RAGService protocol
- [ ] Add metadata methods (last_update_date, counts)

### Step 1.2: Implement in SQLiteCardDataService (30 min)

```python
# In mtg_card_app/managers/card_data/sqlite_service.py

def export_to_path(self, path: Path) -> None:
    """Copy SQLite database to bundle path."""
    import shutil
    shutil.copy2(self.db_path, path)

def import_from_path(self, path: Path) -> None:
    """Copy SQLite database from bundle to data directory."""
    import shutil
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, self.db_path)

def get_last_update_date(self) -> datetime | None:
    """Get most recent card release date from database."""
    cursor = self.conn.execute(
        "SELECT MAX(released_at) FROM cards WHERE released_at IS NOT NULL"
    )
    result = cursor.fetchone()[0]
    return datetime.fromisoformat(result) if result else None
```

**Tasks:**
- [ ] Implement export_to_path (database copy)
- [ ] Implement import_from_path (database restore)
- [ ] Implement get_last_update_date (for incremental sync)
- [ ] Add error handling for missing files

### Step 1.3: Implement in ChromaRAGService (30 min)

```python
# In mtg_card_app/managers/rag/chroma_service.py

def export_embeddings(self, path: Path) -> None:
    """Copy entire ChromaDB directory to bundle path."""
    import shutil
    if self.persist_directory.exists():
        shutil.copytree(self.persist_directory, path, dirs_exist_ok=True)

def import_embeddings(self, path: Path) -> None:
    """Copy ChromaDB directory from bundle to data directory."""
    import shutil
    self.persist_directory.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copytree(path, self.persist_directory, dirs_exist_ok=True)

def get_embedding_count(self) -> int:
    """Get count of embedded cards."""
    return self.collection.count()
```

**Tasks:**
- [ ] Implement export_embeddings (directory copy)
- [ ] Implement import_embeddings (directory restore)
- [ ] Implement get_embedding_count (for validation)
- [ ] Handle ChromaDB persistence properly

### Step 1.4: Create Data Bundle Script (1 hour)

**Create `scripts/build_data_bundle.py`:**

```python
"""Build pre-computed data bundle for distribution."""

from pathlib import Path
import tarfile
import json
from datetime import datetime
from mtg_card_app.managers.card_data.sqlite_service import SQLiteCardDataService
from mtg_card_app.managers.rag.chroma_service import ChromaRAGService
from mtg_card_app.config.manager import ConfigManager

def build_bundle():
    """Build data bundle with SQLite DB + ChromaDB embeddings."""
    
    # Initialize services
    config = ConfigManager()
    card_service = SQLiteCardDataService(config)
    rag_service = ChromaRAGService(config)
    
    # Prepare bundle directory
    bundle_dir = Path("dist/data_bundle")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    # Export database
    db_path = bundle_dir / "cards.db"
    card_service.export_to_path(db_path)
    
    # Export embeddings
    chroma_path = bundle_dir / "chroma"
    rag_service.export_embeddings(chroma_path)
    
    # Export combos (simple file copy)
    combos_src = Path.home() / ".mtg" / "data" / "combos.json"
    if combos_src.exists():
        import shutil
        shutil.copy2(combos_src, bundle_dir / "combos.json")
    
    # Create manifest with metadata
    manifest = {
        "version": "0.1.0",
        "build_date": datetime.utcnow().isoformat(),
        "last_card_date": card_service.get_last_update_date().isoformat(),
        "card_count": card_service.get_card_count(),
        "embedding_count": rag_service.get_embedding_count(),
        "files": ["cards.db", "chroma/", "combos.json"],
    }
    
    with open(bundle_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Create compressed tarball
    bundle_path = Path("dist/mtg-data-v0.1.0.tar.xz")
    with tarfile.open(bundle_path, "w:xz") as tar:
        tar.add(bundle_dir, arcname="data")
    
    # Stats
    size_mb = bundle_path.stat().st_size / (1024 * 1024)
    print(f"✅ Bundle created: {bundle_path}")
    print(f"   Size: {size_mb:.1f} MB")
    print(f"   Cards: {manifest['card_count']}")
    print(f"   Embeddings: {manifest['embedding_count']}")
    print(f"   Last card date: {manifest['last_card_date']}")
    
    return bundle_path

if __name__ == "__main__":
    build_bundle()
```

**Tasks:**
- [ ] Create scripts/build_data_bundle.py
- [ ] Use service methods for export (not direct file copy)
- [ ] Generate manifest.json with metadata
- [ ] Create compressed tarball (tar.xz)
- [ ] Test locally with real data

### Step 1.5: Enhance Update Command for Incremental Sync (1 hour)

**Update `mtg_card_app/ui/cli/commands/update.py`:**

```python
@click.command()
@click.option('--force', is_flag=True, help='Force re-download even if up to date')
@click.option('--since', help='Only import cards released after this date (ISO format)')
@click.option('--cards-only', is_flag=True, help='Skip embedding generation')
@click.option('--embeddings-only', is_flag=True, help='Skip card download')
def update(force: bool, since: str | None, cards_only: bool, embeddings_only: bool):
    """Update card database from Scryfall."""
    
    if since:
        # Incremental update
        since_date = datetime.fromisoformat(since)
        console.print(f"[yellow]Downloading cards released since {since_date.date()}...[/yellow]")
        # Filter Scryfall bulk data by released_at > since_date
        cards_to_import = [c for c in all_cards if c.get('released_at', '') > since]
        console.print(f"[green]Found {len(cards_to_import)} new cards[/green]")
    else:
        # Full update
        console.print("[yellow]Downloading all cards from Scryfall...[/yellow]")
        cards_to_import = all_cards
    
    # Import cards
    # Generate embeddings (only for new cards)
    # ...
```

**Tasks:**
- [ ] Add `--since` parameter for incremental updates
- [ ] Filter Scryfall data by release date
- [ ] Only process cards newer than since date
- [ ] Report count of new cards found
- [ ] Test incremental update flow

### Step 1.6: Update Setup Wizard (1 hour)

**Update `mtg_card_app/ui/cli/commands/setup.py`:**

```python
def install_data():
    """Install data bundle + incremental update."""
    
    # Step 1: Download bundle
    console.print("[yellow]Downloading pre-computed data bundle (~100 MB)...[/yellow]")
    bundle_path = download_bundle()
    
    # Step 2: Extract bundle
    console.print("[yellow]Extracting data...[/yellow]")
    extract_bundle(bundle_path)
    
    # Step 3: Read manifest
    manifest = read_manifest()
    console.print(
        f"[green]✓ Base data installed "
        f"({manifest['card_count']} cards as of {manifest['last_card_date']})[/green]"
    )
    
    # Step 4: Incremental update
    console.print("[yellow]Checking for new cards since bundle creation...[/yellow]")
    from click.testing import CliRunner
    from mtg_card_app.ui.cli.commands.update import update
    
    runner = CliRunner()
    result = runner.invoke(update, ['--since', manifest['last_card_date']])
    
    if result.exit_code == 0:
        console.print("[green]✓ Data is now up to date![/green]")
    else:
        console.print("[yellow]⚠ Incremental update had issues, but base data is installed[/yellow]")

def download_bundle():
    """Download bundle from GitHub releases."""
    import requests
    from rich.progress import Progress, DownloadColumn, TransferSpeedColumn
    
    url = "https://github.com/topherhaynie/mtg_card_app/releases/download/data-v0.1.0/mtg-data-v0.1.0.tar.xz"
    
    with Progress(
        *Progress.get_default_columns(),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        
        task = progress.add_task("Downloading", total=total)
        
        bundle_path = Path("/tmp/mtg-data-bundle.tar.xz")
        with open(bundle_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))
    
    return bundle_path

def extract_bundle(bundle_path: Path):
    """Extract bundle to data directory."""
    import tarfile
    data_dir = Path.home() / ".mtg" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    with tarfile.open(bundle_path, "r:xz") as tar:
        tar.extractall(data_dir)
    
    bundle_path.unlink()  # Clean up

def read_manifest() -> dict:
    """Read bundle manifest."""
    import json
    manifest_path = Path.home() / ".mtg" / "data" / "data" / "manifest.json"
    with open(manifest_path) as f:
        return json.load(f)
```

**Tasks:**
- [ ] Add download_bundle() function with progress bar
- [ ] Add extract_bundle() function
- [ ] Add read_manifest() function
- [ ] Integrate incremental update after bundle install
- [ ] Handle errors gracefully (fallback to full update)

### Step 1.7: Upload Bundle to GitHub Releases (30 min)

**Process:**
1. Build bundle locally: `python scripts/build_data_bundle.py`
2. Create GitHub release (tag: `data-v0.1.0`)
3. Upload tarball as release asset
4. Document download URL in setup code
5. Test download in setup wizard

**Tasks:**
- [ ] Run `mtg update` to ensure fresh data
- [ ] Build first bundle with script
- [ ] Create GitHub release for data
- [ ] Upload tarball (~100 MB compressed)
- [ ] Update setup.py with correct URL
- [ ] Test end-to-end: setup downloads → extracts → updates

**Estimated Time:** ~5-6 hours total

---

## Priority 2: PyPI Package 📦

**Goal:** Users can `pip install mtg-card-app` and get started immediately.

### Step 2.1: Prepare Package Metadata (1 hour)

**Update `pyproject.toml`:**

```toml
[project]
name = "mtg-card-app"
version = "0.1.0"
description = "Conversational MTG card search, combo finder, and deck builder with AI"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["mtg", "magic-the-gathering", "cards", "combos", "deck-builder", "ai", "cli"]
authors = [
    {name = "Christopher Haynie", email = "your-email@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Games/Entertainment :: Board Games",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/topherhaynie/mtg_card_app"
Documentation = "https://github.com/topherhaynie/mtg_card_app/tree/main/docs"
Repository = "https://github.com/topherhaynie/mtg_card_app"
Issues = "https://github.com/topherhaynie/mtg_card_app/issues"
Changelog = "https://github.com/topherhaynie/mtg_card_app/releases"
```

**Tasks:**
- [ ] Update classifiers (Alpha → Beta)
- [ ] Add author email
- [ ] Add keywords for discoverability
- [ ] Add project URLs
- [ ] Verify all metadata is accurate

### Step 2.2: Create PyPI-Ready README (2 hours)

**Requirements:**
- Beautiful badges (PyPI version, Python versions, license)
- Quick start with copy-paste commands
- Feature highlights with screenshots/examples
- Clear installation instructions
- Link to full documentation

**Example Structure:**
```markdown
# MTG Card App 🎴

[![PyPI version](https://badge.fury.io/py/mtg-card-app.svg)](https://badge.fury.io/py/mtg-card-app)
[![Python Versions](https://img.shields.io/pypi/pyversions/mtg-card-app.svg)](https://pypi.org/project/mtg-card-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Conversational MTG card search, combo finder, and deck builder powered by AI.

## Quick Start

```bash
pip install mtg-card-app
mtg setup
mtg
```

## Features
- 🤖 Chat with AI about MTG cards
- 🔍 Search 35K+ cards with natural language
- 💥 Find combos and synergies
- 🎯 Build and validate decks
- 🎨 Beautiful terminal UI

[Full documentation →](https://github.com/...)
```

**Tasks:**
- [ ] Create badges (PyPI, Python, License, CI)
- [ ] Add quick start section
- [ ] Add feature highlights with examples
- [ ] Add screenshots/GIFs if possible
- [ ] Keep it concise (PyPI README should be scannable)

### Step 2.3: Package Testing (2 hours)

**Test the package build:**
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check for errors
twine check dist/*

# Test installation locally
pip install dist/mtg_card_app-0.1.0-py3-none-any.whl

# Verify it works
mtg --version
mtg --help
```

**Test scenarios:**
- [ ] Fresh install in new virtualenv
- [ ] Install with optional dependencies: `pip install mtg-card-app[all-providers]`
- [ ] Entry point works: `mtg --version`
- [ ] Setup wizard runs: `mtg setup`
- [ ] Update command works: `mtg update`

### Step 2.4: TestPyPI Upload (1 hour)

**Why TestPyPI first?**
- Practice the release process
- Catch issues before real release
- Can't delete packages from real PyPI

**Steps:**
```bash
# Create account at test.pypi.org
# Generate API token

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mtg-card-app

# Verify everything works
mtg --version
mtg setup
```

**Tasks:**
- [ ] Create TestPyPI account
- [ ] Generate API token
- [ ] Upload package
- [ ] Test installation
- [ ] Document any issues

### Step 2.5: Real PyPI Upload (30 minutes)

**Note:** Now with data bundle, setup is truly fast (~2 minutes)!

**Final checklist:**
- [ ] README looks good on TestPyPI
- [ ] Package installs correctly
- [ ] All commands work
- [ ] No errors or warnings
- [ ] Version number is correct (0.1.0)

**Upload:**
```bash
# Create account at pypi.org
# Generate API token

# Upload to real PyPI
twine upload dist/*

# Announce! 🎉
```

**Post-upload:**
- [ ] Verify package page looks good
- [ ] Test fresh installation
- [ ] Update docs to show `pip install` instead of source install
- [ ] Create GitHub release with same version tag

**Estimated Time:** 6-7 hours total

---

## Priority 3: Docker Image 🐳

**Goal:** Provide containerized version for easy deployment.

### Step 3.1: Create Dockerfile (2 hours)

**Note:** Dockerfile now downloads data bundle on first run (faster, smaller image)

**Strategy:** Multi-stage build to minimize image size.

**Dockerfile outline:**
```dockerfile
# Stage 1: Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (layer caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Create data directory
RUN mkdir -p /root/.mtg/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MTG_DATA_DIR=/root/.mtg/data

# Expose port (for future web UI)
EXPOSE 8000

# Entry point
ENTRYPOINT ["mtg"]
CMD ["--help"]
```

**Features:**
- Multi-stage build (smaller image)
- Layer caching for faster rebuilds
- Minimal base image (python:3.12-slim)
- Pre-creates data directory
- Sets environment variables

**Tasks:**
- [ ] Create Dockerfile
- [ ] Test local build: `docker build -t mtg-card-app .`
- [ ] Test container run: `docker run mtg-card-app --version`
- [ ] Document volume mounts for persistence

### Step 3.2: Create docker-compose.yml (1 hour)

**Purpose:** Easy local deployment with persistence.

```yaml
version: '3.8'

services:
  mtg-app:
    image: ghcr.io/topherhaynie/mtg-card-app:latest
    container_name: mtg-card-app
    volumes:
      - ~/.mtg:/root/.mtg  # Persist data and config
    environment:
      # Optional: Override LLM provider
      - OLLAMA_HOST=http://host.docker.internal:11434
    stdin_open: true
    tty: true
    
  # Optional: Include Ollama for complete local setup
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

**Tasks:**
- [ ] Create docker-compose.yml
- [ ] Test: `docker-compose up`
- [ ] Document usage in README
- [ ] Add example with Ollama included

### Step 3.3: Publish to GitHub Container Registry (1 hour)

**Why GHCR?**
- Free for public repositories
- Integrated with GitHub
- No rate limits for pulls
- Automatic from GitHub Actions

**Manual first (later automate):**
```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u topherhaynie --password-stdin

# Tag image
docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:latest
docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:0.1.0

# Push
docker push ghcr.io/topherhaynie/mtg-card-app:latest
docker push ghcr.io/topherhaynie/mtg-card-app:0.1.0
```

**Tasks:**
- [ ] Create GitHub personal access token (packages:write)
- [ ] Build and tag images
- [ ] Push to GHCR
- [ ] Make package public
- [ ] Test pull: `docker pull ghcr.io/topherhaynie/mtg-card-app:latest`

### Step 3.4: Documentation (1 hour)

**Add to README:**
- Docker installation instructions
- Volume mount examples
- docker-compose usage
- Troubleshooting common issues

**Create `docs/DOCKER.md`:**
- Detailed Docker usage guide
- Environment variables
- Custom configurations
- Using with external Ollama
- Development workflows

**Tasks:**
- [ ] Update README with Docker section
- [ ] Create docs/DOCKER.md
- [ ] Add examples for common use cases
- [ ] Document port mappings for future web UI

**Estimated Time:** 5-6 hours total

---

## Priority 4: CI/CD Pipeline 🔄

**Goal:** Automate testing, building, and releasing.

### Step 4.1: GitHub Actions - Testing (2 hours)

**Note:** Tests can now download data bundle for faster CI runs

**Create `.github/workflows/test.yml`:**

```yaml
name: Tests

on:
  push:
    branches: [ main, initial_build ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev,all-providers]"
      
      - name: Run tests
        run: |
          pytest tests/unit/ -v --cov=mtg_card_app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**Features:**
- Tests on 3 OS × 3 Python versions = 9 jobs
- Installs all providers for complete testing
- Generates coverage reports
- Uploads to Codecov (optional)

**Tasks:**
- [ ] Create .github/workflows/ directory
- [ ] Create test.yml workflow
- [ ] Test on push to branch
- [ ] Add status badge to README
- [ ] Set up Codecov (optional)

### Step 4.2: GitHub Actions - Release (2 hours)

**Create `.github/workflows/release.yml`:**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags (v0.1.0, v0.2.0, etc.)

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install build tools
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Features:**
- Triggered by pushing version tags
- Builds package
- Uploads to PyPI
- Creates GitHub Release with notes
- Attaches wheel/sdist files

**Tasks:**
- [ ] Create release.yml workflow
- [ ] Add PYPI_API_TOKEN to GitHub Secrets
- [ ] Test release process (dry run first)
- [ ] Document release process for maintainers

### Step 4.3: GitHub Actions - Docker Build (2 hours)

**Create `.github/workflows/docker.yml`:**

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Features:**
- Builds on push to main or tags
- Pushes to GHCR automatically
- Creates semantic version tags
- Uses BuildKit caching for speed

**Tasks:**
- [ ] Create docker.yml workflow
- [ ] Test Docker builds in CI
- [ ] Verify images are published to GHCR
- [ ] Add Docker status badge to README

**Estimated Time:** 6-7 hours total

### Step 4.4: GitHub Actions - Data Bundle Automation (1 hour)

**Create `.github/workflows/data-bundle.yml`:**

```yaml
name: Build Data Bundle

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 0 1 * *'  # Monthly on 1st

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Run update to get latest cards
        run: mtg update
      
      - name: Build data bundle
        run: python scripts/build_data_bundle.py
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: data-v${{ github.run_number }}
          name: Data Bundle - ${{ github.run_number }}
          files: dist/mtg-data-*.tar.xz
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Tasks:**
- [ ] Create data-bundle.yml workflow
- [ ] Test manual trigger
- [ ] Set up monthly schedule (optional)
- [ ] Document bundle update process

**Estimated Time:** ~6-7 hours total

---

## ~~Priority 4: Pre-computed Data Bundle~~ ✅ NOW PRIORITY 1

**This section moved to Priority 1 above.**

### ~~Step 4.1: Create Data Bundle Script (2 hours)~~

**Create `scripts/build_data_bundle.py`:**

```python
**Moved to Priority 1 - See above for complete implementation details.**

---

## Implementation Timeline

### Week 1: Foundation & Distribution (Days 1-4)

**Day 1: Data Bundle Infrastructure (5-6 hours)** 🆕
- Morning: Extend protocols (export/import methods)
- Midday: Implement SQLite and Chroma service methods
- Afternoon: Create build_data_bundle.py script
- Evening: Test bundle creation locally

**Day 2: Data Bundle Integration (3-4 hours)** 🆕
- Morning: Enhance update command with `--since` parameter
- Afternoon: Update setup wizard (download + extract + update)
- Evening: Build and upload first bundle to GitHub Releases

**Day 3: PyPI Preparation (6-7 hours)**
- Morning: Update pyproject.toml, create PyPI-ready README (now mentions 2-min setup!)
- Afternoon: Build and test package locally
- Evening: Upload to TestPyPI, test installation

**Day 4: PyPI Release (2-3 hours)**
- Morning: Fix any issues from TestPyPI
- Publish to real PyPI
- Update documentation
- Create GitHub release tag

### Week 2: Containerization & Automation (Days 5-7)

**Day 5: Docker (5-6 hours)**
- Morning: Create Dockerfile (downloads bundle on first run)
- Afternoon: Create docker-compose.yml, test locally
- Evening: Publish to GHCR, write documentation

**Day 6-7: CI/CD (6-7 hours)**
- Day 6: Create test workflow, test across platforms
- Day 7: Create release, Docker, and data-bundle workflows
- Set up GitHub secrets

### Optional: Week 3: Polish & Testing

**Day 8-9: Documentation & Testing**
- Comprehensive installation documentation
- User acceptance testing
- Bug fixes

**Day 10: Launch Prep**
- Final testing
- Write announcement
- Prepare demos/videos

---

## Success Criteria

### Must Have ✅
- [ ] Package published to PyPI
- [ ] `pip install mtg-card-app` works on macOS/Linux/Windows
- [ ] Docker image available on GHCR
- [ ] Automated tests run on push
- [ ] Installation takes < 5 minutes
- [ ] Documentation updated

### Nice to Have 🎯
- [ ] Pre-computed data bundle available
- [ ] Automated releases on tag push
- [ ] Docker image builds automatically
- [ ] Coverage reports
- [ ] Status badges on README

### Future (Phase 6.1) 🔮
- [ ] Native installers (.dmg, .deb, .exe)
- [ ] Homebrew formula
- [ ] Snap package (Linux)
- [ ] Windows Store listing
- [ ] Auto-update mechanism

---

## Risk Assessment

### Low Risk ✅
- **PyPI Publication** - Standard process, well-documented
- **Docker Basic Image** - Simple Dockerfile, no complex dependencies
- **GitHub Actions Testing** - Mature, reliable platform

### Medium Risk ⚠️
- **Multi-platform Testing** - Windows might have path issues
- **Data Bundle Size** - Could exceed GitHub release limits (2 GB max)
- **Docker Image Size** - ML dependencies (PyTorch) are large (~2 GB)

### Mitigation Strategies
- Test on Windows early, use pathlib consistently
- Compress data bundle aggressively (xz compression)
- Multi-stage Docker build to minimize layers
- Consider separate "slim" Docker image without embeddings

---

## Open Questions

### Q1: Package Name
**Current:** `mtg-card-app`  
**Alternative:** `mtgcli`, `mtg-assistant`, `mtgapp`  
**Decision:** Keep `mtg-card-app` (descriptive, not taken on PyPI)

### Q2: Docker Base Image
**Options:**
- `python:3.12-slim` (~150 MB base, +2 GB for PyTorch)
- `python:3.12-alpine` (Smaller but compilation issues)
**Decision:** Use slim for compatibility, accept larger size

### Q3: Data Bundle Hosting
**Options:**
- GitHub Releases (2 GB limit, free)
- GitHub LFS (bandwidth costs)
- External CDN (complexity)
**Decision:** GitHub Releases, monitor size

### Q4: Version Strategy
**Options:**
- SemVer (0.1.0, 0.2.0, 1.0.0)
- CalVer (2025.10.0)
**Decision:** SemVer, save 1.0.0 for "production ready"

---

## Dependencies

### External Services Required
- [ ] PyPI account + API token
- [ ] TestPyPI account + API token
- [ ] GitHub Container Registry (automatic)
- [ ] Codecov account (optional)

### Repository Secrets Needed
- [ ] `PYPI_API_TOKEN` - For automated releases
- [ ] `GITHUB_TOKEN` - Automatic (for releases)

### Tools to Install Locally
- [ ] `build` - Python package builder
- [ ] `twine` - PyPI upload tool
- [ ] Docker Desktop - For testing

---

## Deliverables

### Code
- [ ] `pyproject.toml` updated with metadata
- [ ] README.md with badges and quick start
- [ ] `Dockerfile` and `docker-compose.yml`
- [ ] `.github/workflows/` directory with 3-4 workflows
- [ ] `scripts/build_data_bundle.py`

### Documentation
- [ ] docs/DOCKER.md - Docker usage guide
- [ ] docs/INSTALLATION.md - All installation methods
- [ ] docs/CONTRIBUTING.md - Release process for maintainers
- [ ] Updated README with installation options

### Releases
- [ ] v0.1.0 on PyPI
- [ ] v0.1.0 tagged on GitHub
- [ ] Docker image on GHCR
- [ ] Data bundle on GitHub Releases

---

## Next Steps

**Immediate Actions:**
1. Review and approve this plan
2. Create PyPI and TestPyPI accounts
3. Generate API tokens
4. Create `.github/workflows/` directory
5. Start with Priority 1 (PyPI)

**After Track 3 Complete:**
- Phase 6 is 100% complete! 🎉
- Option 1: Start Phase 7 (Web UI)
- Option 2: Polish Phase 6 (more tests, optimization)
- Option 3: Phase 6.1 (Native installers)

---

**Status:** 📋 READY TO START  
**Last Updated:** October 22, 2025  
**Next Review:** After PyPI publication

