#!/usr/bin/env python3
"""
Material Recognition Service - Test Application
Simple Flask app to test the CI/CD pipeline workflow
"""

from flask import Flask, jsonify
import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint - Hello World"""
    return jsonify({
        'message': 'Hello World from Material Recognition Service!',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': 'production',
        'instance_id': os.environ.get('INSTANCE_ID', 'unknown')
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'MaterialRecognitionService'
    })

@app.route('/test')
def test():
    """Test endpoint for deployment verification"""
    return jsonify({
        'test': 'success',
        'message': 'Deployment test successful!',
        'timestamp': datetime.datetime.now().isoformat(),
        'workflow': 'Local Development → GitHub → CI/CD Pipeline → Production EC2'
    })

@app.route('/info')
def info():
    """Service information endpoint"""
    return jsonify({
        'service_name': 'MaterialRecognitionService',
        'description': 'Test application for CI/CD pipeline workflow',
        'endpoints': [
            '/ - Hello World',
            '/health - Health check',
            '/test - Deployment test',
            '/info - Service information'
        ],
        'deployment_workflow': [
            '1. Local development on user EC2',
            '2. Push code to GitHub main branch',
            '3. GitHub Actions triggers AWS CodePipeline',
            '4. CodeBuild deploys to production EC2',
            '5. Service is live on production'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Material Recognition Service...")
    print(f"Environment: Production")
    print(f"Timestamp: {datetime.datetime.now()}")
    print("Service endpoints:")
    print("  - / : Hello World")
    print("  - /health : Health check")
    print("  - /test : Deployment test")
    print("  - /info : Service information")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
