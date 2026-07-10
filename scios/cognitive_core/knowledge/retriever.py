from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4

from scios.cognitive_core.knowledge.base import KnowledgeBase
from scios.cognitive_core.knowledge.graph import KnowledgeGraph


@dataclass
class KnowledgeRetriever:
    """
    KnowledgeRetriever = Retrieves knowledge from base or graph stores.
    """

    retriever_id: UUID = field(default_factory=uuid4)
    base: KnowledgeBase = field(default_factory=KnowledgeBase)
    graph: KnowledgeGraph = field(default_factory=KnowledgeGraph)

    # =========================================================
    # Core API
    # =========================================================

    def search(self, keyword: str) -> Dict[str, Any]:
        """
        Search knowledge entries by keyword in base + graph.
        """
        results: Dict[str, Any] = {}

        # Search in KnowledgeBase
        for k, v in self.base.list_entries().items():
            if keyword.lower() in k.lower() or keyword.lower() in str(v).lower():
                results[k] = v

        # Search in KnowledgeGraph nodes
        for node_id, data in self.graph.all_nodes().items():
            if keyword.lower() in node_id.lower() or keyword.lower() in str(data).lower():
                results[node_id] = data

        return results

    def related_concepts(self, concept: str) -> List[str]:
        """
        Retrieve related concepts from KnowledgeGraph.
        """
        neighbors = self.graph.get_neighbors(concept)
        return [f"{concept} --{rel}--> {target}" for rel, target in neighbors]

    def category_lookup(self, category: str) -> Dict[str, Any]:
        """
        Retrieve knowledge entries by category from KnowledgeBase.
        """
        return self.base.search_by_category(category)

    # =========================================================
    # Utility
    # =========================================================

    def clear(self) -> None:
        """
        Clear retriever state (base + graph).
        """
        self.base.clear()
        self.graph.clear()
