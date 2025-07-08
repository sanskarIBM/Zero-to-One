from flask import Flask, request, jsonify

from .healing_engine import HealingEngine
from .knowledge_graph import KnowledgeGraph

app = Flask(__name__)
kg = KnowledgeGraph()
engine = HealingEngine()

@app.route('/add_test_run', methods=['POST'])
def add_test_run_api():
    data = request.json
    kg.add_test_run(
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

@app.route('/auto_heal_and_feedback', methods=['POST'])
def auto_heal_and_feedback_api():
    data = request.json
    # Optionally pass element_context for LLM
    result = engine.auto_heal_and_feedback(
        data['test_id'],
        data['element_id'],
        data['locator'],
        data.get('element_context')
    )
    return jsonify(result)

@app.route('/healing_strategies/<element_id>')
def healing_strategies_api(element_id):
    return jsonify(kg.get_healing_strategies(element_id))

if __name__ == '__main__':
    kg.create_constraints()
    app.run(debug=True)
