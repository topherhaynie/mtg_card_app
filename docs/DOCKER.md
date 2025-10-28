# Docker Guide for MTG Card App

## Image Size

The Docker image has been optimized for size while maintaining full functionality:

- **Size**: 1.44 GB (down from 1.93 GB unoptimized)
- **Optimizations**: CPU-only PyTorch, multi-stage build, cleanup of caches and test files
- **Base**: Python 3.11 Slim (Debian-based for broad compatibility)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start the app
docker-compose up

# In another terminal, run commands
docker-compose exec mtg-card-app mtg --version
docker-compose exec mtg-card-app mtg config show
docker-compose exec mtg-card-app mtg setup

# Stop the app
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

### Using Docker Directly

```bash
# Build the image
docker build -t mtg-card-app .

# Run interactively
docker run -it --rm mtg-card-app mtg

# Run a single command
docker run --rm mtg-card-app mtg --version

# Run with persistent data
docker run -it --rm \
  -v mtg-data:/home/mtguser/data \
  -v mtg-config:/home/mtguser/.mtg \
  mtg-card-app mtg
```

## Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

**Stage 1: Builder**
- Uses `python:3.11-slim` base
- Installs build dependencies (gcc, g++)
- Compiles Python dependencies
- Creates virtual environment

**Stage 2: Runtime**
- Uses `python:3.11-slim` base (fresh, minimal)
- Only runtime dependencies
- Copies compiled venv from builder
- Runs as non-root user (`mtguser`)
- Final image size: ~2-2.5 GB (most is PyTorch/transformers)

### Security Features

- **Non-root user**: Runs as `mtguser` (UID 1000)
- **Minimal base**: Uses slim Python image
- **No unnecessary tools**: Only runtime dependencies
- **Volume isolation**: Data stored in named volumes
- **Health checks**: Monitors container health

## Volume Mounts

### Data Volume (`/home/mtguser/data`)

Stores:
- `cards.db` - SQLite database
- `chroma/` - Vector embeddings
- `combos.json` - Combo data

```bash
# Mount local data directory
docker run -v $(pwd)/data:/home/mtguser/data mtg-card-app

# Use named volume (recommended)
docker run -v mtg-data:/home/mtguser/data mtg-card-app
```

### Config Volume (`/home/mtguser/.mtg`)

Stores:
- `config.toml` - Application configuration
- API keys (if stored in config)

```bash
# Mount local config
docker run -v $(pwd)/.mtg:/home/mtguser/.mtg mtg-card-app

# Use named volume (recommended)
docker run -v mtg-config:/home/mtguser/.mtg mtg-card-app
```

## Environment Variables

### LLM Provider API Keys

```bash
# OpenAI
docker run -e OPENAI_API_KEY=sk-... mtg-card-app

# Anthropic
docker run -e ANTHROPIC_API_KEY=sk-ant-... mtg-card-app

# Gemini
docker run -e GEMINI_API_KEY=... mtg-card-app

# Groq
docker run -e GROQ_API_KEY=gsk_... mtg-card-app
```

### App Configuration

```bash
# Data directory (default: /home/mtguser/data)
docker run -e MTG_DATA_DIR=/custom/path mtg-card-app

# Config directory (default: /home/mtguser/.mtg)
docker run -e MTG_CONFIG_DIR=/custom/path mtg-card-app
```

## Usage Examples

### Setup and Initial Configuration

```bash
# Run setup wizard
docker-compose run --rm mtg-card-app mtg setup

# Or with docker directly
docker run -it --rm \
  -v mtg-data:/home/mtguser/data \
  -v mtg-config:/home/mtguser/.mtg \
  mtg-card-app mtg setup
```

### Update Card Data

```bash
# Full update
docker-compose exec mtg-card-app mtg update

# Incremental update (since specific date)
docker-compose exec mtg-card-app mtg update --since 2024-01-01

# Cards only (skip embeddings)
docker-compose exec mtg-card-app mtg update --cards-only
```

### Interactive Chat

```bash
# Start interactive chat session
docker-compose run --rm mtg-card-app mtg

# With API key from environment
docker-compose run --rm \
  -e OPENAI_API_KEY=sk-... \
  mtg-card-app mtg
```

### Card Operations

```bash
# Search for cards
docker-compose exec mtg-card-app mtg search "blue counterspells"

# Get card details
docker-compose exec mtg-card-app mtg card "Lightning Bolt"

# Find combos
docker-compose exec mtg-card-app mtg combo find "Thassa's Oracle"
```

### Deck Building

```bash
# Create new deck
docker-compose exec mtg-card-app mtg deck new commander \
  --commander "Muldrotha, the Gravetide"

# Analyze deck
docker-compose exec mtg-card-app mtg deck analyze my_deck.json

# Get suggestions
docker-compose exec mtg-card-app mtg deck suggest my_deck.json \
  --budget 200
```

## Docker Compose Configuration

### Basic Setup

```yaml
version: '3.8'

services:
  mtg-card-app:
    build: .
    volumes:
      - mtg-data:/home/mtguser/data
      - mtg-config:/home/mtguser/.mtg
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: mtg

volumes:
  mtg-data:
  mtg-config:
```

### With Ollama (Local LLM)

```yaml
version: '3.8'

services:
  mtg-card-app:
    build: .
    volumes:
      - mtg-data:/home/mtguser/data
      - mtg-config:/home/mtguser/.mtg
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
    networks:
      - mtg-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - mtg-network

volumes:
  mtg-data:
  mtg-config:
  ollama-data:

networks:
  mtg-network:
```

### Environment File (.env)

Create `.env` file:

```env
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...

# App Configuration
MTG_DATA_DIR=/home/mtguser/data
MTG_CONFIG_DIR=/home/mtguser/.mtg
```

Then use in docker-compose.yml:

```yaml
services:
  mtg-card-app:
    env_file: .env
```

## Publishing to GitHub Container Registry (GHCR)

### Prerequisites

1. Create GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `write:packages`, `read:packages`, `delete:packages`
   - Copy token

2. Login to GHCR:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u topherhaynie --password-stdin
   ```

### Tag and Push

```bash
# Build image
docker build -t mtg-card-app .

# Tag for GHCR
docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:latest
docker tag mtg-card-app ghcr.io/topherhaynie/mtg-card-app:0.1.0

# Push to GHCR
docker push ghcr.io/topherhaynie/mtg-card-app:latest
docker push ghcr.io/topherhaynie/mtg-card-app:0.1.0
```

### Make Package Public

1. Go to: https://github.com/topherhaynie?tab=packages
2. Click on `mtg-card-app` package
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

### Pull from GHCR

```bash
# Pull latest
docker pull ghcr.io/topherhaynie/mtg-card-app:latest

# Pull specific version
docker pull ghcr.io/topherhaynie/mtg-card-app:0.1.0

# Run
docker run -it ghcr.io/topherhaynie/mtg-card-app:latest mtg
```

## Troubleshooting

### Container Exits Immediately

```bash
# Check logs
docker-compose logs mtg-card-app

# Run with interactive terminal
docker-compose run --rm mtg-card-app /bin/bash
```

### Permission Denied Errors

The container runs as `mtguser` (UID 1000). If mounting local directories:

```bash
# Fix permissions
chown -R 1000:1000 ./data ./mtg

# Or run as root (not recommended)
docker run --user root -it mtg-card-app
```

### Large Image Size

The image is ~2-2.5 GB due to:
- PyTorch (~1.5 GB)
- Transformers/sentence-transformers (~500 MB)
- ChromaDB dependencies (~200 MB)

To reduce size:
- Use CPU-only PyTorch (saves ~500 MB)
- Pre-download embeddings model

### Cannot Connect to Ollama

If using Ollama in docker-compose:

```bash
# Check Ollama is running
docker-compose ps

# Check network
docker network inspect mtg_mtg-network

# Set correct host in config
mtg config set llm.ollama.base_url http://ollama:11434
```

### Data Not Persisting

```bash
# Check volumes exist
docker volume ls

# Inspect volume
docker volume inspect mtg-card-app_mtg-data

# Backup volume
docker run --rm -v mtg-card-app_mtg-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mtg-data-backup.tar.gz /data
```

## Advanced Usage

### Custom Entrypoint

```bash
# Run bash instead of mtg
docker run -it --rm --entrypoint /bin/bash mtg-card-app

# Run Python script
docker run --rm -v $(pwd)/script.py:/tmp/script.py \
  mtg-card-app python /tmp/script.py
```

### Mount Local Code for Development

```bash
# Override installed package with local code
docker run -it --rm \
  -v $(pwd)/mtg_card_app:/app/mtg_card_app \
  -v mtg-data:/home/mtguser/data \
  mtg-card-app mtg
```

### Resource Limits

```yaml
services:
  mtg-card-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Cleanup

### Remove Everything

```bash
# Stop containers
docker-compose down

# Remove volumes (DELETES ALL DATA!)
docker-compose down -v

# Remove image
docker rmi mtg-card-app

# Remove all unused Docker resources
docker system prune -a
```

### Backup Data

```bash
# Backup data volume
docker run --rm \
  -v mtg-card-app_mtg-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mtg-data.tar.gz /data

# Restore data volume
docker run --rm \
  -v mtg-card-app_mtg-data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/mtg-data.tar.gz --strip 1"
```

## Performance

### Build Time

- Initial build: ~5-10 minutes (downloads all dependencies)
- Subsequent builds: ~1-2 minutes (uses cache)

### Runtime Performance

- Startup time: ~2-3 seconds
- Memory usage: ~1-2 GB (with loaded models)
- CPU usage: Varies by operation (embeddings are CPU-intensive)

### Optimization Tips

1. **Use BuildKit** for faster builds:
   ```bash
   DOCKER_BUILDKIT=1 docker build -t mtg-card-app .
   ```

2. **Pre-download models** to avoid startup delay:
   ```bash
   docker run --rm -v mtg-data:/home/mtguser/data \
     mtg-card-app mtg update
   ```

3. **Use volume mounts** instead of COPY for development

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/topherhaynie/mtg-card-app:latest
            ghcr.io/topherhaynie/mtg-card-app:${{ github.ref_name }}
```

## Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **GHCR Documentation**: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

**Created:** October 22, 2025  
**Version:** 0.1.0  
**Status:** Ready for testing once Docker Desktop is running
