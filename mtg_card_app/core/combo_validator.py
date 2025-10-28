"""Combo validation system for verifying card interactions.

This module provides validation and confidence scoring for card combinations,
helping filter out nonsensical suggestions and educating users about why
certain combos work or don't work.
"""

import logging
from typing import Any

from mtg_card_app.domain.entities import Card

logger = logging.getLogger(__name__)


class ComboValidator:
    """Validates card combinations for mechanical feasibility.
    
    Performs basic rules checking to determine if suggested card combinations
    can actually interact meaningfully in Magic: The Gathering.
    """

    def __init__(self, known_combos: dict[str, Any] | None = None):
        """Initialize the combo validator.
        
        Args:
            known_combos: Optional dictionary of pre-validated known combos
                         from combo database (keyed by combo ID)
        """
        self.known_combos = known_combos or {}
        logger.info(f"Initialized ComboValidator with {len(self.known_combos)} known combos")
    
    def validate_combo(self, cards: list[Card]) -> dict[str, Any]:
        """Validate a combination of cards for mechanical feasibility.
        
        Args:
            cards: List of Card entities to validate as a combo
            
        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "confidence": float (0.0-1.0),
                "score_breakdown": dict,
                "warnings": list[str],
                "is_known_combo": bool,
                "known_combo_name": str | None
            }
        """
        if not cards:
            return {
                "valid": False,
                "confidence": 0.0,
                "score_breakdown": {},
                "warnings": ["No cards provided"],
                "is_known_combo": False,
                "known_combo_name": None
            }
        
        # Check if this is a known combo first
        known_check = self._check_known_combo(cards)
        
        if known_check["is_known"]:
            return {
                "valid": True,
                "confidence": 0.95,  # High confidence for known combos
                "score_breakdown": {"known_combo_bonus": 0.95},
                "warnings": [],
                "is_known_combo": True,
                "known_combo_name": known_check["name"]
            }
        
        # Perform individual validation checks
        score_breakdown = {}
        warnings = []
        
        # 1. Mana compatibility check
        mana_score, mana_warnings = self._check_mana_compatibility(cards)
        score_breakdown["mana_compatibility"] = mana_score
        warnings.extend(mana_warnings)
        
        # 2. Color identity check
        color_score, color_warnings = self._check_color_compatibility(cards)
        score_breakdown["color_compatibility"] = color_score
        warnings.extend(color_warnings)
        
        # 3. Timing/interaction check
        timing_score, timing_warnings = self._check_timing_compatibility(cards)
        score_breakdown["timing_compatibility"] = timing_score
        warnings.extend(timing_warnings)
        
        # 4. Mechanical synergy check
        synergy_score, synergy_warnings = self._check_mechanical_synergy(cards)
        score_breakdown["mechanical_synergy"] = synergy_score
        warnings.extend(synergy_warnings)
        
        # Calculate overall confidence score (weighted average)
        weights = {
            "mana_compatibility": 0.2,
            "color_compatibility": 0.15,
            "timing_compatibility": 0.3,
            "mechanical_synergy": 0.35
        }
        
        confidence = sum(
            score_breakdown[key] * weights[key]
            for key in weights
        )
        
        # Determine if valid (confidence > 0.4 threshold)
        valid = confidence >= 0.4
        
        return {
            "valid": valid,
            "confidence": round(confidence, 3),
            "score_breakdown": score_breakdown,
            "warnings": warnings,
            "is_known_combo": False,
            "known_combo_name": None
        }
    
    def _check_known_combo(self, cards: list[Card]) -> dict[str, Any]:
        """Check if this combination matches a known combo.
        
        Args:
            cards: List of cards to check
            
        Returns:
            Dict with "is_known" bool and "name" str
        """
        if not self.known_combos:
            return {"is_known": False, "name": None}
        
        card_ids = {card.id for card in cards}
        
        for combo_id, combo_data in self.known_combos.items():
            combo_card_ids = set(combo_data.get("card_ids", []))
            
            # Check if the cards match (subset match for larger combos)
            if card_ids.issubset(combo_card_ids) or combo_card_ids.issubset(card_ids):
                return {
                    "is_known": True,
                    "name": combo_data.get("name", "Unknown Combo")
                }
        
        return {"is_known": False, "name": None}
    
    def _check_mana_compatibility(self, cards: list[Card]) -> tuple[float, list[str]]:
        """Check if the mana costs are reasonable for a combo.
        
        Args:
            cards: List of cards
            
        Returns:
            Tuple of (score 0.0-1.0, warnings list)
        """
        warnings = []
        
        # Calculate total mana cost
        total_cmc = sum(card.cmc or 0 for card in cards)
        
        # Scoring based on total cost
        if total_cmc == 0:
            # All free spells or lands
            score = 1.0
        elif total_cmc <= 4:
            # Efficient combo (2-4 mana total)
            score = 1.0
        elif total_cmc <= 8:
            # Moderate cost (5-8 mana)
            score = 0.8
        elif total_cmc <= 12:
            # High cost (9-12 mana)
            score = 0.6
            warnings.append(f"High total mana cost: {total_cmc} mana")
        else:
            # Very expensive (13+ mana)
            score = 0.3
            warnings.append(f"Very high mana cost: {total_cmc} mana - may be impractical")
        
        return score, warnings
    
    def _check_color_compatibility(self, cards: list[Card]) -> tuple[float, list[str]]:
        """Check if the color requirements are compatible.
        
        Args:
            cards: List of cards
            
        Returns:
            Tuple of (score 0.0-1.0, warnings list)
        """
        warnings = []
        
        # Collect all colors needed
        all_colors = set()
        for card in cards:
            all_colors.update(card.colors or [])
        
        color_count = len(all_colors)
        
        # Scoring based on color diversity
        if color_count == 0:
            # Colorless cards
            score = 1.0
        elif color_count == 1:
            # Mono-color
            score = 1.0
        elif color_count == 2:
            # Two colors
            score = 0.9
        elif color_count == 3:
            # Three colors
            score = 0.7
            warnings.append(f"Three-color combo - requires {', '.join(sorted(all_colors))} mana base")
        elif color_count == 4:
            # Four colors
            score = 0.5
            warnings.append(f"Four-color combo - difficult mana base")
        else:
            # Five colors
            score = 0.3
            warnings.append(f"Five-color combo - very difficult mana base")
        
        return score, warnings
    
    def _check_timing_compatibility(self, cards: list[Card]) -> tuple[float, list[str]]:
        """Check if the cards can interact at appropriate times.
        
        Checks card types and timing restrictions to see if combo is mechanically possible.
        
        Args:
            cards: List of cards
            
        Returns:
            Tuple of (score 0.0-1.0, warnings list)
        """
        warnings = []
        score = 0.7  # Base score - assume basic compatibility
        
        # Extract card types
        types = [card.type_line.lower() if card.type_line else "" for card in cards]
        
        # Check for instant-speed interaction
        has_instant = any("instant" in t for t in types)
        has_flash = any("flash" in (card.oracle_text or "").lower() for card in cards)
        instant_speed = has_instant or has_flash
        
        # Check for activated abilities
        has_activated_ability = any(
            ":" in (card.oracle_text or "") 
            for card in cards
        )
        
        # Check for enters-the-battlefield effects
        has_etb = any(
            "enters the battlefield" in (card.oracle_text or "").lower() or
            "when" in (card.oracle_text or "").lower()
            for card in cards
        )
        
        # Positive signals for interaction
        if instant_speed:
            score += 0.1
        if has_activated_ability:
            score += 0.1
        if has_etb:
            score += 0.1
        
        # Check for potential issues
        all_creatures = all("creature" in t for t in types)
        if all_creatures and not has_etb and not has_activated_ability:
            score -= 0.2
            warnings.append("All creatures without obvious synergy - check for combat/static interactions")
        
        all_sorceries = all("sorcery" in t for t in types)
        if all_sorceries and len(cards) > 1:
            score -= 0.1
            warnings.append("Multiple sorceries - limited interaction potential")
        
        return min(1.0, max(0.0, score)), warnings
    
    def _check_mechanical_synergy(self, cards: list[Card]) -> tuple[float, list[str]]:
        """Check for mechanical synergy between cards.
        
        Looks for keywords and mechanics that work together.
        
        Args:
            cards: List of cards
            
        Returns:
            Tuple of (score 0.0-1.0, warnings list)
        """
        warnings = []
        score = 0.5  # Base score
        
        # Collect oracle texts
        oracle_texts = [(card.oracle_text or "").lower() for card in cards]
        
        # Synergy keywords that indicate good interactions
        synergy_keywords = {
            "untap": ["tap", "activated ability", "mana", "artifacts"],
            "copy": ["instant", "sorcery", "spell"],
            "sacrifice": ["enters the battlefield", "dies", "death trigger"],
            "draw": ["discard", "hand size", "library"],
            "mill": ["graveyard", "library", "exile"],
            "token": ["creature", "sacrifice", "goes to the graveyard"],
            "counter": ["spell", "target"],
            "search": ["library", "shuffle", "land"],
            "reanimate": ["graveyard", "dies", "discard"],
            "storm": ["instant", "sorcery", "copy"],
            "cascade": ["instant", "sorcery", "spell"],
        }
        
        # Check for keyword synergies
        synergy_found = False
        for primary_keyword, related_keywords in synergy_keywords.items():
            has_primary = any(primary_keyword in text for text in oracle_texts)
            has_related = any(
                any(related in text for text in oracle_texts)
                for related in related_keywords
            )
            
            if has_primary and has_related:
                score += 0.15
                synergy_found = True
        
        # Check for common combo patterns
        has_untap_effect = any("untap" in text for text in oracle_texts)
        has_tap_ability = any(": " in text and "tap" in text for text in oracle_texts)
        if has_untap_effect and has_tap_ability:
            score += 0.2
            synergy_found = True
        
        # Check for infinite potential
        has_copy = any("copy" in text for text in oracle_texts)
        has_spell = any("instant" in text or "sorcery" in text for text in oracle_texts)
        if has_copy and has_spell:
            score += 0.15
            synergy_found = True
        
        if not synergy_found:
            score -= 0.1
            warnings.append("No obvious mechanical synergy detected - combo may require specific board state")
        
        return min(1.0, max(0.0, score)), warnings
    
    def get_validation_summary(self, validation_result: dict[str, Any]) -> str:
        """Generate a human-readable summary of validation results.
        
        Args:
            validation_result: Result from validate_combo()
            
        Returns:
            Formatted string summary
        """
        if validation_result["is_known_combo"]:
            return f"✅ Known combo: {validation_result['known_combo_name']} (Confidence: {validation_result['confidence']:.1%})"
        
        confidence = validation_result["confidence"]
        valid = validation_result["valid"]
        
        if valid:
            if confidence >= 0.8:
                status = "✅ Strong combo"
            elif confidence >= 0.6:
                status = "✓ Good combo"
            else:
                status = "⚠️ Moderate combo"
        else:
            status = "❌ Weak combo"
        
        lines = [f"{status} (Confidence: {confidence:.1%})"]
        
        # Add score breakdown
        breakdown = validation_result["score_breakdown"]
        if breakdown:
            lines.append("\nScore breakdown:")
            for key, value in breakdown.items():
                key_formatted = key.replace("_", " ").title()
                lines.append(f"  • {key_formatted}: {value:.1%}")
        
        # Add warnings
        warnings = validation_result["warnings"]
        if warnings:
            lines.append("\nWarnings:")
            for warning in warnings:
                lines.append(f"  ⚠️ {warning}")
        
        return "\n".join(lines)
