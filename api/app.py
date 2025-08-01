from flask import Flask, jsonify
import psycopg2
import redis
import os
import time
import random

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'api'})

@app.route('/api/data')
def get_data():
    try:
        # Simulate database call
        time.sleep(random.uniform(0.1, 0.3))
        return jsonify({'data': 'sample data', 'timestamp': time.time()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)