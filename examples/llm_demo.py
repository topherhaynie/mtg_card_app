"""llm_demo.py - Example usage of OllamaLLMService for natural language MTG queries"""

from mtg_card_app.managers.llm.services.ollama_service import OllamaLLMService

if __name__ == "__main__":
    service = OllamaLLMService(model="llama3")
    prompt = "Suggest three blue card draw spells in Magic: The Gathering that cost 3 mana or less."
    print(f"Prompt: {prompt}\n")
    response = service.generate(prompt, max_tokens=256)
    print(f"LLM Response:\n{response}")
