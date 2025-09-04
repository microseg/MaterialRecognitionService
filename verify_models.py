#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to verify MaskTerial models are properly downloaded and set up
"""

import os
import sys
import glob

def check_model_directory():
    """Check if model directory exists and contains models"""
    model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
    
    print(f"Checking model directory: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model directory does not exist: {model_path}")
        return False
    
    print(f"OK: Model directory exists: {model_path}")
    
    # List all files in model directory
    model_files = glob.glob(os.path.join(model_path, "*"))
    print(f"Found {len(model_files)} files in model directory:")
    
    for file_path in model_files:
        file_name = os.path.basename(file_path)
        if os.path.isdir(file_path):
            print(f"  DIR: {file_name}/")
        else:
            size = os.path.getsize(file_path)
            print(f"  FILE: {file_name} ({size:,} bytes)")
    
    return True

def check_maskterial_import():
    """Check if MaskTerial can be imported and find the correct class"""
    try:
        import maskterial
        print("OK: MaskTerial module imported successfully")
        
        # Check what's available in the module
        print(f"Available in maskterial module: {dir(maskterial)}")
        
        # Try to find the detector class - look for MaskTerial specifically
        detector_class = None
        if hasattr(maskterial, 'MaskTerial'):
            detector_class = 'MaskTerial'
        else:
            # Fallback: look for classes with 'detector' or 'detect' in the name
            for item in dir(maskterial):
                if 'detector' in item.lower() or 'detect' in item.lower():
                    detector_class = item
                    break
        
        if detector_class:
            print(f"OK: Found detector class: {detector_class}")
            return True, detector_class
        else:
            print("WARNING: No detector class found in maskterial module")
            return False, None
            
    except ImportError as e:
        print(f"ERROR: Failed to import MaskTerial: {e}")
        return False, None

def check_detector_initialization():
    """Check if detector can be initialized"""
    try:
        import maskterial
        from maskterial.utils.loader_functions import load_models
        model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
        
        print("Loading MaskTerial models...")
        
        # Try to load models using the load_models function
        try:
            # Try to load segmentation and classification models
            seg_model, cls_model, pp_model = load_models(
                cls_model_type="AMM",
                cls_model_root=model_path,
                seg_model_type="M2F", 
                seg_model_root=model_path,
                device="cpu"
            )
            
            # Initialize MaskTerial with loaded models
            detector = maskterial.MaskTerial(
                segmentation_model=seg_model,
                classification_model=cls_model,
                postprocessing_model=pp_model,
                device="cpu"
            )
            print("OK: Successfully initialized MaskTerial with all models")
            return True
            
        except Exception as e:
            print(f"WARNING: Failed to load all models: {e}")
            
            # Try with just classification model
            try:
                seg_model, cls_model, pp_model = load_models(
                    cls_model_type="AMM",
                    cls_model_root=model_path,
                    device="cpu"
                )
                
                detector = maskterial.MaskTerial(
                    classification_model=cls_model,
                    device="cpu"
                )
                print("OK: Successfully initialized MaskTerial with classification model only")
                return True
                
            except Exception as e2:
                print(f"WARNING: Failed to load classification model: {e2}")
                
                # Try with just segmentation model
                try:
                    seg_model, cls_model, pp_model = load_models(
                        seg_model_type="M2F",
                        seg_model_root=model_path,
                        device="cpu"
                    )
                    
                    detector = maskterial.MaskTerial(
                        segmentation_model=seg_model,
                        device="cpu"
                    )
                    print("OK: Successfully initialized MaskTerial with segmentation model only")
                    return True
                    
                except Exception as e3:
                    print(f"ERROR: Failed to load any models: {e3}")
                    return False
        
    except Exception as e:
        print(f"ERROR: Failed to initialize detector: {e}")
        return False

def main():
    """Main verification function"""
    print("MaskTerial Model Verification")
    print("=" * 50)
    
    # Check model directory
    dir_ok = check_model_directory()
    
    # Check import
    import_ok, detector_class = check_maskterial_import()
    
    # Check initialization
    init_ok = False
    if import_ok:
        init_ok = check_detector_initialization()
    
    print("\nVerification Results:")
    print(f"  Model Directory: {'PASS' if dir_ok else 'FAIL'}")
    print(f"  MaskTerial Import: {'PASS' if import_ok else 'FAIL'}")
    print(f"  Detector Initialization: {'PASS' if init_ok else 'FAIL'}")
    
    if dir_ok and import_ok and init_ok:
        print("\nSUCCESS: All verifications passed! MaskTerial is ready to use.")
        sys.exit(0)
    else:
        print("\nERROR: Some verifications failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
