# PyPI Upload Guide

## Overview

This guide covers Steps 1.4 (TestPyPI) and 1.5 (PyPI) for publishing the `mtg-card-app` package.

## Prerequisites

- ✅ Package built successfully (`dist/` contains .whl and .tar.gz)
- ✅ Package tested locally
- ✅ `twine` installed (`pip install twine`)

## Step 1.4: TestPyPI Upload (Test Run)

### 1. Create TestPyPI Account

Visit: https://test.pypi.org/account/register/

- Create account with email/password
- Verify email address
- Enable 2FA (recommended)

### 2. Generate API Token

1. Go to: https://test.pypi.org/manage/account/#api-tokens
2. Click "Add API token"
3. Name: `mtg-card-app-test`
4. Scope: "Entire account" (or specific to project after first upload)
5. Copy the token (starts with `pypi-...`)
6. Save it securely - you won't see it again!

### 3. Configure Twine for TestPyPI

Create or edit `~/.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE
```

Or use environment variable:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE
```

### 4. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

**Expected output:**
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading mtg_card_app-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 115.0/115.0 kB • 00:00
Uploading mtg_card_app-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 93.0/93.0 kB • 00:00

View at:
https://test.pypi.org/project/mtg-card-app/0.1.0/
```

### 5. Test Installation from TestPyPI

```bash
# Create fresh test environment
uv venv test_pypi_venv
source test_pypi_venv/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    mtg-card-app

# Test it works
mtg --version

# Clean up
deactivate
rm -rf test_pypi_venv
```

**Note:** `--extra-index-url` is needed because dependencies aren't on TestPyPI.

### 6. Verify Package Page

Visit: https://test.pypi.org/project/mtg-card-app/

Check:
- ✅ README renders correctly (badges, formatting, code blocks)
- ✅ Metadata is correct (author, license, keywords)
- ✅ Links work (Homepage, Repository, Issues, etc.)
- ✅ Python version classifiers show correctly
- ✅ Dependencies listed

### Common Issues

**Issue: "File already exists"**
- TestPyPI/PyPI don't allow re-uploading same version
- Solution: Bump version in `pyproject.toml` and rebuild

**Issue: README not rendering**
- Check README_PYPI.md syntax
- Use `twine check dist/*` before uploading
- Test with: `python -m readme_renderer README_PYPI.md`

**Issue: Dependencies not installing**
- Make sure to use `--extra-index-url https://pypi.org/simple/`
- TestPyPI only has test packages

## Step 1.5: Real PyPI Upload (Production)

### 1. Create PyPI Account

Visit: https://pypi.org/account/register/

- Create account with email/password
- Verify email address
- **Enable 2FA (REQUIRED for new projects)**

### 2. Generate API Token

1. Go to: https://pypi.org/manage/account/#api-tokens
2. Click "Add API token"
3. Name: `mtg-card-app`
4. Scope: "Entire account" (change to project-specific after first upload)
5. Copy the token
6. Save securely!

### 3. Configure Twine for PyPI

Add to `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE
```

Or use environment variable:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE
```

### 4. Final Pre-Upload Checks

```bash
# Verify version is correct
grep '^version = ' pyproject.toml

# Verify no test/debug code
grep -r "TODO\|FIXME\|XXX" mtg_card_app/

# Run tests one more time
pytest

# Check distribution files
twine check dist/*

# Verify README renders
python -m readme_renderer README_PYPI.md -o /tmp/test.html
open /tmp/test.html  # macOS
```

### 5. Upload to PyPI

```bash
twine upload dist/*
```

**Expected output:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading mtg_card_app-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 115.0/115.0 kB • 00:01
Uploading mtg_card_app-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 93.0/93.0 kB • 00:00

View at:
https://pypi.org/project/mtg-card-app/0.1.0/
```

### 6. Test Real Installation

```bash
# Create fresh environment
uv venv pypi_test_venv
source pypi_test_venv/bin/activate

# Install from PyPI (usually available within seconds)
pip install mtg-card-app

# Test with optional extras
pip install mtg-card-app[openai]
pip install mtg-card-app[all-providers]

# Verify it works
mtg --version
mtg config show

# Clean up
deactivate
rm -rf pypi_test_venv
```

### 7. Create GitHub Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0 - Initial PyPI release"
git push origin v0.1.0

# Create GitHub release via CLI
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "First public release on PyPI!

## Installation
\`\`\`bash
pip install mtg-card-app
\`\`\`

## What's New
- 🎴 AI-powered MTG combo finder
- 🔍 Semantic search with RAG
- 🤖 Multi-provider LLM support
- 🏗️ Deck builder with combo awareness
- 📊 Rich CLI interface
- 🔌 MCP integration for Claude Desktop

## Links
- 📦 [PyPI Package](https://pypi.org/project/mtg-card-app/)
- 📖 [Documentation](https://github.com/topherhaynie/mtg_card_app#readme)
"
```

### 8. Update Documentation

Update README.md badges:
```markdown
[![PyPI version](https://img.shields.io/pypi/v/mtg-card-app.svg)](https://pypi.org/project/mtg-card-app/)
[![Downloads](https://pepy.tech/badge/mtg-card-app)](https://pepy.tech/project/mtg-card-app)
```

Update installation instructions to use PyPI:
```bash
pip install mtg-card-app  # Remove "coming soon!" note
```

### 9. Announce! 🎉

Share the release:
- GitHub Discussions
- Reddit (r/magicTCG, r/EDH)
- Twitter/X
- Discord servers

## Version Management

### Semantic Versioning

Follow [SemVer](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backwards compatible
- **PATCH** (0.1.1): Bug fixes, backwards compatible

### Releasing Updates

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (if you have one)
3. Rebuild: `python -m build`
4. Test locally
5. Upload: `twine upload dist/*`
6. Create GitHub release
7. Announce

### Yanking a Release (Emergency)

If you need to remove a broken release:

```bash
# Via PyPI web interface: Project → Releases → Options → Yank

# Or with twine
pip install pkginfo
# (No direct twine command, use web interface)
```

**Note:** Yanking doesn't delete, just marks as "yanked" and prevents new installs.

## Security Best Practices

### API Token Storage

```bash
# Store in environment (recommended)
export TWINE_PASSWORD="$(security find-generic-password -s 'PyPI Token' -w)"

# Or use keyring
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
```

### 2FA

- **Required** for PyPI since 2024
- Use authenticator app (Authy, Google Authenticator, 1Password)
- Save recovery codes securely

### Project-Specific Tokens

After first upload, create project-specific tokens:
1. PyPI → Manage Project → Settings → API tokens
2. Create token scoped to `mtg-card-app` only
3. Update `~/.pypirc` with new token
4. Delete account-wide token

## Troubleshooting

### "403 Forbidden" Error

- Check token is correct and not expired
- Verify 2FA is enabled
- Ensure token has correct scope

### "400 Bad Request" Error

- Run `twine check dist/*` first
- Check metadata in pyproject.toml
- Verify README syntax

### README Not Rendering

- Use `python -m readme_renderer README_PYPI.md`
- Check for invalid Markdown
- Test badges/links work

### Can't Upload New Version

- You can't reupload same version
- Bump version in pyproject.toml
- Delete old files from dist/
- Rebuild: `python -m build`

## Useful Commands

```bash
# Check package before upload
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Test README rendering
python -m readme_renderer README_PYPI.md -o /tmp/test.html

# View package info
pip show mtg-card-app

# Uninstall
pip uninstall mtg-card-app
```

## Resources

- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **Twine Docs**: https://twine.readthedocs.io/
- **Python Packaging Guide**: https://packaging.python.org/
- **Semantic Versioning**: https://semver.org/

---

**Current Status:** Steps 1.1-1.3 complete, ready for upload when accounts are created!

**Last Updated:** October 22, 2025
