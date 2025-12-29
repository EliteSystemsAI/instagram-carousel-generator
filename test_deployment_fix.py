#!/usr/bin/env python3
"""
Quick deployment verification script to test if the title_font error is resolved
"""

import sys
import ast
import re

def check_for_undefined_variables():
    """Check for undefined font variables in carousel_generator.py"""
    
    with open('carousel_generator.py', 'r') as f:
        content = f.read()
    
    # List of undefined variables that should be caught
    undefined_patterns = [
        r'\btitle_font\b',
        r'\bsubtitle_font\b', 
        r'\bbody_font\b',
        r'\bbullet_font\b',
        r'\bcontent_font\b',
        r'\bcaption_font\b'
    ]
    
    errors = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Skip comments and strings
        if line.strip().startswith('#') or '"""' in line or "'''" in line:
            continue
            
        for pattern in undefined_patterns:
            if re.search(pattern, line):
                # Check if it's inside fonts dictionary reference
                if not re.search(r"fonts\[", line):
                    errors.append(f"Line {i}: Found undefined variable: {pattern}")
                    print(f"❌ Line {i}: {line.strip()}")
    
    if errors:
        print(f"\n🚨 Found {len(errors)} undefined font variable errors!")
        return False
    else:
        print("✅ No undefined font variables found!")
        return True

def check_syntax():
    """Check if the Python file has valid syntax"""
    try:
        with open('carousel_generator.py', 'r') as f:
            code = f.read()
        ast.parse(code)
        print("✅ Python syntax is valid!")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing deployment fixes...")
    
    syntax_ok = check_syntax()
    variables_ok = check_for_undefined_variables()
    
    if syntax_ok and variables_ok:
        print("\n🎉 ALL CHECKS PASSED - Ready for deployment!")
        sys.exit(0)
    else:
        print("\n💥 ERRORS FOUND - Fix before deploying!")
        sys.exit(1)# Railway Deployment Trigger
