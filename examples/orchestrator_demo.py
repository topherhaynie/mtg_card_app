"""orchestrator_demo.py - Example usage of QueryOrchestrator for natural language MTG queries"""

from mtg_card_app.managers.rag.embedding_manager import EmbeddingManager
from mtg_card_app.managers.rag.vector_store_manager import VectorStoreManager

from mtg_card_app.core.orchestrator import QueryOrchestrator
from mtg_card_app.managers.card_data.manager import CardDataManager
from mtg_card_app.managers.llm.manager import LLMManager
from mtg_card_app.managers.llm.services.ollama_service import OllamaLLMService

if __name__ == "__main__":
    llm_manager = LLMManager(service=OllamaLLMService(model="llama3"))
    card_data_manager = CardDataManager()
    embedding_manager = EmbeddingManager()
    vector_store_manager = VectorStoreManager()

    orchestrator = QueryOrchestrator(
        llm_manager=llm_manager,
        card_data_manager=card_data_manager,
        embedding_manager=embedding_manager,
        vector_store_manager=vector_store_manager,
    )

    user_query = "Find three blue card draw spells under 3 mana."
    print(f"User Query: {user_query}\n")
    response = orchestrator.answer_query(user_query)
    print(f"Orchestrator Response:\n{response}")
