# Data Bundle Release Guide

## Overview

This guide explains how to build and release data bundles for the MTG Card App. Data bundles enable fast 2-minute setup for users instead of 10-minute full downloads.

## Bundle Information

- **Current Bundle:** `mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz`
- **Size:** 77.83 MB compressed
- **Contents:**
  - 35,402 cards (cards.db)
  - 35,402 embeddings (chroma/)
  - Combos (combos.json)
  - Metadata (manifest.json)

## Building a New Bundle

### Prerequisites

1. Ensure you have current card data:
   ```bash
   mtg update  # If needed to refresh data
   ```

2. Verify data integrity:
   ```bash
   mtg stats  # Should show 35k+ cards and embeddings
   ```

### Build Command

```bash
python scripts/build_data_bundle.py
```

**Output:**
- Location: `dist/mtg-card-app-data-bundle-v{version}-{date}.tar.xz`
- Build time: ~75 seconds
- Compression: tar.xz (best compression ratio)

**Manifest Contents:**
```json
{
  "version": "0.1.0",
  "build_date": "2025-10-22T...",
  "last_card_date": null,  // Will be populated once released_at is tracked
  "card_count": 35402,
  "embedding_count": 35402,
  "files": [
    "cards.db",
    "chroma/",
    "combos.json",
    "manifest.json"
  ]
}
```

## Publishing to GitHub Releases

### Step 1: Create a GitHub Release

```bash
# Using GitHub CLI (recommended)
gh release create data-v0.1.0 \
  dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz \
  --title "Data Bundle v0.1.0" \
  --notes "Pre-built data bundle with 35,402 cards and embeddings. Enables 2-minute setup."

# Alternative: Manual upload via GitHub web interface
# 1. Go to: https://github.com/topherhaynie/mtg_card_app/releases/new
# 2. Tag: data-v0.1.0
# 3. Title: Data Bundle v0.1.0
# 4. Upload: dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz
```

### Step 2: Create Latest Bundle Alias

For convenience, create a `latest` tag that always points to the newest bundle:

```bash
# After uploading the versioned bundle
gh release create data-latest \
  dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz \
  --title "Latest Data Bundle" \
  --notes "Always points to the most recent data bundle."

# Or update existing latest release
gh release upload data-latest \
  dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz \
  --clobber
```

### Step 3: Update Setup Wizard URL

Once the release is published, update the download URL in `setup.py`:

**Current placeholder URL:**
```python
bundle_url = "https://github.com/topherhaynie/mtg_card_app/releases/latest/download/mtg-card-app-data-bundle-latest.tar.xz"
```

**Update to actual filename:**
```python
bundle_url = "https://github.com/topherhaynie/mtg_card_app/releases/download/data-latest/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz"
```

Or keep using `/latest/download/` with a consistent filename:
1. Rename bundle to: `mtg-card-app-data-bundle-latest.tar.xz`
2. Upload to `data-latest` release
3. URL will work as-is

### Step 4: Test the Setup Flow

```bash
# Remove existing data (backup first!)
mv data data.bak

# Run setup wizard
mtg setup

# Select option 1 (Download pre-built bundle)
# Verify:
# - Download progress shows
# - Extraction completes
# - Manifest displays correctly
# - Incremental update runs

# Verify data
mtg stats  # Should show 35k+ cards
```

## Bundle Update Schedule

### When to Build New Bundles

1. **Major Releases** (every 2-3 months)
   - New set releases
   - Significant card database updates
   - Version bumps (0.2.0, 0.3.0, etc.)

2. **On Demand** (as needed)
   - Database schema changes
   - Embedding model updates
   - Critical bug fixes requiring data rebuild

### Versioning Scheme

- **data-v{version}**: Matches app version (e.g., data-v0.1.0)
- **data-latest**: Always points to most recent bundle
- Bundle filename includes date: `v0_1_0-20251022`

## Maintenance

### Checking Bundle Size

```bash
ls -lh dist/mtg-card-app-data-bundle-*.tar.xz
# Target: ~80-100 MB compressed
```

### Verifying Bundle Contents

```bash
tar -tf dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz
# Should show: data/cards.db, data/chroma/, data/combos.json, data/manifest.json
```

### Testing Bundle Locally

```bash
# Extract to temporary directory
mkdir -p /tmp/test_bundle
tar -xf dist/mtg-card-app-data-bundle-v0_1_0-20251022.tar.xz -C /tmp/test_bundle

# Verify contents
ls -la /tmp/test_bundle/data/
```

## Automation (Future Enhancement)

### CI/CD Bundle Publishing

Add to `.github/workflows/release.yml`:

```yaml
- name: Build Data Bundle
  run: python scripts/build_data_bundle.py

- name: Upload Bundle to Release
  uses: softprops/action-gh-release@v1
  with:
    files: dist/mtg-card-app-data-bundle-*.tar.xz
  if: startsWith(github.ref, 'refs/tags/v')
```

### Scheduled Bundle Updates

Create `.github/workflows/data-bundle.yml`:

```yaml
name: Build Monthly Data Bundle
on:
  schedule:
    - cron: '0 0 1 * *'  # First day of each month
  workflow_dispatch:  # Manual trigger

jobs:
  build-bundle:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e .
      - name: Update card data
        run: mtg update
      - name: Build bundle
        run: python scripts/build_data_bundle.py
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: data-${{ github.run_number }}
          files: dist/mtg-card-app-data-bundle-*.tar.xz
```

## Troubleshooting

### Bundle Too Large

- Check for duplicate files
- Verify compression (tar.xz vs tar.gz)
- Consider excluding test data

### Download Fails in Setup

- Verify release is public
- Check URL is accessible
- Test with `curl` or `wget`

### Extraction Errors

- Verify tar.xz format
- Check disk space
- Ensure proper permissions

## Quick Reference

```bash
# Build bundle
python scripts/build_data_bundle.py

# Create release (requires gh CLI)
gh release create data-v0.1.0 dist/*.tar.xz \
  --title "Data Bundle v0.1.0" \
  --notes "Pre-built data bundle"

# Test setup
mtg setup

# Verify
mtg stats
```

## Next Steps

1. ✅ Build bundle (done: 77.83 MB)
2. ⏳ Create GitHub release
3. ⏳ Upload bundle
4. ⏳ Update setup.py URL
5. ⏳ Test end-to-end
6. ⏳ Document in README

---

**Last Updated:** October 22, 2025  
**Bundle Version:** v0.1.0  
**Bundle Date:** 2025-10-22
