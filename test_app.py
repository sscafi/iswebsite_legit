#!/usr/bin/env python3
"""
Test script for Domain Checker application
Verifies all components are working correctly
"""

import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter")
    except ImportError as e:
        print(f"✗ tkinter: {e}")
        return False
    
    try:
        import whois
        print("✓ python-whois")
    except ImportError as e:
        print(f"✗ python-whois: {e}")
        return False
    
    try:
        import requests
        print("✓ requests")
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    try:
        from cryptography.fernet import Fernet
        print("✓ cryptography")
    except ImportError as e:
        print(f"✗ cryptography: {e}")
        return False
    
    return True

def test_utils():
    """Test utility modules"""
    print("\nTesting utility modules...")
    
    try:
        from utils.config import config
        print("✓ Config manager")
    except Exception as e:
        print(f"✗ Config manager: {e}")
        return False
    
    try:
        from utils.logger import logger
        print("✓ Logger")
    except Exception as e:
        print(f"✗ Logger: {e}")
        return False
    
    try:
        from utils.validators import validator
        print("✓ Validator")
    except Exception as e:
        print(f"✗ Validator: {e}")
        return False
    
    try:
        from utils.cache import cache_manager, rate_limiter
        print("✓ Cache manager")
    except Exception as e:
        print(f"✗ Cache manager: {e}")
        return False
    
    return True

def test_services():
    """Test service modules"""
    print("\nTesting service modules...")
    
    try:
        from services.domain_checker import domain_checker
        print("✓ Domain checker service")
    except Exception as e:
        print(f"✗ Domain checker service: {e}")
        return False
    
    return True

def test_validation():
    """Test domain validation"""
    print("\nTesting domain validation...")
    
    try:
        from utils.validators import validator
        
        # Test valid domains
        test_domains = [
            "example.com",
            "google.com",
            "test.co.uk",
            "subdomain.example.org"
        ]
        
        for domain in test_domains:
            is_valid, result = validator.validate_domain(domain)
            if is_valid:
                print(f"✓ Valid domain: {domain}")
            else:
                print(f"✗ Invalid domain: {domain} - {result}")
        
        # Test invalid domains
        invalid_domains = [
            "",
            "not-a-domain",
            "http://example.com",
            "example"
        ]
        
        for domain in invalid_domains:
            is_valid, result = validator.validate_domain(domain)
            if not is_valid:
                print(f"✓ Correctly rejected: {domain}")
            else:
                print(f"✗ Should have rejected: {domain}")
        
        return True
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def test_config():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    try:
        from utils.config import config
        
        # Test API key management
        test_key = "test_api_key_123"
        config.set_api_key('test_service', test_key)
        retrieved_key = config.get_api_key('test_service')
        
        if retrieved_key == test_key:
            print("✓ API key storage/retrieval")
        else:
            print("✗ API key storage/retrieval failed")
            return False
        
        # Test settings management
        config.set_setting('test_setting', True)
        setting_value = config.get_setting('test_setting')
        
        if setting_value == True:
            print("✓ Settings storage/retrieval")
        else:
            print("✗ Settings storage/retrieval failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Domain Checker - Component Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_utils,
        test_services,
        test_validation,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"Test failed: {test.__name__}")
        except Exception as e:
            print(f"Test error: {test.__name__} - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("python main.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTo install missing dependencies:")
        print("pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 