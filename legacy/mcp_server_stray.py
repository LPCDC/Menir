from flask import Flask, request, jsonify
import json
import os
app = Flask(__name__)
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'operations.jsonl')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {'query': ''}
    q = data.get('query', '').lower()
    if 'eve' in q:
        entry = {'ts': '2025-10-27T15:50:00Z', 'action': 'ping', 'response': 'Menir alive'}
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        return jsonify({'response': 'Menir alive'})
    return jsonify({'response': 'I’m Eve. Say "eve" to wake me.'})
if __name__ == '__main__':
    app.run(port=5000)
