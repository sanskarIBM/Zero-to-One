# --- AUTOMATED HEALING AND FEEDBACK ENDPOINT ---
import random

@app.route('/auto_heal_and_feedback', methods=['POST'])
def auto_heal_and_feedback():
    """
    Request JSON: {"element_id": str, "test_id": str, "locator": str}
    1. Get healing strategies for the element.
    2. Pick the top strategy (if any).
    3. Simulate applying healing and rerunning the test (random pass/fail for demo).
    4. Record the new test run with healing info.
    5. Return the healing used and new result.
    """
    data = request.json
    element_id = data['element_id']
    test_id = data['test_id']
    locator = data['locator']
    # 1. Get healing strategies
    with driver.session() as session:
        strategies = session.read_transaction(healing_strategies, element_id)
    if not strategies:
        return jsonify({"status": "no healing strategies found"}), 404
    healing = strategies[0]['healing_type']
    # 2. Simulate rerun (random pass/fail for demo)
    result = random.choice(["pass", "fail"])
    # 3. Record the new test run
    with driver.session() as session:
        session.write_transaction(
            add_test_run,
            test_id,
            element_id,
            locator,
            result,
            healing,
            "patch_auto",
            None,
            "auto_prompt"
        )
    return jsonify({
        "healing_used": healing,
        "rerun_result": result
    })

from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import datetime

# Neo4j connection
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "ibm@7802"))

app = Flask(__name__)

# --- SCHEMA CREATION (optional, for constraints) ---
def create_constraints():
    with driver.session() as session:
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Element) REQUIRE e.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Locator) REQUIRE l.value IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patch) REQUIRE p.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Failure) REQUIRE f.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:HealingAction) REQUIRE h.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Prompt) REQUIRE pr.id IS UNIQUE")

# --- POPULATE GRAPH ---
def add_test_run(tx, test_id, element_id, locator, result, healing=None, patch=None, failure_reason=None, prompt_id=None):
    # Create test run, element, locator, and optionally healing/failure/prompt
    tx.run("""
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

@app.route('/add_test_run', methods=['POST'])
def add_test_run_api():
    data = request.json
    with driver.session() as session:
        session.write_transaction(
            add_test_run,
            data['test_id'],
            data['element_id'],
            data['locator'],
            data['result'],
            data.get('healing'),
            data.get('patch'),
            data.get('failure_reason'),
            data.get('prompt_id')
        )
    return jsonify({"status": "ok"})

# --- QUERY: Suggest Best Locator for Element ---
def suggest_best_locator(tx, element_id):
    result = tx.run("""
        MATCH (e:Element {id: $element_id})-[:LOCATED_BY]->(l:Locator)
        OPTIONAL MATCH (l)-[:USED_IN]->(t:TestCase)-[:EXECUTED_IN]->(tr:TestRun)
        WITH l, count(tr) AS total, sum(CASE WHEN tr.result='pass' THEN 1 ELSE 0 END) AS passes
        RETURN l.value AS locator, passes, total, (toFloat(passes)/total) AS success_rate
        ORDER BY success_rate DESC, total DESC
        LIMIT 1
    """, element_id=element_id)
    return [record.data() for record in result]

@app.route('/suggest_locator/<element_id>')
def suggest_locator_api(element_id):
    with driver.session() as session:
        result = session.read_transaction(suggest_best_locator, element_id)
    return jsonify(result)

# --- QUERY: Healing Strategies for Element ---
def healing_strategies(tx, element_id):
    result = tx.run("""
        MATCH (f:Failure)-[:ON_ELEMENT]->(e:Element {id: $element_id})
        MATCH (f)-[:HEALED_BY]->(h:HealingAction)
        WHERE h.type IS NOT NULL
        RETURN h.type AS healing_type, count(*) AS times_successful
        ORDER BY times_successful DESC
    """, element_id=element_id)
    return [record.data() for record in result]

@app.route('/healing_strategies/<element_id>')
def healing_strategies_api(element_id):
    with driver.session() as session:
        result = session.read_transaction(healing_strategies, element_id)
    return jsonify(result)

# --- QUERY: Locator History for Element ---
def get_locator_history(tx, element_id):
    result = tx.run("""
        MATCH (e:Element {id: $element_id})-[:LOCATED_BY]->(l:Locator)-[:USED_IN]->(t:TestCase)-[:EXECUTED_IN]->(tr:TestRun)
        RETURN l.value AS locator, tr.result AS result, tr.timestamp AS ts
        ORDER BY ts DESC
    """, element_id=element_id)
    return [record.data() for record in result]

@app.route('/get_locator_history/<element_id>')
def get_locator_history_api(element_id):
    with driver.session() as session:
        history = session.read_transaction(get_locator_history, element_id)
    return jsonify(history)

# --- QUERY: Self-Healing Actions for Element ---
def get_successful_healings(tx, element_id):
    result = tx.run("""
        MATCH (e:Element {id: $element_id})<-[:ON_ELEMENT]-(f:Failure)-[:HEALED_BY]->(ha:HealingAction)-[:GENERATED_PATCH]->(p:Patch)
        RETURN ha.type AS healing_type, p.id AS patch_id, ha.timestamp AS healed_at
        ORDER BY ha.timestamp DESC
    """, element_id=element_id)
    return [record.data() for record in result]

@app.route('/get_healings/<element_id>')
def get_healings_api(element_id):
    with driver.session() as session:
        healings = session.read_transaction(get_successful_healings, element_id)
    return jsonify(healings)

# --- QUERY: Analytics for Element ---
def element_analytics(tx, element_id):
    result = tx.run("""
        MATCH (e:Element {id: $element_id})-[:LOCATED_BY]->(l:Locator)
        OPTIONAL MATCH (l)-[:USED_IN]->(t:TestCase)-[:EXECUTED_IN]->(tr:TestRun)
        WITH e, l, count(tr) AS total, sum(CASE WHEN tr.result='fail' THEN 1 ELSE 0 END) AS fails
        RETURN e.id AS element_id, count(l) AS locator_count, total AS total_runs, fails AS failures
    """, element_id=element_id)
    return [record.data() for record in result]

@app.route('/analytics/element/<element_id>')
def analytics_element_api(element_id):
    with driver.session() as session:
        result = session.read_transaction(element_analytics, element_id)
    return jsonify(result)

# --- MAIN ---
if __name__ == '__main__':
    create_constraints()
    app.run(debug=True)
