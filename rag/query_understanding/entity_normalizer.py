"""
Entity normalisation for RAGLink.

This module converts user-mentioned entity names into
canonical entity names and domain types.

Examples:

    Meridian
        -> Project Meridian / project

    AWS
        -> AWS / infrastructure

    Azure
        -> Azure / infrastructure

Unknown entities are NOT assigned an arbitrary domain.

Important:
This registry is intentionally conservative.
It should eventually be populated dynamically from
the indexed knowledge base.
"""

from dataclasses import dataclass
from typing import Optional


# ============================================================
# ENTITY INFORMATION
# ============================================================

@dataclass(frozen=True)
class EntityInfo:
    """
    Canonical information about a known entity.
    """

    canonical_name: str
    entity_type: str


# ============================================================
# KNOWN ENTITY REGISTRY
# ============================================================

ENTITY_REGISTRY = {

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    "project meridian": EntityInfo(
        canonical_name="Project Meridian",
        entity_type="project",
    ),

    "meridian": EntityInfo(
        canonical_name="Project Meridian",
        entity_type="project",
    ),

    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    "series tech limited": EntityInfo(
        canonical_name="Series Tech Limited",
        entity_type="company",
    ),

    "series tech": EntityInfo(
        canonical_name="Series Tech Limited",
        entity_type="company",
    ),

    # --------------------------------------------------------
    # INFRASTRUCTURE
    # --------------------------------------------------------

    "aws": EntityInfo(
        canonical_name="AWS",
        entity_type="infrastructure",
    ),

    "amazon web services": EntityInfo(
        canonical_name="AWS",
        entity_type="infrastructure",
    ),

    "azure": EntityInfo(
        canonical_name="Azure",
        entity_type="infrastructure",
    ),

    "microsoft azure": EntityInfo(
        canonical_name="Azure",
        entity_type="infrastructure",
    ),
}


# ============================================================
# SINGLE ENTITY NORMALISATION
# ============================================================

def normalise_entity(
    entity: str,
) -> Optional[EntityInfo]:
    """
    Normalise a single entity mention.

    Args:
        entity:
            Entity mentioned by the user.

    Returns:
        EntityInfo if the entity is known.
        None if the entity is unknown.
    """

    if not entity:
        return None

    key = entity.strip().lower()

    return ENTITY_REGISTRY.get(key)


# ============================================================
# MULTIPLE ENTITY NORMALISATION
# ============================================================

def normalise_entities(
    entities: list[str],
) -> list[dict]:
    """
    Normalise multiple extracted entities.

    Unknown entities are ignored instead of being
    incorrectly assigned to a domain.

    Example:

        Input:
            ["Meridian", "AWS", "Azure"]

        Output:
            [
                {
                    "mention": "Meridian",
                    "canonical_name": "Project Meridian",
                    "entity_type": "project",
                },
                {
                    "mention": "AWS",
                    "canonical_name": "AWS",
                    "entity_type": "infrastructure",
                },
                {
                    "mention": "Azure",
                    "canonical_name": "Azure",
                    "entity_type": "infrastructure",
                },
            ]
    """

    normalised = []

    for entity in entities:

        if not entity:
            continue

        info = normalise_entity(
            entity
        )

        # Unknown entity:
        # Do not invent a domain.
        if info is None:
            continue

        normalised.append(
            {
                "mention": entity,
                "canonical_name": info.canonical_name,
                "entity_type": info.entity_type,
            }
        )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    seen = set()

    unique_entities = []

    for entity in normalised:

        key = (
            entity["canonical_name"],
            entity["entity_type"],
        )

        if key not in seen:

            seen.add(key)

            unique_entities.append(
                entity
            )

    return unique_entities