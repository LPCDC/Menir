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
<<<<<<< HEAD
        entry = {'ts': '2025-10-27T15:41:00Z', 'action': 'ping', 'response': 'Menir alive'}
=======
        entry = {'ts': '2025-10-27T15:29:00Z', 'action': 'ping', 'response': 'Menir alive'}
>>>>>>> 1f1d182cd6f45c42741054cc75a8e0274b37976e
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        return jsonify({'response': 'Menir alive'})
    return jsonify({'response': 'I’m Eve. Say "eve" to wake me.'})
if __name__ == '__main__':
<<<<<<< HEAD
    app.run(port=5000)'
=======
    app.run(port=5000)
>>>>>>> 1f1d182cd6f45c42741054cc75a8e0274b37976e
