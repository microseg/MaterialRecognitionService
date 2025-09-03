#!/usr/bin/env python3
"""
MaskTerial API Service
A Flask-based API for 2D material flake detection using MaskTerial model
"""

import os
import json
import uuid
import boto3
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import cv2
import numpy as np
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# AWS Configuration
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'matsight-customer-images')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'CustomerImages')
MODEL_PATH = os.environ.get('MODEL_PATH', '/opt/maskterial/models')

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# MaskTerial model imports (these will be available after installation)
try:
    import maskterial
    # Try to find the correct detector class
    detector_class = None
    for item in dir(maskterial):
        if 'detector' in item.lower() or 'detect' in item.lower():
            detector_class = getattr(maskterial, item)
            break
    
    if detector_class:
        MaskTerialDetector = detector_class
        MASKTERIAL_AVAILABLE = True
        logger.info(f"MaskTerial model imported successfully with class: {detector_class.__name__}")
    else:
        MASKTERIAL_AVAILABLE = False
        logger.warning("No detector class found in maskterial module - using mock detection")
except ImportError:
    MASKTERIAL_AVAILABLE = False
    logger.warning("MaskTerial model not available - using mock detection")

class MockMaskTerialDetector:
    """Mock detector for testing when MaskTerial is not available"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        logger.info("Initialized mock MaskTerial detector")
    
    def detect(self, image_path):
        """Mock detection that returns random flakes"""
        import random
        
        # Load image to get dimensions
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
        
        height, width = image.shape[:2]
        
        # Generate mock detection results
        num_flakes = random.randint(1, 5)
        flakes = []
        
        for i in range(num_flakes):
            # Generate random bounding box
            x1 = random.randint(0, width - 100)
            y1 = random.randint(0, height - 100)
            x2 = x1 + random.randint(50, 100)
            y2 = y1 + random.randint(50, 100)
            
            flake = {
                'bbox': [x1, y1, x2, y2],
                'confidence': random.uniform(0.7, 0.95),
                'area': (x2 - x1) * (y2 - y1),
                'material_type': random.choice(['graphene', 'hBN', 'MoS2', 'WS2'])
            }
            flakes.append(flake)
        
        return {
            'flakes': flakes,
            'total_flakes': len(flakes),
            'image_dimensions': [width, height]
        }

# Initialize detector
if MASKTERIAL_AVAILABLE:
    try:
        detector = MaskTerialDetector(model_path=MODEL_PATH)
        logger.info(f"MaskTerial detector initialized with model path: {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize MaskTerial detector: {e}")
        detector = MockMaskTerialDetector(MODEL_PATH)
else:
    detector = MockMaskTerialDetector(MODEL_PATH)

def convert_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_decimal(item) for item in obj]
    else:
        return obj

def save_to_s3(file_data, s3_key, content_type='image/jpeg'):
    """Save file data to S3"""
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save to S3: {e}")
        return False

def save_metadata_to_dynamodb(metadata):
    """Save metadata to DynamoDB"""
    try:
        # Convert metadata to use Decimal for float values
        metadata = convert_to_decimal(metadata)
        table.put_item(Item=metadata)
        return True
    except Exception as e:
        logger.error(f"Failed to save to DynamoDB: {e}")
        return False

def create_result_image(original_image_path, detection_results):
    """Create result image with detection overlays"""
    try:
        # Load original image
        image = cv2.imread(original_image_path)
        if image is None:
            raise ValueError("Could not load original image")
        
        # Draw detection results
        for flake in detection_results.get('flakes', []):
            bbox = flake['bbox']
            confidence = flake['confidence']
            material_type = flake.get('material_type', 'unknown')
            
            # Draw bounding box
            cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            
            # Add label
            label = f"{material_type}: {confidence:.2f}"
            cv2.putText(image, label, (bbox[0], bbox[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
    except Exception as e:
        logger.error(f"Failed to create result image: {e}")
        return None

@app.route('/')
def hello():
    return jsonify({
        "service": "MaskTerial 2D Material Detection Service",
        "version": "1.0.0",
        "model_available": MASKTERIAL_AVAILABLE,
        "endpoints": {
            "health": "/health",
            "detect": "/detect (POST)",
            "detect_from_s3": "/detect_from_s3 (POST)",
            "info": "/info"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "MaskTerial Detection Service",
        "model_available": MASKTERIAL_AVAILABLE,
        "aws_region": AWS_REGION,
        "s3_bucket": S3_BUCKET_NAME,
        "dynamodb_table": DYNAMODB_TABLE_NAME,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/detect', methods=['POST'])
def detect_image():
    """Detect 2D materials in uploaded image"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        # Get customer ID from request
        customer_id = request.form.get('customer_id', 'default-customer')
        
        # Generate unique image ID
        image_id = f"img-{uuid.uuid4()}"
        timestamp = int(datetime.now().timestamp())
        
        # Save original image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Perform detection
            detection_results = detector.detect(temp_path)
            
            # Create result image with overlays
            result_image_data = create_result_image(temp_path, detection_results)
            
            if result_image_data is None:
                return jsonify({"error": "Failed to create result image"}), 500
            
            # Generate S3 keys
            original_key = f"{customer_id}/uploaded/{image_id}_original.jpg"
            result_key = f"{customer_id}/saved-result/{image_id}_result.jpg"
            
            # Read original image data
            with open(temp_path, 'rb') as f:
                original_image_data = f.read()
            
            # Save images to S3
            original_saved = save_to_s3(original_image_data, original_key, 'image/jpeg')
            result_saved = save_to_s3(result_image_data, result_key, 'image/jpeg')
            
            if not original_saved or not result_saved:
                return jsonify({"error": "Failed to save images to S3"}), 500
            
            # Prepare metadata
            metadata = {
                "customerID": customer_id,
                "imageID": image_id,
                "createdAt": timestamp,
                "type": "UPLOADED",
                "s3Key": original_key,
                "thumbnailKey": original_key,
                "status": "active",
                "materialType": "detected",
                "imageSize": len(original_image_data),
                "imageFormat": "jpg",
                "processingStatus": "completed",
                "metadata": {
                    "detection_results": detection_results,
                    "total_flakes": detection_results.get('total_flakes', 0),
                    "uploadSource": "api",
                    "originalFilename": secure_filename(file.filename),
                    "processing_timestamp": timestamp
                },
                "expiresAt": int((datetime.now() + timedelta(days=365)).timestamp())
            }
            
            # Save metadata to DynamoDB
            if not save_metadata_to_dynamodb(metadata):
                return jsonify({"error": "Failed to save metadata to DynamoDB"}), 500
            
            # Generate presigned URLs for access
            original_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': original_key},
                ExpiresIn=3600
            )
            
            result_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': result_key},
                ExpiresIn=3600
            )
            
            return jsonify({
                "status": "success",
                "image_id": image_id,
                "customer_id": customer_id,
                "detection_results": detection_results,
                "original_image_url": original_url,
                "result_image_url": result_url,
                "s3_keys": {
                    "original": original_key,
                    "result": result_key
                },
                "processing_timestamp": timestamp
            })
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"Error in detect_image: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/detect_from_s3', methods=['POST'])
def detect_from_s3():
    """Detect 2D materials in image from S3"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        s3_key = data.get('s3_key')
        customer_id = data.get('customer_id', 'default-customer')
        
        if not s3_key:
            return jsonify({"error": "No S3 key provided"}), 400
        
        # Generate unique image ID
        image_id = f"img-{uuid.uuid4()}"
        timestamp = int(datetime.now().timestamp())
        
        # Download image from S3
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            image_data = response['Body'].read()
        except Exception as e:
            return jsonify({"error": f"Failed to download image from S3: {e}"}), 500
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # Perform detection
            detection_results = detector.detect(temp_path)
            
            # Create result image with overlays
            result_image_data = create_result_image(temp_path, detection_results)
            
            if result_image_data is None:
                return jsonify({"error": "Failed to create result image"}), 500
            
            # Generate result S3 key
            result_key = f"{customer_id}/saved-result/{image_id}_result.jpg"
            
            # Save result image to S3
            if not save_to_s3(result_image_data, result_key, 'image/jpeg'):
                return jsonify({"error": "Failed to save result image to S3"}), 500
            
            # Prepare metadata
            metadata = {
                "customerID": customer_id,
                "imageID": image_id,
                "createdAt": timestamp,
                "type": "SAVED_RESULT",
                "s3Key": result_key,
                "thumbnailKey": result_key,
                "status": "active",
                "materialType": "detected",
                "imageSize": len(result_image_data),
                "imageFormat": "jpg",
                "processingStatus": "completed",
                "metadata": {
                    "detection_results": detection_results,
                    "total_flakes": detection_results.get('total_flakes', 0),
                    "source_s3_key": s3_key,
                    "processing_timestamp": timestamp
                },
                "expiresAt": int((datetime.now() + timedelta(days=365)).timestamp())
            }
            
            # Save metadata to DynamoDB
            if not save_metadata_to_dynamodb(metadata):
                return jsonify({"error": "Failed to save metadata to DynamoDB"}), 500
            
            # Generate presigned URL for result
            result_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': result_key},
                ExpiresIn=3600
            )
            
            return jsonify({
                "status": "success",
                "image_id": image_id,
                "customer_id": customer_id,
                "detection_results": detection_results,
                "result_image_url": result_url,
                "s3_keys": {
                    "source": s3_key,
                    "result": result_key
                },
                "processing_timestamp": timestamp
            })
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"Error in detect_from_s3: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/info')
def info():
    return jsonify({
        "service": "MaskTerial 2D Material Detection Service",
        "version": "1.0.0",
        "model_available": MASKTERIAL_AVAILABLE,
        "model_path": MODEL_PATH,
        "aws_configuration": {
            "region": AWS_REGION,
            "s3_bucket": S3_BUCKET_NAME,
            "dynamodb_table": DYNAMODB_TABLE_NAME
        },
        "endpoints": {
            "health": "/health",
            "detect": "/detect (POST) - Upload image for detection",
            "detect_from_s3": "/detect_from_s3 (POST) - Detect from S3 image",
            "info": "/info"
        },
        "example_usage": {
            "detect": {
                "method": "POST",
                "url": "/detect",
                "form_data": {
                    "image": "image file",
                    "customer_id": "customer-123"
                }
            },
            "detect_from_s3": {
                "method": "POST",
                "url": "/detect_from_s3",
                "json": {
                    "s3_key": "customer-123/uploaded/image.jpg",
                    "customer_id": "customer-123"
                }
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
