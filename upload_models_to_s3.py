#!/usr/bin/env python3
"""
Script to upload MaskTerial models to S3
This script downloads models from Zenodo and uploads them to S3
"""

import os
import boto3
import requests
import zipfile
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
S3_BUCKET_NAME = os.environ.get('MODELS_S3_BUCKET', 'matsight-maskterial-models-v2')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

# Model URLs from Zenodo
MODEL_URLS = {
    'SEG_M2F_GrapheneH': 'https://zenodo.org/records/15765516/files/SEG_M2F_GrapheneH.zip?download=1',
    'SEG_M2F_GrapheneL': 'https://zenodo.org/records/15765516/files/SEG_M2F_GrapheneL.zip?download=1',
    'SEG_M2F_hBN_Thin': 'https://zenodo.org/records/15765516/files/SEG_M2F_hBN_Thin.zip?download=1',
    'SEG_M2F_WS2': 'https://zenodo.org/records/15765516/files/SEG_M2F_WS2.zip?download=1',
    'CLS_AMM_GrapheneH': 'https://zenodo.org/records/15765516/files/CLS_AMM_GrapheneH.zip?download=1',
    'CLS_AMM_GrapheneL': 'https://zenodo.org/records/15765516/files/CLS_AMM_GrapheneL.zip?download=1',
    'CLS_AMM_hBN_Thin': 'https://zenodo.org/records/15765516/files/CLS_AMM_hBN_Thin.zip?download=1',
    'CLS_AMM_WS2': 'https://zenodo.org/records/15765516/files/CLS_AMM_WS2.zip?download=1',
}

def download_and_extract_model(model_name, url, temp_dir):
    """Download and extract a model from Zenodo"""
    logger.info(f"Downloading {model_name} from {url}")
    
    # Download the zip file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    zip_path = os.path.join(temp_dir, f"{model_name}.zip")
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Extract the zip file
    extract_dir = os.path.join(temp_dir, model_name)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    logger.info(f"Extracted {model_name} to {extract_dir}")
    return extract_dir

def upload_model_to_s3(s3_client, model_dir, model_name):
    """Upload model files to S3"""
    logger.info(f"Uploading {model_name} to S3")
    
    uploaded_files = []
    for root, dirs, files in os.walk(model_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, model_dir)
            s3_key = f"{model_name}/{relative_path}"
            
            # Upload file to S3
            with open(file_path, 'rb') as f:
                s3_client.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
            
            uploaded_files.append(s3_key)
            logger.info(f"Uploaded {s3_key}")
    
    return uploaded_files

def main():
    """Main function to download and upload all models"""
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"S3 bucket {S3_BUCKET_NAME} exists")
        except Exception as e:
            logger.error(f"S3 bucket {S3_BUCKET_NAME} does not exist or is not accessible: {e}")
            return False
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            total_uploaded = 0
            
            # Process each model
            for model_name, url in MODEL_URLS.items():
                try:
                    # Download and extract model
                    model_dir = download_and_extract_model(model_name, url, temp_dir)
                    
                    # Upload to S3
                    uploaded_files = upload_model_to_s3(s3_client, model_dir, model_name)
                    total_uploaded += len(uploaded_files)
                    
                    logger.info(f"Successfully processed {model_name}: {len(uploaded_files)} files")
                    
                except Exception as e:
                    logger.error(f"Failed to process {model_name}: {e}")
                    continue
            
            logger.info(f"Upload completed. Total files uploaded: {total_uploaded}")
            return True
            
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
