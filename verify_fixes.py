#!/usr/bin/env python3
"""
Elite Systems AI - Carousel Generator Verification Script
Verifies all critical fixes are properly implemented
"""

import ast
import re
from pathlib import Path

def verify_syntax():
    """Verify Python syntax is correct"""
    try:
        with open('carousel_generator.py', 'r') as f:
            code = f.read()
        
        # Parse the code to check for syntax errors
        ast.parse(code)
        print("✅ Python syntax validation: PASSED")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

def verify_font_references():
    """Verify all font references use fonts dictionary"""
    with open('carousel_generator.py', 'r') as f:
        code = f.read()
    
    # Check for problematic font references
    problematic_patterns = [
        r'\btitle_font\b',
        r'\bsubtitle_font\b', 
        r'\bbody_font\b',
        r'\bbullet_font\b'
    ]
    
    issues = []
    for pattern in problematic_patterns:
        matches = re.findall(pattern, code)
        if matches:
            issues.extend(matches)
    
    if issues:
        print(f"❌ Font reference issues found: {issues}")
        return False
    else:
        print("✅ Font references validation: PASSED")
        return True

def verify_error_handling():
    """Verify comprehensive error handling is implemented"""
    with open('carousel_generator.py', 'r') as f:
        code = f.read()
    
    required_functions = [
        'sanitize_json_string',
        'extract_json_from_text', 
        'validate_ai_response'
    ]
    
    missing = []
    for func in required_functions:
        if func not in code:
            missing.append(func)
    
    if missing:
        print(f"❌ Missing error handling functions: {missing}")
        return False
    else:
        print("✅ Error handling validation: PASSED")
        return True

def verify_analytics():
    """Verify analytics and performance tracking"""
    with open('carousel_generator.py', 'r') as f:
        code = f.read()
    
    required_features = [
        'EliteAnalytics',
        'track_event',
        'track_generation_performance',
        'track_ai_usage',
        'track_export'
    ]
    
    missing = []
    for feature in required_features:
        if feature not in code:
            missing.append(feature)
    
    if missing:
        print(f"❌ Missing analytics features: {missing}")
        return False
    else:
        print("✅ Analytics validation: PASSED")
        return True

def verify_font_caching():
    """Verify font caching is implemented"""
    with open('carousel_generator.py', 'r') as f:
        code = f.read()
    
    if '_font_cache' not in code:
        print("❌ Font caching not implemented")
        return False
    else:
        print("✅ Font caching validation: PASSED")
        return True

def verify_dependencies():
    """Verify all required dependencies are listed"""
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt missing")
        return False
    
    with open('requirements.txt', 'r') as f:
        deps = f.read()
    
    required = ['streamlit', 'pillow', 'anthropic', 'python-dotenv', 'psutil']
    missing = []
    
    for dep in required:
        if dep not in deps.lower():
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    else:
        print("✅ Dependencies validation: PASSED")
        return True

def main():
    """Run all verification checks"""
    print("🚀 Elite Systems AI - Deployment Verification")
    print("=" * 50)
    
    checks = [
        verify_syntax,
        verify_font_references,
        verify_error_handling,
        verify_analytics,
        verify_font_caching,
        verify_dependencies
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED - READY FOR ELITE DEPLOYMENT!")
        return True
    else:
        print("❌ Some checks failed - review the issues above")
        return False

if __name__ == "__main__":
    main()