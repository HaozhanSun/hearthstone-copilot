#!/usr/bin/env python3
"""
Analyze ground truth image to understand "点击开始" text detection
"""

import cv2
import numpy as np
import base64
import requests
import os
from datetime import datetime

def analyze_ground_truth():
    """Analyze the ground truth image to understand the text detection issue"""
    
    # Load the ground truth image
    ground_truth_path = "screenshots/ground_truth/click_to_start.png"
    if not os.path.exists(ground_truth_path):
        print(f"Ground truth image not found: {ground_truth_path}")
        return
    
    print(f"Loading ground truth image: {ground_truth_path}")
    image = cv2.imread(ground_truth_path)
    if image is None:
        print("Failed to load image")
        return
    
    print(f"Image size: {image.shape[1]}x{image.shape[0]}")
    print(f"Image type: {image.dtype}")
    
    # Test OCR on the ground truth image
    print("\n=== Testing OCR on Ground Truth Image ===")
    
    # Convert to base64
    _, buffer = cv2.imencode('.png', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Test with Chinese OCR
    print("Testing with Chinese OCR...")
    ocr_data = {
        "base64": image_base64,
        "options": {
            "ocr.language": "简体中文",
            "ocr.maxSideLen": 1024,
            "tbpu.parser": "multi_para",
            "data.format": "dict"
        }
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:1224/api/ocr",
            json=ocr_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 100:
                ocr_results = result.get('data', [])
                print(f"Chinese OCR found {len(ocr_results)} text blocks:")
                
                for i, block in enumerate(ocr_results):
                    text = block.get('text', '').strip()
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        print(f"  Block {i}: '{text}' at ({int(x1)}, {int(y1)}) size ({int(x2-x1)}x{int(y2-y1)})")
                        
                        # Check if this looks like "点击开始"
                        if "点击" in text or "开始" in text or "Click" in text or "Start" in text:
                            print(f"    *** POTENTIAL MATCH for '点击开始': '{text}' ***")
            else:
                print(f"Chinese OCR failed: {result.get('data', 'Unknown error')}")
        else:
            print(f"Chinese OCR request failed: {response.status_code}")
    except Exception as e:
        print(f"Chinese OCR error: {e}")
    
    # Test with English OCR
    print("\nTesting with English OCR...")
    ocr_data["options"]["ocr.language"] = "English"
    
    try:
        response = requests.post(
            "http://127.0.0.1:1224/api/ocr",
            json=ocr_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 100:
                ocr_results = result.get('data', [])
                print(f"English OCR found {len(ocr_results)} text blocks:")
                
                for i, block in enumerate(ocr_results):
                    text = block.get('text', '').strip()
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        print(f"  Block {i}: '{text}' at ({int(x1)}, {int(y1)}) size ({int(x2-x1)}x{int(y2-y1)})")
                        
                        # Check if this looks like "点击开始"
                        if "点击" in text or "开始" in text or "Click" in text or "Start" in text:
                            print(f"    *** POTENTIAL MATCH for '点击开始': '{text}' ***")
            else:
                print(f"English OCR failed: {result.get('data', 'Unknown error')}")
        else:
            print(f"English OCR request failed: {response.status_code}")
    except Exception as e:
        print(f"English OCR error: {e}")
    
    # Test with different preprocessing
    print("\n=== Testing with Image Preprocessing ===")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply different preprocessing techniques
    preprocessing_methods = [
        ("Original", image),
        ("Grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)),
        ("Gaussian Blur", cv2.cvtColor(cv2.GaussianBlur(gray, (3, 3), 0), cv2.COLOR_GRAY2BGR)),
        ("Adaptive Threshold", cv2.cvtColor(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2), cv2.COLOR_GRAY2BGR)),
        ("Morphological Close", cv2.cvtColor(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))), cv2.COLOR_GRAY2BGR)),
    ]
    
    for method_name, processed_image in preprocessing_methods:
        print(f"\nTesting {method_name} preprocessing...")
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', processed_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        ocr_data = {
            "base64": image_base64,
            "options": {
                "ocr.language": "简体中文",
                "ocr.maxSideLen": 1024,
                "tbpu.parser": "multi_para",
                "data.format": "dict"
            }
        }
        
        try:
            response = requests.post(
                "http://127.0.0.1:1224/api/ocr",
                json=ocr_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 100:
                    ocr_results = result.get('data', [])
                    print(f"  Found {len(ocr_results)} text blocks:")
                    
                    for i, block in enumerate(ocr_results):
                        text = block.get('text', '').strip()
                        if text:  # Only show non-empty text
                            print(f"    '{text}'")
                            
                            # Check if this looks like "点击开始"
                            if "点击" in text or "开始" in text or "Click" in text or "Start" in text:
                                print(f"      *** POTENTIAL MATCH for '点击开始': '{text}' ***")
                else:
                    print(f"  Failed: {result.get('data', 'Unknown error')}")
            else:
                print(f"  Request failed: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    analyze_ground_truth() 