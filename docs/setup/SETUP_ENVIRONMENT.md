# Environment Setup Guide

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (install from https://github.com/astral-sh/uv)

## Quick Setup

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Create Virtual Environment

```bash
# Create the virtual environment
uv venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Install the package in editable mode
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
```

## Verify Installation

```bash
# Check installed packages
uv pip list

# Run the demo
python -m examples.data_layer_demo
```

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Coverage

```bash
pytest --cov=mtg_card_app --cov-report=html
```

### Running the Application

```bash
# Run the data layer demo
python -m examples.data_layer_demo

# Or use the entry points defined in pyproject.toml
mtg-card-app
```

## Using uv Commands

### Install a new package

```bash
uv pip install package-name
```

### Update dependencies

```bash
uv pip install --upgrade package-name
```

### Freeze dependencies

```bash
uv pip freeze > requirements.txt
```

### Sync dependencies from requirements.txt

```bash
uv pip sync requirements.txt
```

## Project Structure

```
mtg_card_app/
├── .venv/                  # Virtual environment (ignored by git)
├── data/                   # Runtime data (ignored by git)
├── mtg_card_app/          # Main package
├── examples/              # Example scripts
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
└── README.md              # Project documentation
```

## Environment Variables

Currently, no environment variables are required. The application uses:
- Local JSON storage (in `data/` directory)
- Free Scryfall API (no API key needed)

## Troubleshooting

### Virtual environment not activating

Make sure you're in the project root directory and run:
```bash
source .venv/bin/activate
```

### Import errors

Ensure the package is installed in editable mode:
```bash
uv pip install -e .
```

### Permission errors on macOS/Linux

If you get permission errors, make sure the activate script is executable:
```bash
chmod +x .venv/bin/activate
```

## Updating the Environment

To update all dependencies to their latest compatible versions:

```bash
uv pip install --upgrade -e ".[dev]"
```

## Clean Installation

To start fresh:

```bash
# Remove the virtual environment
rm -rf .venv

# Recreate it
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Next Steps

Once your environment is set up:

1. Read `DATA_LAYER_SETUP.md` for architecture overview
2. Run `python -m examples.data_layer_demo` to see it in action
3. Check out `ARCHITECTURE_FLOW.md` for detailed diagrams
4. Start building new features!
