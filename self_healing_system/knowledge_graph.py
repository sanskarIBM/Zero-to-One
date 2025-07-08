from neo4j import GraphDatabase
from . import config

class KnowledgeGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Element) REQUIRE e.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Locator) REQUIRE l.value IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patch) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Failure) REQUIRE f.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:HealingAction) REQUIRE h.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Prompt) REQUIRE pr.id IS UNIQUE")

    def add_test_run(self, test_id, element_id, locator, result, healing=None, patch=None, failure_reason=None, prompt_id=None):
        with self.driver.session() as session:
            session.run("""
                MERGE (t:TestCase {id: $test_id})
                MERGE (e:Element {id: $element_id})
                MERGE (l:Locator {value: $locator})
                MERGE (tr:TestRun {id: randomUUID(), result: $result, timestamp: timestamp()})
                MERGE (t)-[:EXECUTED_IN]->(tr)
                MERGE (e)-[:LOCATED_BY]->(l)
                MERGE (l)-[:USED_IN]->(t)
                FOREACH (fail IN CASE WHEN $result = 'fail' THEN [1] ELSE [] END |
                    MERGE (f:Failure {id: randomUUID(), reason: $failure_reason, timestamp: timestamp()})
                    MERGE (tr)-[:FAILED_AT]->(f)
                    MERGE (f)-[:ON_ELEMENT]->(e)
                    FOREACH (h IN CASE WHEN $healing IS NULL THEN [] ELSE [$healing] END |
                        MERGE (ha:HealingAction {id: randomUUID(), type: h, timestamp: timestamp()})
                        MERGE (f)-[:HEALED_BY]->(ha)
                        FOREACH (p IN CASE WHEN $patch IS NULL THEN [] ELSE [$patch] END |
                            MERGE (pa:Patch {id: p})
                            MERGE (ha)-[:GENERATED_PATCH]->(pa)
                        )
                        FOREACH (pr IN CASE WHEN $prompt_id IS NULL THEN [] ELSE [$prompt_id] END |
                            MERGE (prm:Prompt {id: pr})
                            MERGE (ha)-[:TRIGGERED_BY]->(prm)
                        )
                    )
                )
            """, test_id=test_id, element_id=element_id, locator=locator, result=result, healing=healing, patch=patch, failure_reason=failure_reason, prompt_id=prompt_id)

    def get_healing_strategies(self, element_id):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:Failure)-[:ON_ELEMENT]->(e:Element {id: $element_id})
                MATCH (f)-[:HEALED_BY]->(h:HealingAction)
                WHERE h.type IS NOT NULL
                RETURN h.type AS healing_type, count(*) AS times_successful
                ORDER BY times_successful DESC
            """, element_id=element_id)
            return [record.data() for record in result]

    def add_auto_heal_feedback(self, test_id, element_id, locator, healing, result, patch="patch_auto", prompt_id="auto_prompt"):
        self.add_test_run(test_id, element_id, locator, result, healing, patch, None, prompt_id)
