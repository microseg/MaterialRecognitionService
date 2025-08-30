#!/usr/bin/env python3
"""
Simple Calculator API Service
A Flask-based calculator API for testing CI/CD pipeline workflow
"""

from flask import Flask, jsonify, request
import datetime
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint - API information"""
    return jsonify({
        'message': 'Welcome to Simple Calculator API!',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.2',
        'environment': 'production',
        'instance_id': os.environ.get('INSTANCE_ID', 'unknown'),
        'endpoints': {
            '/': 'API information',
            '/health': 'Health check',
            '/calculate': 'Perform calculations (POST)',
            '/add/<a>/<b>': 'Add two numbers (GET)',
            '/subtract/<a>/<b>': 'Subtract two numbers (GET)',
            '/multiply/<a>/<b>': 'Multiply two numbers (GET)',
            '/divide/<a>/<b>': 'Divide two numbers (GET)'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'CalculatorAPI'
    })

@app.route('/calculate', methods=['POST'])
def calculate():
    """Perform calculations via POST request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        operation = data.get('operation')
        a = data.get('a')
        b = data.get('b')
        
        if operation is None or a is None or b is None:
            return jsonify({'error': 'Missing required fields: operation, a, b'}), 400
        
        try:
            a = float(a)
            b = float(b)
        except ValueError:
            return jsonify({'error': 'Invalid numbers provided'}), 400
        
        result = None
        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                return jsonify({'error': 'Division by zero'}), 400
            result = a / b
        else:
            return jsonify({'error': 'Invalid operation. Use: add, subtract, multiply, divide'}), 400
        
        return jsonify({
            'operation': operation,
            'a': a,
            'b': b,
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add/<a>/<b>')
def add(a, b):
    """Add two numbers via GET request"""
    try:
        result = float(a) + float(b)
        return jsonify({
            'operation': 'add',
            'a': float(a),
            'b': float(b),
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except ValueError:
        return jsonify({'error': 'Invalid numbers provided'}), 400

@app.route('/subtract/<a>/<b>')
def subtract(a, b):
    """Subtract two numbers via GET request"""
    try:
        result = float(a) - float(b)
        return jsonify({
            'operation': 'subtract',
            'a': float(a),
            'b': float(b),
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except ValueError:
        return jsonify({'error': 'Invalid numbers provided'}), 400

@app.route('/multiply/<a>/<b>')
def multiply(a, b):
    """Multiply two numbers via GET request"""
    try:
        result = float(a) * float(b)
        return jsonify({
            'operation': 'multiply',
            'a': float(a),
            'b': float(b),
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except ValueError:
        return jsonify({'error': 'Invalid numbers provided'}), 400

@app.route('/divide/<a>/<b>')
def divide(a, b):
    """Divide two numbers via GET request"""
    try:
        a_val = float(a)
        b_val = float(b)
        if b_val == 0:
            return jsonify({'error': 'Division by zero'}), 400
        result = a_val / b_val
        return jsonify({
            'operation': 'divide',
            'a': a_val,
            'b': b_val,
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except ValueError:
        return jsonify({'error': 'Invalid numbers provided'}), 400

@app.route('/test')
def test():
    """Test endpoint for deployment verification"""
    return jsonify({
        'test': 'success',
        'message': 'Calculator API is working!',
        'timestamp': datetime.datetime.now().isoformat(),
        'workflow': 'Local Development → GitHub → CI/CD Pipeline → Production EC2'
    })

if __name__ == '__main__':
    print("🧮 Starting Simple Calculator API...")
    print(f"Environment: Production")
    print(f"Timestamp: {datetime.datetime.now()}")
    print("API endpoints:")
    print("  - / : API information")
    print("  - /health : Health check")
    print("  - /calculate : POST calculations")
    print("  - /add/<a>/<b> : Add numbers")
    print("  - /subtract/<a>/<b> : Subtract numbers")
    print("  - /multiply/<a>/<b> : Multiply numbers")
    print("  - /divide/<a>/<b> : Divide numbers")
    print("  - /test : Deployment test")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
