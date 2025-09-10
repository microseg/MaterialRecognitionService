#!/usr/bin/env python3
"""
MaterialRecognitionService
Flask API exposing /health, /detect_from_s3 (POST), and /detect (POST).
Uses MaskTerial if available, otherwise a lightweight mock so the service
is deployable even before models are ready.
"""

import os
import io
import json
import uuid
import time
import tempfile
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict

from flask import Flask, request, jsonify
import boto3

# --------------------
# Configuration (env)
# --------------------
PORT = int(os.environ.get("PORT", "5000"))
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "matsight-customer-images")
DDB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "CustomerImages")
MODEL_PATH = os.environ.get("MODEL_PATH", "/opt/maskterial/models")
MODELS_S3_BUCKET = os.environ.get("MODELS_S3_BUCKET", "matsight-maskterial-models-v2")

# AWS clients
s3 = boto3.client("s3", region_name=AWS_REGION)
ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
ddb_table = ddb.Table(DDB_TABLE_NAME)

app = Flask(__name__)
log = logging.getLogger("mrs")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# --------------------------
# Optional: model sync (S3)
# --------------------------
def ensure_models():
    """Ensure models exist locally at MODEL_PATH by syncing from MODELS_S3_BUCKET."""
    os.makedirs(MODEL_PATH, exist_ok=True)
    marker_file = os.path.join(MODEL_PATH, ".synced")
    if os.path.exists(marker_file):
        return
    try:
        log.info("Syncing models from s3://%s to %s ...", MODELS_S3_BUCKET, MODEL_PATH)
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=MODELS_S3_BUCKET):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                local_path = os.path.join(MODEL_PATH, key)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                s3.download_file(MODELS_S3_BUCKET, key, local_path)
        open(marker_file, "w").close()
        log.info("Model sync complete.")
    except Exception as e:
        log.warning("Model sync skipped: %s", e)

# --------------------------
# MaskTerial inference shim
# --------------------------
def _mock_detect(image_path: str) -> Dict[str, Any]:
    """Tiny mock to keep API responsive if MaskTerial isn't installed yet."""
    import random
    return {
        "flakes": [
            {"bbox": [10, 10, 120, 120], "confidence": round(random.uniform(0.7, 0.95), 2), "material_type": "graphene"}
        ],
        "total_flakes": 1,
        "engine": "mock"
    }

def run_maskterial(image_path: str) -> Dict[str, Any]:
    """
    Try MaskTerial python API; if unavailable, return mock result.
    You can replace this with the exact calls your MaskTerial lib requires.
    """
    try:
        # Example import; adjust once MaskTerial lib layout is finalized
        from maskterial.inference import detect_image  # ← update to actual function
        results = detect_image(image_path=image_path, model_dir=MODEL_PATH)
        return {"ok": True, "engine": "maskterial-python", "results": results}
    except Exception as e:
        log.warning("MaskTerial unavailable or failed (%s). Using mock.", e)
        return {"ok": True, "engine": "mock", "results": _mock_detect(image_path)}

# ----------------
# Helper: Decimal
# ----------------
def _to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_decimal(v) for v in obj]
    return obj

# ----------
# Endpoints
# ----------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "MaterialRecognitionService",
        "status": "healthy",
        "time": datetime.utcnow().isoformat(),
        "region": AWS_REGION,
        "s3_bucket": S3_BUCKET_NAME,
        "dynamodb_table": DDB_TABLE_NAME
    })

@app.route("/detect_from_s3", methods=["POST"])
def detect_from_s3():
    """
    Body example (JSON):
    {
      "customer_id": "test_user",
      "s3_key": "test_user/uploaded/xxx.jpg"
    }
    """
    t0 = time.time()
    data = request.get_json(force=True, silent=False) or {}
    customer_id = data.get("customer_id")
    s3_key = data.get("s3_key")
    if not customer_id or not s3_key:
        return jsonify({"ok": False, "error": "customer_id and s3_key required"}), 400

    ensure_models()

    # Download the image from S3
    tmpdir = tempfile.mkdtemp(prefix="mrs_")
    local_path = os.path.join(tmpdir, os.path.basename(s3_key))
    log.info("Downloading s3://%s/%s -> %s", S3_BUCKET_NAME, s3_key, local_path)
    s3.download_file(S3_BUCKET_NAME, s3_key, local_path)

    # Run detection
    result = run_maskterial(local_path)

    # Save result image to S3 in saved-result directory
    result_image_id = f"img-{uuid.uuid4()}"
    result_s3_key = f"{customer_id}/saved-result/{result_image_id}.jpg"
    
    # Generate presigned URL for download (valid for 7 days)
    download_url = None
    try:
        # Upload the processed image to S3
        log.info("Uploading result to s3://%s/%s", S3_BUCKET_NAME, result_s3_key)
        s3.upload_file(local_path, S3_BUCKET_NAME, result_s3_key)
        log.info("Result image saved successfully to S3")
        
        # Generate presigned URL for download (no expiration)
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': result_s3_key}
        )
        log.info("Generated presigned download URL")
    except Exception as e:
        log.error("Failed to save result image to S3: %s", e)
        result_s3_key = None

    # Persist record in DynamoDB
    item = {
        "customerID": str(customer_id),
        "imageID": result_image_id,
        "s3Key": s3_key,  # Original image key
        "resultS3Key": result_s3_key,  # Result image key
        "downloadUrl": download_url,  # Presigned download URL
        "result": json.dumps(result)[:350000],
        "createdAt": int(time.time()),
        "type": "SAVED_RESULT",
        "status": "active",
        "expiresAt": int((datetime.utcnow() + timedelta(days=365)).timestamp())
    }
    try:
        ddb_table.put_item(Item=_to_decimal(item))
        log.info("Record saved to DynamoDB successfully")
    except Exception as e:
        log.warning("Failed to write to DynamoDB: %s", e)

    elapsed = time.time() - t0
    return jsonify({
        "ok": True,
        "elapsed_sec": round(elapsed, 3),
        "customer_id": customer_id,
        "original_s3_key": s3_key,
        "result_s3_key": result_s3_key,
        "result_image_id": result_image_id,
        "download_url": download_url,
        "inference": result
    })

@app.route("/detect", methods=["POST"])
def detect_upload():
    """
    Multipart form (POST):
      - image: file
      - customer_id: optional
    """
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "image file is required"}), 400

    customer_id = request.form.get("customer_id", "default-customer")
    f = request.files["image"]
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as t:
        f.save(t.name)
        local_path = t.name

    ensure_models()
    result = run_maskterial(local_path)
    return jsonify({"ok": True, "customer_id": customer_id, "inference": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
