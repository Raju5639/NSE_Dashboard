#!/usr/bin/env python
"""Check nsepython functions"""
import sys
print("Python version:", sys.version)

try:
    print("Importing nsepython...")
    import nsepython
    print("Success!")
    
    funcs = [x for x in dir(nsepython) if not x.startswith('_')]
    funcs_list = sorted(funcs)
    
    print(f"\nFound {len(funcs_list)} public functions/classes")
    
    for f in funcs_list:
        print(f)
        
except ImportError as e:
    print(f"Failed to import nsepython: {e}")
except Exception as e:
    print(f"Error: {e}")
