#!/usr/bin/env python3
"""Debug: Full hybrid scoring breakdown for Isochron Scepter."""

import logging
from mtg_card_app.core.manager_registry import ManagerRegistry  
from mtg_card_app.core.interactor import Interactor

# Set to DEBUG to see all the scoring details
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s: %(message)s')
logger = logging.getLogger()

# Filter out noisy debug messages
class DebugFilter(logging.Filter):
    def filter(self, record):
        # Only show our debug messages, not library stuff
        if 'weighted=' in record.msg or 'Exact match candidate' in record.msg or 'Top' in record.msg:
            return True
        if record.levelname in ['INFO', 'WARNING', 'ERROR']:
            if 'Step' in record.msg or 'combo' in record.msg.lower() or 'dramatic' in record.msg.lower():
                return True
        return False

for handler in logger.handlers:
    handler.addFilter(DebugFilter())

def full_debug():
    print("=" * 80)
    print("FULL HYBRID SCORING DEBUG - Isochron Scepter")
    print("=" * 80)
    
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        query_cache=registry.query_cache,
    )
    
    print("\nRunning find_combo_pieces with use_cache=False...")
    result = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)
    
    print("\n" + "=" * 80)
    print("CHECKING RESULTS FOR DRAMATIC REVERSAL")
    print("=" * 80)
    
    if "dramatic reversal" in result.lower():
        print("✅ FOUND in final results!")
    else:
        print("❌ NOT FOUND in final results")

if __name__ == "__main__":
    full_debug()
