"""DeckBuilderManager: Core logic for deck construction and validation."""

import logging
from typing import Any

from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.utils.suggestion_cache import get_suggestion_cache

# ManagerRegistry import moved below for test monkeypatching compatibility


class DeckBuilderManager:
    def __init__(self):
        # Future: inject dependencies (card data, RAG, LLM, etc.)
        pass

    def build_deck(
        self,
        deck_format: str,
        card_pool: list[str],
        commander: str = None,
        constraints: dict = None,
        metadata: dict = None,
    ) -> Deck:
        """Build a deck for the given format and constraints.

        Args:
            deck_format: Format (e.g., 'Commander', 'Modern')
            card_pool: List of card names/IDs to select from
            commander: Commander card (if applicable)
            constraints: Dict of constraints (budget, theme, banned, etc.)
            metadata: Extra info
        Returns:
            Deck entity

        """
        # Basic implementation: select all cards, set commander, apply metadata
        deck = Deck(
            format=deck_format,
            cards=card_pool,
            sections={},
            commander=commander,
            metadata=metadata or {},
        )
        # TODO: enforce format rules, constraints, banned lists, etc.
        return deck

    def validate_deck(self, deck: Deck) -> dict[str, Any]:
        """Validate deck against format rules.
        Returns dict with validation results and errors.
        """
        errors = []
        # Example: Commander must have 100 cards, singleton, commander set
        if deck.format.lower() == "commander":
            if len(deck.cards) != 100:
                errors.append("Commander decks must have exactly 100 cards.")
            if not deck.commander:
                errors.append("Commander deck must specify a commander.")
            # TODO: check singleton, banned list, color identity, etc.
        # Other formats: add rules as needed
        return {"valid": not errors, "errors": errors}

    def analyze_deck(self, deck: Deck) -> dict[str, Any]:
        """Analyze a deck for curve, types, color identity, and basic issues.

        Returns a dict with summary statistics and findings.
        """
        summary: dict[str, Any] = {
            "format": deck.format,
            "total_cards": len(deck.cards),
            "commander": deck.commander,
            "metadata": deck.metadata,
        }

        # Try to enrich using card data (best-effort)
        try:
            from mtg_card_app.core.manager_registry import ManagerRegistry

            registry = ManagerRegistry.get_instance()
            card_data = registry.card_data_manager
        except Exception:
            card_data = None

        cmc_bins = {str(i): 0 for i in range(8)}  # 0..7 where 7 means 7+
        type_counts: dict[str, int] = {}
        colors_seen: set[str] = set()
        details_used = False

        for name in deck.cards:
            if not card_data:
                continue
            card = card_data.get_card(name)
            if not card:
                continue
            details_used = True
            # CMC binning
            cmc = int(card.cmc or 0)
            bin_key = str(cmc) if cmc < 7 else "7"
            cmc_bins[bin_key] = cmc_bins.get(bin_key, 0) + 1
            # Type counting (coarse)
            tline = (card.type_line or "").lower()
            for t in ["creature", "instant", "sorcery", "artifact", "enchantment", "planeswalker", "land"]:
                if t in tline:
                    type_counts[t] = type_counts.get(t, 0) + 1
            # Colors
            for c in card.color_identity or card.colors or []:
                colors_seen.add(c)

        issues: list[str] = []
        # Format-specific simple checks
        if deck.format.lower() == "commander":
            if len(deck.cards) != 100:
                issues.append("Commander: expected 100 cards.")
            if not deck.commander:
                issues.append("Commander: missing commander.")
            # Land count heuristic
            land_count = type_counts.get("land", 0)
            if land_count and land_count < 34:
                issues.append("Commander: consider increasing land count to ~34-38.")

        summary.update(
            {
                "mana_curve": cmc_bins,
                "type_counts": type_counts,
                "colors": sorted(list(colors_seen)) if colors_seen else [],
                "issues": issues,
                "analysis_limited": not details_used,
            },
        )
        return summary

    def suggest_cards(self, deck: Deck, constraints: dict | None = None) -> list[dict[str, Any]]:
        """Suggest cards based on deck metadata/theme, constraints, synergy/weakness analysis, and combo detection.

        Uses RAG when available; falls back to empty list.

        Args:
            deck: The current deck entity
            constraints: Dict of constraints (theme, budget, power, banned, combo_mode, etc.)
                - combo_mode: "focused" or "broad" (default: "focused")
                - combo_limit: max combos per suggestion (default: 3)
                - combo_types: list of combo types to include (e.g., ["infinite_mana", "engine"])
                - exclude_cards: list of card names to exclude from combos
                - sort_by: "power", "price", "popularity", "complexity" (default: "power")
                - explain_combos: if True, add LLM explanations for combos (default: False)

        Returns:
            List of suggested card dicts with name, score, reason, synergy/weakness info, and combos.

        """
        constraints = constraints or {}
        theme = constraints.get("theme") or (deck.metadata.get("theme") if deck.metadata else None)
        budget = constraints.get("budget")
        power = constraints.get("power")
        banned = set(constraints.get("banned", []))
        n_results = constraints.get("n_results", 10)
        combo_mode = constraints.get("combo_mode", "focused")  # "focused" or "broad"
        combo_limit = constraints.get("combo_limit", 3)
        combo_types_filter = constraints.get("combo_types")  # e.g., ["infinite_mana", "engine"]
        exclude_cards = set(constraints.get("exclude_cards", []))
        sort_by = constraints.get("sort_by", "power")  # "power", "price", "popularity", "complexity"
        explain_combos = constraints.get("explain_combos", False)
        suggestions: list[dict[str, Any]] = []

        from mtg_card_app.core.manager_registry import ManagerRegistry

        registry = ManagerRegistry.get_instance()
        rag = getattr(registry, "rag_manager", None)
        card_data = getattr(registry, "card_data_manager", None)
        interactor = getattr(registry, "interactor", None)
        if not rag or not card_data or not interactor:
            return suggestions

        # Build a more detailed query
        query_parts = ["MTG cards"]
        if theme:
            query_parts.append(f"for {theme} strategy")
        if deck.format:
            query_parts.append(f"({deck.format})")
        if power:
            query_parts.append(f"power level {power}")
        if budget:
            query_parts.append(f"under ${budget}")
        query = " ".join(query_parts)

        # Get cache instance
        cache = get_suggestion_cache()

        # Check cache for RAG results
        cached_rag = cache.get_rag_results(query, n_results)
        if cached_rag:
            results = cached_rag
            logging.info("Using cached RAG results")
        else:
            try:
                results = rag.search_similar(query=query, n_results=n_results)
                # Cache the results
                cache.cache_rag_results(query, n_results, results)
            except Exception:
                logging.exception("RAG search_similar failed")
                return suggestions

        deck_colors = set(deck.metadata.get("colors", [])) if deck.metadata else set()

        # Gather all candidate cards (deck, commander, suggestions)
        candidate_names = set(deck.cards)
        if deck.commander:
            candidate_names.add(deck.commander)
        # We'll collect suggested cards after loop for cross-combo detection
        suggestion_objs = []

        # First pass: build suggestion objects without combos
        for cid, score, _meta in results:
            card = card_data.get_card_by_id(cid, fetch_if_missing=False)
            if not card or card.name in candidate_names or card.name in banned:
                continue

            synergy_score = 0
            weakness_flags = []
            card_colors = set(card.color_identity or card.colors or [])
            if deck_colors and card_colors and deck_colors & card_colors:
                synergy_score += 1
            if theme and theme.lower() not in (card.oracle_text or "").lower():
                weakness_flags.append("May not fit theme")
            if budget and hasattr(card, "usd") and card.usd:
                try:
                    if float(card.usd) > float(budget):
                        weakness_flags.append(f"Price ${card.usd} exceeds budget")
                except (ValueError, TypeError) as exc:
                    logging.warning(f"Could not parse card price for {card.name}: {exc}")

            suggestion_objs.append(
                {
                    "card": card,
                    "score": round(score, 3),
                    "synergy": synergy_score,
                    "weaknesses": weakness_flags,
                    "reason": f"Matches theme '{theme}'" if theme else "Relevant to deck",
                },
            )

        # Add suggested card names to candidates for cross-combo detection
        candidate_names.update(obj["card"].name for obj in suggestion_objs)

        # Second pass: robust combo detection for each suggestion
        for obj in suggestion_objs:
            card = obj["card"]
            combos_found = []
            # Check combos with every candidate card (deck, commander, suggestions)
            for other_name in candidate_names:
                if other_name == card.name or other_name in exclude_cards:
                    continue
                other_card = card_data.get_card(other_name)
                if not other_card or not hasattr(other_card, "id") or not hasattr(card, "id"):
                    continue
                # Find combos containing both cards
                combos = []
                try:
                    # Search for combos with both card IDs, plus filter by theme, format, colors, budget, etc.
                    combo_query = {"card_ids": [card.id, other_card.id]}
                    if theme:
                        combo_query["tags"] = [theme]
                    if deck.format:
                        combo_query["legal_formats"] = [deck.format]
                    if budget:
                        combo_query["max_price"] = float(budget)
                    if deck_colors:
                        combo_query["colors"] = list(deck_colors)
                    if combo_types_filter:
                        combo_query["combo_types"] = combo_types_filter

                    # Check cache for combo results
                    card_pair = (card.name, other_card.name)
                    cached_combos = cache.get_combo_results(card_pair)
                    if cached_combos:
                        combos = cached_combos
                    else:
                        combos = interactor.db_manager.combo_service.search(combo_query)
                        # Cache the results
                        cache.cache_combo_results(card_pair, combos)
                except Exception as exc:
                    logging.warning(f"Combo search failed for {card.name} + {other_card.name}: {exc}")

                # Filter out combos with excluded cards
                for combo in combos:
                    if not any(name in exclude_cards for name in combo.card_names):
                        combos_found.append(combo)

            # Remove duplicates by combo ID
            unique_combos = {}
            for combo in combos_found:
                if hasattr(combo, "id"):
                    unique_combos[combo.id] = combo
            combos_found = list(unique_combos.values())

            # Advanced ranking: calculate score for each combo
            for combo in combos_found:
                score = 0.0

                # Factor 1: Archetype fit (theme match)
                if theme and any(theme.lower() in tag.lower() for tag in combo.tags):
                    score += 10

                # Factor 2: Commander synergy
                if deck.commander and deck.commander in combo.card_names:
                    score += 15

                # Factor 3: Color identity overlap
                combo_colors = set(combo.colors_required)
                if deck_colors:
                    overlap = len(deck_colors & combo_colors)
                    score += overlap * 5

                # Factor 4: Budget fit
                if budget and combo.total_price_usd:
                    if combo.total_price_usd <= budget:
                        score += 10
                    else:
                        score -= (combo.total_price_usd - budget) / 10

                # Factor 5: Power level fit
                if power and combo.competitive_viability:
                    viability_scores = {"casual": 1, "fringe": 2, "tier2": 3, "tier1": 4}
                    combo_power = viability_scores.get(combo.competitive_viability, 0)
                    if abs(combo_power - power) <= 1:
                        score += 8

                # Factor 6: Complexity penalty (simpler combos are better)
                if combo.complexity == "low":
                    score += 5
                elif combo.complexity == "high":
                    score -= 3

                # Factor 7: Ease of assembly (fewer cards = easier)
                if combo.card_count <= 2:
                    score += 8
                elif combo.card_count <= 3:
                    score += 4
                else:
                    score -= combo.card_count

                # Factor 8: Disruptibility penalty (if documented)
                if combo.weaknesses:
                    score -= len(combo.weaknesses) * 2

                # Factor 9: Infinite combo boost
                if combo.is_infinite():
                    score += 12

                # Factor 10: Popularity boost
                if combo.popularity_score:
                    score += combo.popularity_score * 5

                # Store calculated score for sorting
                combo._ranking_score = score

            # Sort by the method specified in constraints
            def combo_sort_key(combo):
                if sort_by == "power":
                    return -getattr(combo, "_ranking_score", 0)
                if sort_by == "price":
                    return combo.total_price_usd or float("inf")
                if sort_by == "popularity":
                    return -(combo.popularity_score or 0)
                if sort_by == "complexity":
                    complexity_order = {"low": 0, "medium": 1, "high": 2}
                    return complexity_order.get(combo.complexity, 1)
                return -getattr(combo, "_ranking_score", 0)

            combos_found.sort(key=combo_sort_key)
            if combo_mode == "focused":
                combos_found = combos_found[:combo_limit]

            # Generate LLM explanations for combos if requested
            combo_dicts = []
            for combo in combos_found:
                combo_dict = combo.to_dict()
                if explain_combos:
                    try:
                        llm_manager = getattr(registry, "llm_manager", None)
                        if llm_manager:
                            explain_prompt = f"""Explain why this combo works well in a {deck.format} deck:

Combo: {combo.name}
Cards: {", ".join(combo.card_names)}
Type: {", ".join([ct.value for ct in combo.combo_types])}
Deck Theme: {theme or "General"}
Commander: {deck.commander or "None"}

Provide a brief (2-3 sentences) explanation of:
1. How this combo synergizes with the deck
2. What makes it powerful or fun
3. When to use it in gameplay"""
                            explanation = llm_manager.generate(explain_prompt)
                            combo_dict["llm_explanation"] = explanation
                    except Exception:
                        pass  # Silent fail for explanations
                combo_dicts.append(combo_dict)

            suggestions.append(
                {
                    "name": card.name,
                    "score": obj["score"],
                    "synergy": obj["synergy"],
                    "weaknesses": obj["weaknesses"],
                    "reason": obj["reason"],
                    "combos": combo_dicts,
                },
            )

        # Sort by synergy, score, combo count
        suggestions.sort(key=lambda s: (-(s["synergy"] or 0), -s["score"], -len(s["combos"])))

        return suggestions

    def export_deck(self, deck: Deck, format: str = "text") -> str:
        """Export a deck to various formats.

        Args:
            deck: Deck entity to export
            format: Export format:
                - "text": Plain text list with sections
                - "json": JSON format
                - "moxfield": Moxfield import format
                - "mtgo": Magic Online format
                - "arena": MTG Arena format
                - "archidekt": Archidekt import format

        Returns:
            Formatted deck string

        Raises:
            ValueError: If format is unsupported

        """
        format_lower = format.lower()

        if format_lower == "text":
            return self._export_text(deck)
        if format_lower == "json":
            return self._export_json(deck)
        if format_lower == "moxfield":
            return self._export_moxfield(deck)
        if format_lower == "mtgo":
            return self._export_mtgo(deck)
        if format_lower == "arena":
            return self._export_arena(deck)
        if format_lower == "archidekt":
            return self._export_archidekt(deck)

        msg = f"Unsupported export format: {format}"
        raise ValueError(msg)

    def _export_text(self, deck: Deck) -> str:
        """Export deck as plain text with sections."""
        lines = []

        # Header
        lines.append(f"# {deck.metadata.get('name', 'Untitled Deck')}")
        lines.append(f"# Format: {deck.format}")
        if deck.commander:
            lines.append(f"# Commander: {deck.commander}")
        if "theme" in deck.metadata:
            lines.append(f"# Theme: {deck.metadata['theme']}")
        lines.append("")

        # Commander section (if applicable)
        if deck.commander:
            lines.append("## Commander")
            lines.append(f"1 {deck.commander}")
            lines.append("")

        # Sections (if provided)
        if deck.sections:
            for section_name, cards in deck.sections.items():
                lines.append(f"## {section_name}")
                for card in sorted(cards):
                    lines.append(f"1 {card}")
                lines.append("")
        else:
            # No sections, just list all cards
            lines.append("## Main Deck")
            for card in sorted(deck.cards):
                if card != deck.commander:  # Don't duplicate commander
                    lines.append(f"1 {card}")

        return "\n".join(lines)

    def _export_json(self, deck: Deck) -> str:
        """Export deck as JSON."""
        import json

        return json.dumps(deck.to_dict(), indent=2, sort_keys=True)

    def _export_moxfield(self, deck: Deck) -> str:
        """Export deck in Moxfield import format.

        Format: quantity cardname
        Sections separated by blank lines with headers.
        """
        lines = []

        # Commander (if applicable)
        if deck.commander:
            lines.append("Commander")
            lines.append(f"1 {deck.commander}")
            lines.append("")

        # Sections or main deck
        if deck.sections:
            for section_name, cards in deck.sections.items():
                lines.append(section_name)
                for card in sorted(cards):
                    lines.append(f"1 {card}")
                lines.append("")
        else:
            lines.append("Main")
            for card in sorted(deck.cards):
                if card != deck.commander:
                    lines.append(f"1 {card}")

        return "\n".join(lines)

    def _export_mtgo(self, deck: Deck) -> str:
        """Export deck in MTGO format.

        Format: quantity cardname
        No section headers.
        """
        lines = []

        # All cards (including commander if present)
        all_cards = deck.cards.copy()
        if deck.commander and deck.commander not in all_cards:
            all_cards.append(deck.commander)

        for card in sorted(all_cards):
            lines.append(f"1 {card}")

        return "\n".join(lines)

    def _export_arena(self, deck: Deck) -> str:
        """Export deck in MTG Arena format.

        Format: quantity cardname (SET) collector_number
        Falls back to just "quantity cardname" if card details unavailable.
        """
        lines = []

        # Try to get card details for set/number
        try:
            from mtg_card_app.core.manager_registry import ManagerRegistry

            registry = ManagerRegistry.get_instance()
            card_data = registry.card_data_manager
        except Exception:
            card_data = None

        all_cards = deck.cards.copy()
        if deck.commander and deck.commander not in all_cards:
            all_cards.append(deck.commander)

        for card_name in sorted(all_cards):
            if card_data:
                card = card_data.get_card(card_name)
                if card and hasattr(card, "set_code") and hasattr(card, "collector_number"):
                    # Format: 1 Card Name (SET) 123
                    lines.append(f"1 {card.name} ({card.set_code.upper()}) {card.collector_number}")
                    continue
            # Fallback: just name
            lines.append(f"1 {card_name}")

        return "\n".join(lines)

    def _export_archidekt(self, deck: Deck) -> str:
        """Export deck in Archidekt import format.

        Similar to Moxfield format with sections.
        """
        return self._export_moxfield(deck)  # Same format
