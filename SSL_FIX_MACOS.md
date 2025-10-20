# SSL Certificate Fix for macOS

## Issue

On macOS, you may encounter SSL certificate verification errors when the Scryfall service tries to fetch card data:

```
ssl.SSLCertVerifyError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

This is a common issue with Python on macOS, especially if you installed Python directly rather than through Homebrew.

## Solutions

### Option 1: Run the Certificate Install Script (Recommended)

Python on macOS comes with a script to install certificates:

```bash
# For Python 3.13 (adjust version as needed)
/Applications/Python\ 3.13/Install\ Certificates.command
```

Or run this in terminal:

```bash
cd /Applications/Python\ 3.*/
open Install\ Certificates.command
```

### Option 2: Install certifi

Install the certifi package which provides Mozilla's certificate bundle:

```bash
source .venv/bin/activate
uv pip install certifi
```

Then test:

```bash
python -c "import ssl; import certifi; print(ssl.get_default_verify_paths())"
```

### Option 3: Install Certificates via pip

```bash
source .venv/bin/activate
uv pip install --upgrade certifi
```

### Option 4: Use Homebrew Python

If you installed Python with Homebrew, it should already have certificates configured:

```bash
brew install python@3.13
```

## Testing the Fix

After applying one of the solutions above, test that it works:

```bash
source .venv/bin/activate
python -c "
from mtg_card_app.interfaces.card_data import ScryfallCardDataService

service = ScryfallCardDataService()
print('Testing Scryfall service...')

try:
    card = service.get_card_by_name('Sol Ring', exact=True)
    if card:
        print(f'✅ Success! Got card: {card[\"name\"]}')
    else:
        print('❌ Card returned None')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

If you see "✅ Success! Got card: Sol Ring", the SSL certificates are working!

## Running the Demo

After fixing SSL certificates, you can run the full demo:

```bash
python -m examples.data_layer_demo
```

## Alternative: Mock Service for Testing

If you can't fix the SSL issue immediately, you can create a mock service for testing:

```python
from mtg_card_app.interfaces.card_data.base import CardDataService
from typing import Optional, Dict, Any, List

class MockCardDataService(CardDataService):
    """Mock service that returns fake data without making API calls."""
    
    def __init__(self):
        self.mock_data = {
            "Sol Ring": {
                "id": "mock-sol-ring",
                "name": "Sol Ring",
                "mana_cost": "{1}",
                "type_line": "Artifact",
                "oracle_text": "{T}: Add {C}{C}.",
                "prices": {"usd": "1.50"}
            },
            # Add more mock cards as needed
        }
    
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        return self.mock_data.get(name)
    
    # Implement other required methods...

# Use it:
from mtg_card_app.core import ManagerRegistry, Interactor

mock_service = MockCardDataService()
registry = ManagerRegistry(card_data_service=mock_service)
interactor = Interactor(registry=registry)

# Now it works without SSL!
card = interactor.fetch_card("Sol Ring")
```

## Why This Happens

macOS ships with its own OpenSSL certificates, but Python needs its own bundle. When you install Python from python.org, it doesn't automatically trust the system certificates. The solutions above install the necessary certificate bundle so Python can verify HTTPS connections.
