#!/usr/bin/env python3
"""
Script to verify MaskTerial models are properly downloaded and set up
"""

import os
import sys
import glob

def check_model_directory():
    """Check if model directory exists and contains models"""
    model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
    
    print(f"🔍 Checking model directory: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Model directory does not exist: {model_path}")
        return False
    
    print(f"✅ Model directory exists: {model_path}")
    
    # List all files in model directory
    model_files = glob.glob(os.path.join(model_path, "*"))
    print(f"\n📁 Found {len(model_files)} files in model directory:")
    
    for file_path in model_files:
        file_name = os.path.basename(file_path)
        if os.path.isdir(file_path):
            print(f"   📂 {file_name}/")
        else:
            size = os.path.getsize(file_path)
            print(f"   📄 {file_name} ({size:,} bytes)")
    
    return True

def check_maskterial_import():
    """Check if MaskTerial can be imported"""
    try:
        from maskterial import MaskTerialDetector
        print("✅ MaskTerial imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import MaskTerial: {e}")
        return False

def check_detector_initialization():
    """Check if detector can be initialized"""
    try:
        from maskterial import MaskTerialDetector
        model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
        
        print(f"🔧 Initializing MaskTerial detector with model path: {model_path}")
        detector = MaskTerialDetector(model_path=model_path)
        print("✅ MaskTerial detector initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize MaskTerial detector: {e}")
        return False

def main():
    """Main verification function"""
    print("🧪 MaskTerial Model Verification\n")
    
    # Check model directory
    dir_ok = check_model_directory()
    
    # Check import
    import_ok = check_maskterial_import()
    
    # Check initialization
    init_ok = False
    if import_ok:
        init_ok = check_detector_initialization()
    
    print(f"\n📊 Verification Results:")
    print(f"   Model Directory: {'✅ PASS' if dir_ok else '❌ FAIL'}")
    print(f"   MaskTerial Import: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"   Detector Initialization: {'✅ PASS' if init_ok else '❌ FAIL'}")
    
    if dir_ok and import_ok and init_ok:
        print("\n🎉 All verifications passed! MaskTerial is ready to use.")
        sys.exit(0)
    else:
        print("\n💥 Some verifications failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
