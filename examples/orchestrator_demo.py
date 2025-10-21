"""orchestrator_demo.py - Example usage of Interactor for natural language MTG queries

MIGRATED: Now uses Interactor instead of deprecated QueryOrchestrator.
The Interactor provides clean architecture with proper dependency injection.
"""

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

if __name__ == "__main__":
    # Create manager registry with default services
    registry = ManagerRegistry.get_instance()

    # Create interactor (business logic layer)
    interactor = Interactor(registry=registry)

    user_query = "Find three blue card draw spells under 3 mana."
    print(f"User Query: {user_query}\n")

    # Use Interactor's natural language query method
    response = interactor.answer_natural_language_query(user_query)
    print(f"Interactor Response:\n{response}")
