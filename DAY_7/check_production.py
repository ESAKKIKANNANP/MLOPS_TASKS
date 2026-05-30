#!/usr/bin/env python3
"""
Deployment and Production Checklist
Run this script to verify production readiness
"""

import os
import sys
from pathlib import Path


class ProductionChecklist:
    """Production readiness verification"""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def check_files(self):
        """Verify all required files exist"""
        required_files = [
            'app.py',
            'config.py',
            'requirements.txt',
            '.env.example',
            'templates/login.html',
            'templates/detection.html',
            'static/js/app.js',
            'static/css/style.css',
            'README.md',
            'QUICK_START.md',
            'ARCHITECTURE.md',
        ]
        
        for file in required_files:
            if Path(file).exists():
                self.passed.append(f"✓ {file} exists")
            else:
                self.failed.append(f"✗ {file} missing")
    
    def check_directories(self):
        """Verify all required directories exist"""
        required_dirs = [
            'templates',
            'static',
            'static/css',
            'static/js',
            'logs',
            'train',
            'valid',
            'test',
        ]
        
        for directory in required_dirs:
            if Path(directory).exists():
                self.passed.append(f"✓ {directory}/ exists")
            else:
                self.failed.append(f"✗ {directory}/ missing")
    
    def check_environment(self):
        """Check environment setup"""
        # Check Python version
        if sys.version_info >= (3, 8):
            self.passed.append(f"✓ Python {sys.version.split()[0]} (3.8+ required)")
        else:
            self.failed.append(f"✗ Python {sys.version.split()[0]} (3.8+ required)")
        
        # Check Flask
        try:
            import flask
            self.passed.append(f"✓ Flask {flask.__version__} installed")
        except ImportError:
            self.failed.append("✗ Flask not installed")
        
        # Check OpenCV
        try:
            import cv2
            self.passed.append(f"✓ OpenCV {cv2.__version__} installed")
        except ImportError:
            self.failed.append("✗ OpenCV not installed")
        
        # Check YOLOv8
        try:
            from ultralytics import YOLO
            self.passed.append("✓ Ultralytics YOLOv8 installed")
        except ImportError:
            self.failed.append("✗ YOLOv8 not installed")
    
    def check_model(self):
        """Check for trained model"""
        model_path = Path('runs/detect/mall_yolov8/weights/best.pt')
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            self.passed.append(f"✓ Trained model found ({size_mb:.1f}MB)")
        else:
            self.warnings.append(
                "⚠ Trained model not found at "
                "runs/detect/mall_yolov8/weights/best.pt\n"
                "  System will use pretrained YOLOv8n model"
            )
    
    def check_permissions(self):
        """Check directory permissions"""
        try:
            test_file = Path('logs/.test')
            test_file.touch()
            test_file.unlink()
            self.passed.append("✓ Write permissions verified")
        except PermissionError:
            self.failed.append("✗ Insufficient write permissions")
    
    def check_security(self):
        """Check security settings"""
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                if 'SECRET_KEY' in env_content:
                    self.passed.append("✓ .env file configured")
                else:
                    self.warnings.append("⚠ .env file exists but SECRET_KEY not set")
        except FileNotFoundError:
            self.warnings.append("⚠ .env file not found (copy from .env.example)")
    
    def run_all_checks(self):
        """Run all checks"""
        print("\n" + "="*60)
        print("🔍 PRODUCTION READINESS CHECKLIST")
        print("="*60 + "\n")
        
        print("📁 File Structure...")
        self.check_files()
        self.check_directories()
        
        print("🔧 Environment Setup...")
        self.check_environment()
        
        print("🤖 AI Model...")
        self.check_model()
        
        print("🔐 Security...")
        self.check_permissions()
        self.check_security()
        
        self.print_results()
    
    def print_results(self):
        """Print results summary"""
        print("\n" + "-"*60)
        print("RESULTS")
        print("-"*60 + "\n")
        
        if self.passed:
            print("✅ PASSED:")
            for item in self.passed:
                print(f"   {item}")
        
        if self.failed:
            print("\n❌ FAILED:")
            for item in self.failed:
                print(f"   {item}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"   {item}")
        
        print("\n" + "="*60)
        
        if not self.failed:
            print("✨ READY FOR PRODUCTION!")
        else:
            print("⚠️  ISSUES TO RESOLVE BEFORE PRODUCTION")
        
        print("="*60 + "\n")
        
        return len(self.failed) == 0


if __name__ == '__main__':
    checklist = ProductionChecklist()
    success = checklist.run_all_checks()
    sys.exit(0 if success else 1)
