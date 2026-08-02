"""
Enterprise Entity Normalizer for RAGLink.

This module maps user-mentioned entities to their
canonical names and entity types.

Unknown entities are ignored rather than being
incorrectly classified.

In production, this registry can be replaced with
entities dynamically loaded from the indexed
knowledge base.
"""

import re

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# ENTITY INFORMATION
# ============================================================

@dataclass(frozen=True)
class EntityInfo:
    """
    Canonical information about an entity.
    """

    canonical_name: str

    entity_type: str


# ============================================================
# ENTITY REGISTRY
# ============================================================

ENTITY_REGISTRY: Dict[str, EntityInfo] = {

    # --------------------------------------------------------
    # Projects
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
    # Company
    # --------------------------------------------------------

    "series tech": EntityInfo(
        canonical_name="Series Tech Limited",
        entity_type="company",
    ),

    "series tech limited": EntityInfo(
        canonical_name="Series Tech Limited",
        entity_type="company",
    ),

    # --------------------------------------------------------
    # Infrastructure
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
# NORMALIZE TEXT
# ============================================================

def _normalize_text(
    text: str,
) -> str:
    """
    Normalize text before lookup.

    Examples

    Project-Meridian
        ->
    project meridian

    AWS
        ->
    aws
    """

    text = text.lower()

    text = re.sub(
        r"[-_/]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# SINGLE ENTITY
# ============================================================

def normalise_entity(
    entity: str,
) -> Optional[EntityInfo]:
    """
    Normalize one entity.
    """

    if not isinstance(entity, str):

        return None

    entity = entity.strip()

    if not entity:

        return None

    key = _normalize_text(entity)

    return ENTITY_REGISTRY.get(key)


# ============================================================
# MULTIPLE ENTITIES
# ============================================================

def normalise_entities(
    entities: List[str],
) -> List[dict]:
    """
    Normalize multiple extracted entities.

    Returns

    [
        {
            "mention": "...",
            "canonical_name": "...",
            "entity_type": "...",
        }
    ]
    """

    if not entities:

        return []

    results = []

    seen = set()

    for entity in entities:

        info = normalise_entity(entity)

        if info is None:

            continue

        key = (

            info.canonical_name,

            info.entity_type,

        )

        if key in seen:

            continue

        seen.add(key)

        results.append(

            {

                "mention": entity,

                "canonical_name": info.canonical_name,

                "entity_type": info.entity_type,

            }

        )

    return results


# ============================================================
# REGISTER ENTITY
# ============================================================

def register_entity(
    alias: str,
    canonical_name: str,
    entity_type: str,
) -> None:
    """
    Register an entity at runtime.

    Useful when loading entities from the
    knowledge base during startup.
    """

    key = _normalize_text(alias)

    ENTITY_REGISTRY[key] = EntityInfo(

        canonical_name=canonical_name,

        entity_type=entity_type,

    )


# ============================================================
# ALL REGISTERED ENTITIES
# ============================================================

def get_registered_entities() -> Dict[str, EntityInfo]:
    """
    Return the entity registry.
    """

    return ENTITY_REGISTRY.copy()