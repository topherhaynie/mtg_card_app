# Phase 6 Track 3: Installation & Packaging - Checklist

**Started:** October 2025  
**Status:** 🟡 IN PROGRESS

---ck 3: Installation & Packaging - Checklist

**Started:** October### Step 2: Create PyPI-Ready README (1 hour)
- [ ] Add badges (PyPI version, Python versions, License, CI)
- [ ] Write quick start section (install → setup → run)
- [ ] **Highlight 2-minute setup** (thanks to data bundle!)
- [ ] Add feature highlights with examples
- [ ] Add screenshots or GIFs (optional but nice)
- [ ] Keep concise for PyPI rendering
- [ ] Link to full documentation25  
**Status:** � NOT STARTED

---

## 📊 Priority 1: Pre-computed Data Bundle (5-6 hours) 🆕

### Step 1: Extend Data Service Protocols (1 hour)
- [x] Add `export_to_path()` to CardDataService protocol
- [x] Add `import_from_path()` to CardDataService protocol
- [x] Add `get_last_update_date()` to CardDataService protocol
- [x] Add `export_embeddings()` to RAGService protocol
- [x] Add `import_embeddings()` to RAGService protocol
- [x] Add `get_embedding_count()` to RAGService protocol

### Step 2: Implement SQLiteCardDataService Methods (30 min)
- [x] Implement `export_to_path()` (database copy)
- [x] Implement `import_from_path()` (database restore)
- [x] Implement `get_last_update_date()` (query MAX(released_at))
- [x] Add error handling for missing files
- [x] Test methods with real data

### Step 3: Implement ChromaRAGService Methods (30 min)
- [x] Implement `export_embeddings()` (directory copy)
- [x] Implement `import_embeddings()` (directory restore)
- [x] Implement `get_embedding_count()` (collection.count())
- [x] Handle ChromaDB persistence properly
- [x] Test methods with real data

### Step 4: Create Data Bundle Script (1 hour)
- [x] Create `scripts/build_data_bundle.py`
- [x] Use service methods for export (not direct file copy)
- [x] Gather: cards.db, chroma/, combos.json
- [x] Create manifest.json with metadata (version, dates, counts)
- [x] Create compressed tarball (tar.xz)
- [x] Test script locally with real data
- [x] Verify bundle size (~78 MB compressed - ✅ 35,402 cards + embeddings)

### Step 5: Enhance Update Command (1 hour)
- [x] Add `--since` parameter to update command
- [x] Filter Scryfall data by `released_at >= since_date`
- [x] Only import cards newer than since date
- [x] Update embeddings for new cards only (existing flow)
- [x] Test incremental update flow (command works, filtering logic implemented)
- [x] Document usage in help text

### Step 6: Update Setup Wizard (1 hour)
- [x] Add `download_bundle()` function with progress bar
- [x] Add `extract_bundle()` function (tar.xz extraction)
- [x] Add `read_manifest()` function
- [x] Integrate: download → extract → read manifest → incremental update
- [x] Handle errors gracefully (fallback to full update)
- [ ] Test end-to-end setup flow (needs actual GitHub release)

### Step 7: Upload First Bundle (30 min)
- [x] Build bundle: `python scripts/build_data_bundle.py` (already done: 77.83 MB)
- [ ] Create GitHub release (manual step - requires GitHub access)
- [ ] Upload tarball to release assets
- [ ] Update bundle URL in setup.py (once release exists)
- [ ] Test download and extraction
- [ ] Document bundle update process for maintainers

**Completion:** ☐ PyPI package published

---

## 🐳 Priority 3: Docker Image (5-6 hours)

### Step 1.1: Package Metadata (1 hour) ✅
- [x] Update `pyproject.toml` classifiers (Alpha → Beta)
- [x] Add author email
- [x] Add keywords for discoverability (10 keywords: mtg, magic-the-gathering, card-game, combo-finder, ai, llm, rag, vector-search, embeddings, scryfall)
- [x] Add project URLs (Homepage, Repository, Issues, Documentation, Changelog)
- [x] Verify all metadata (TOML validated)

### Step 1.2: PyPI-Ready README (2 hours) ✅
- [x] Add badges (PyPI version, Python versions, license, tests)
- [x] Write quick start section (installation, setup, chat examples)
- [x] Add feature highlights with 8 key features
- [x] Add LLM provider comparison table
- [x] Keep it scannable and concise (shorter than GitHub README)
- [x] Link to full documentation on GitHub
- [x] Created README_PYPI.md (optimized for PyPI display)
- [x] Updated pyproject.toml to use README_PYPI.md

### Step 1.3: Package Testing (2 hours)
- [ ] Install build tools: `pip install build twine`
- [ ] Build package: `python -m build`
- [ ] Check for errors: `twine check dist/*`
- [ ] Test local installation in fresh virtualenv
- [ ] Test with optional dependencies
- [ ] Verify entry point: `mtg --version`
- [ ] Test setup wizard: `mtg setup`
- [ ] Test update command: `mtg update`

### Step 1.4: TestPyPI Upload (1 hour)
- [ ] Create account at test.pypi.org
- [ ] Generate API token
- [ ] Upload: `twine upload --repository testpypi dist/*`
- [ ] Test install from TestPyPI
- [ ] Verify README renders correctly
- [ ] Document any issues

### Step 1.5: Real PyPI Upload (30 min)
- [ ] Create account at pypi.org
- [ ] Generate API token
- [ ] Final checks (version, README, metadata)
- [ ] Upload: `twine upload dist/*`
- [ ] Verify package page
- [ ] Test fresh installation
- [ ] Update docs to show pip install
- [ ] Create GitHub release with v0.1.0 tag
- [ ] Announce! 🎉

---

## Priority 2: Docker Image 🐳 (5-6 hours)

### Step 2.1: Create Dockerfile (2 hours)
- [ ] Create multi-stage Dockerfile
- [ ] Stage 1: Builder (compile dependencies)
- [ ] Stage 2: Runtime (minimal image)
- [ ] Test build: `docker build -t mtg-card-app .`
- [ ] Test run: `docker run mtg-card-app --version`
- [ ] Verify image size is reasonable (<2.5 GB)
- [ ] Test interactive mode: `docker run -it mtg-card-app`

### Step 2.2: Create docker-compose.yml (1 hour)
- [ ] Create docker-compose.yml
- [ ] Configure volume mounts for persistence
- [ ] Add Ollama service (optional)
- [ ] Test: `docker-compose up`
- [ ] Test configuration persistence
- [ ] Document usage

### Step 2.3: Publish to GHCR (1 hour)
- [ ] Create GitHub personal access token (packages:write)
- [ ] Login: `echo $TOKEN | docker login ghcr.io -u USERNAME --password-stdin`
- [ ] Tag: `docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:latest`
- [ ] Tag version: `docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:0.1.0`
- [ ] Push latest: `docker push ghcr.io/topherhaynie/mtg-card-app:latest`
- [ ] Push version: `docker push ghcr.io/topherhaynie/mtg-card-app:0.1.0`
- [ ] Make package public in GitHub settings
- [ ] Test pull: `docker pull ghcr.io/topherhaynie/mtg-card-app:latest`

### Step 2.4: Docker Documentation (1 hour)
- [ ] Add Docker section to README
- [ ] Create docs/DOCKER.md
- [ ] Document volume mounts
- [ ] Document environment variables
- [ ] Add docker-compose examples
- [ ] Document using with external Ollama
- [ ] Add troubleshooting section

---

## Priority 3: CI/CD Pipeline 🔄 (6-7 hours)

### Step 3.1: Testing Workflow (2 hours)
- [ ] Create `.github/workflows/` directory
- [ ] Create `test.yml` workflow
- [ ] Configure matrix: 3 OS × 3 Python versions
- [ ] Add pytest with coverage
- [ ] Test on push to branch
- [ ] Verify all jobs pass
- [ ] Add status badge to README
- [ ] (Optional) Set up Codecov integration

### Step 3.2: Release Workflow (2 hours)
- [ ] Create `release.yml` workflow
- [ ] Trigger on version tags (v*)
- [ ] Build package
- [ ] Upload to PyPI with token
- [ ] Create GitHub Release
- [ ] Attach dist files to release
- [ ] Add PYPI_API_TOKEN to GitHub Secrets
- [ ] Test with v0.1.0 tag (or use v0.1.1 for testing)
- [ ] Document release process

### Step 3.3: Docker Build Workflow (2 hours)
- [ ] Create `docker.yml` workflow
- [ ] Configure Docker Buildx
- [ ] Login to GHCR automatically
- [ ] Extract metadata for tags
- [ ] Build and push on main branch
- [ ] Build and push on version tags
- [ ] Use GitHub Actions cache
- [ ] Verify images appear in GHCR
- [ ] Add Docker status badge to README

---

## Priority 4: Pre-computed Data Bundle 📊 (7-8 hours)

### Step 4.1: Bundle Build Script (2 hours)
- [ ] Create `scripts/build_data_bundle.py`
- [ ] Include cards.db, combos.json, chroma/
- [ ] Create manifest.json with metadata
- [ ] Use xz compression (smallest)
- [ ] Test building bundle locally
- [ ] Verify bundle size (<200 MB)
- [ ] Test extracting bundle
- [ ] Document bundle format

### Step 4.2: Setup Command Integration (2 hours)
- [ ] Add bundle download to setup wizard
- [ ] Implement download with progress bar
- [ ] Add checksum verification (SHA256)
- [ ] Handle download failures gracefully
- [ ] Fallback to `mtg update` if download fails
- [ ] Test download and extraction
- [ ] Verify data works after extraction

### Step 4.3: Upload Bundle to GitHub (1 hour)
- [ ] Build first data bundle
- [ ] Create GitHub release (v0.1.0-data)
- [ ] Upload tarball as release asset
- [ ] Document download URL
- [ ] Test download in setup wizard
- [ ] Update setup wizard with correct URL

### Step 4.4: Automate Bundle Creation (2 hours)
- [ ] Create `data-bundle.yml` workflow
- [ ] Configure manual trigger (workflow_dispatch)
- [ ] Add monthly schedule (optional)
- [ ] Run `mtg update` to get latest cards
- [ ] Build bundle with script
- [ ] Create release automatically
- [ ] Attach bundle to release
- [ ] Test manual trigger
- [ ] Document process for maintainers

---

## Documentation Updates

### Files to Create/Update
- [ ] README.md - Add installation section with pip/docker
- [ ] docs/INSTALLATION.md - Comprehensive guide for all methods
- [ ] docs/DOCKER.md - Docker-specific documentation
- [ ] docs/CONTRIBUTING.md - Release process for maintainers
- [ ] docs/phases/PHASE_6_TRACK_3_COMPLETE.md - Summary when done

### Badges to Add to README
- [ ] PyPI version
- [ ] Python versions supported
- [ ] License
- [ ] CI status (tests)
- [ ] Docker build status
- [ ] Coverage (optional)

---

## External Accounts & Tokens

### Required Accounts
- [ ] PyPI account created
- [ ] TestPyPI account created
- [ ] GitHub Container Registry (automatic with GitHub)
- [ ] Codecov account (optional)

### Tokens/Secrets
- [ ] PyPI API token generated
- [ ] TestPyPI API token generated
- [ ] `PYPI_API_TOKEN` added to GitHub Secrets
- [ ] GitHub personal access token for GHCR (packages:write)

---

## Testing Checklist

### Local Testing
- [ ] Package builds without errors
- [ ] Package installs in fresh virtualenv
- [ ] All CLI commands work after pip install
- [ ] Docker image builds successfully
- [ ] Docker container runs correctly
- [ ] Data bundle downloads and extracts

### CI Testing
- [ ] Tests pass on Ubuntu
- [ ] Tests pass on macOS
- [ ] Tests pass on Windows
- [ ] Tests pass on Python 3.10, 3.11, 3.12
- [ ] Docker builds in GitHub Actions
- [ ] Release workflow triggers correctly

### Integration Testing
- [ ] Fresh install on clean system
- [ ] Setup wizard completes successfully
- [ ] Update command downloads cards
- [ ] All 11 CLI commands functional
- [ ] Docker container persists configuration
- [ ] Optional dependencies install correctly

---

## Success Metrics

### Core Metrics
- [ ] Installation time: < 5 minutes
- [ ] Package size: < 50 MB (without data)
- [ ] Docker image size: < 2.5 GB
- [ ] Data bundle size: < 200 MB compressed
- [ ] Test pass rate: 100%

### User Experience
- [ ] One command install: `pip install mtg-card-app`
- [ ] Works on all 3 major platforms
- [ ] Clear error messages for issues
- [ ] Documentation covers all scenarios
- [ ] No manual dependency installation needed

---

## Completion Criteria

### Must Complete
- ✅ Package on PyPI
- ✅ Docker image on GHCR
- ✅ Automated tests running
- ✅ Documentation updated
- ✅ Installation < 5 minutes

### Nice to Have
- 🎯 Pre-computed data bundle
- 🎯 Automated releases
- 🎯 Coverage reports
- 🎯 All badges on README

### Future Work (Phase 6.1)
- 🔮 Native installers
- 🔮 Homebrew formula
- 🔮 Auto-update mechanism

---

## Progress Log

### 2025-10-22
- ✅ Created Track 3 detailed plan
- ✅ Created this checklist
- 🚧 Starting PyPI preparation

---

**Next Action:** Update pyproject.toml metadata
**Blockers:** None
**ETA:** 1-2 weeks to complete all priorities

