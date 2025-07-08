import random

from .knowledge_graph import KnowledgeGraph
from .llm_integration import suggest_locator_with_llm
import os

class HealingEngine:
    def __init__(self):
        self.kg = KnowledgeGraph()

    def auto_heal_and_feedback(self, test_id, element_id, locator, element_context=None):
        strategies = self.kg.get_healing_strategies(element_id)
        if strategies:
            healing = strategies[0]['healing_type']
            result = random.choice(["pass", "fail"])
            self.kg.add_auto_heal_feedback(test_id, element_id, locator, healing, result)
            return {"healing_used": healing, "rerun_result": result, "source": "graph"}
        # If no strategies, use LLM to suggest a new locator
        if element_context is None:
            element_context = f"Element ID: {element_id}, Locator: {locator}"
        llm_locator = suggest_locator_with_llm(element_context)
        # Simulate using the LLM locator and rerun
        result = random.choice(["pass", "fail"])
        self.kg.add_auto_heal_feedback(test_id, element_id, llm_locator, "llm_suggested_locator", result)
        return {"healing_used": "llm_suggested_locator", "rerun_result": result, "llm_locator": llm_locator, "source": "llm"}
