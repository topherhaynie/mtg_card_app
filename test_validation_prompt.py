#!/usr/bin/env python3
"""Test the validation prompt directly with Dramatic Reversal to verify mana rocks mention."""

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

def main():
    # Initialize
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    # Get the cards
    isochron = interactor.card_data_manager.get_card("Isochron Scepter")
    dramatic = interactor.card_data_manager.get_card("Dramatic Reversal")
    
    # Build validation prompt manually (simplified version)
    combo_prompt = f"""You are an expert Magic: The Gathering combo analyst.

Base Card:
Name: {isochron.name}
Type: {isochron.type_line}
Text: {isochron.oracle_text}

NOTE: This card has a tap ability. Cards that UNTAP it can create infinite loops if you can generate net mana.
NOTE: This card COPIES a spell. If the copied spell can UNTAP this card, you can create an infinite loop.

Potential Combo Piece:
Name: {dramatic.name}
Type: {dramatic.type_line}
Text: {dramatic.oracle_text}

Analyze the ACTUAL MECHANICAL INTERACTION:

1. **How does it combo with {isochron.name}?**
   - Be SPECIFIC about the sequence of actions
   - If it creates an INFINITE LOOP, explain the loop clearly

2. **What does the combo accomplish?**
   - Infinite mana? Infinite casts? Infinite damage? Card advantage?

3. **Are there any additional pieces needed?**
   - CRITICAL FOR TAP ABILITY LOOPS: If {isochron.name} has an activation cost and this creates an infinite loop by untapping, you MUST account for mana requirements:
     * Isochron Scepter costs {{2}} to activate → requires mana rocks producing ≥{{2}} (Sol Ring, Arcane Signet, Thought Vessel)
     * Without mana rocks: Can't pay activation cost repeatedly → NOT infinite
   - BE SPECIFIC: If it needs mana rocks, say which types and why
   - Example: "Yes, needs mana rocks producing ≥{{2}} (Sol Ring, Arcane Signet, etc.) to pay for repeated activations"

4. **Power level**: casual, competitive, or cEDH-viable

CRITICAL RULES FOR INFINITE LOOPS:
- If {isochron.name} COPIES a spell, and that spell UNTAPS {isochron.name}:
  * This creates an INFINITE LOOP
  * Sequence: (1) Pay activation cost, tap Scepter to copy spell → (2) Copied spell untaps Scepter + mana sources → (3) Tap mana sources for mana → (4) Return to step 1
  * Result: INFINITE spell casts, INFINITE untaps, INFINITE mana (with sufficient mana rocks)
  * CRITICAL MANA CALCULATION: 
    - If activation costs {{2}} (like Isochron Scepter), you MUST have mana rocks that produce ≥{{2}}
    - Example mana rocks: Sol Ring ({{2}}), Arcane Signet ({{1}}), Thought Vessel ({{1}})
    - Without ≥{{2}} from rocks: You get infinite untaps but NOT infinite mana/casts
  * WITHOUT mana rocks: NOT infinite (you run out of mana to activate)

IMPORTANT: Be honest about which combos work and which don't.
If a combo creates an INFINITE LOOP, clearly state: "This is an INFINITE COMBO" and explain the loop sequence."""
    
    print("="*80)
    print("Testing Validation Prompt with Dramatic Reversal")
    print("="*80)
    print("\nPrompt (first 500 chars):")
    print(combo_prompt[:500] + "...")
    print("\n" + "="*80)
    print("LLM Response:")
    print("="*80 + "\n")
    
    response = interactor.llm_manager.generate(combo_prompt)
    print(response)
    
    print("\n" + "="*80)
    print("Verification:")
    print("="*80)
    print(f"✓ Mentions 'infinite': {'YES' if 'infinite' in response.lower() or 'INFINITE' in response else 'NO'}")
    print(f"✓ Mentions 'mana rocks': {'YES' if 'mana rock' in response.lower() else 'NO'}")
    print(f"✓ Mentions 'Sol Ring': {'YES' if 'Sol Ring' in response else 'NO'}")
    print(f"✓ Mentions 'Arcane Signet': {'YES' if 'Arcane Signet' in response else 'NO'}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
