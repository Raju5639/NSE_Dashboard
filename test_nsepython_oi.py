#!/usr/bin/env python
"""Test nsepython OI functions"""

import nsepython as nse
import json

print("Testing nsepython OI functions...\n")

print("=" * 80)
print("1. Testing oi_chain_builder")
print("=" * 80)

try:
    # Try various inputs
    result = nse.oi_chain_builder()
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())[:10]}")
        print(f"Full result: {json.dumps(result, indent=2)[:1000]}")
    elif isinstance(result, list):
        print(f"List with {len(result)} items")
        if result:
            print(f"First item: {json.dumps(result[0], indent=2)[:500]}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("2. Testing get_fao_participant_oi")
print("=" * 80)

try:
    result = nse.get_fao_participant_oi()
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())[:10]}")
        print(f"Full result: {json.dumps(result, indent=2)[:1000]}")
    elif isinstance(result, list):
        print(f"List with {len(result)} items")
        if result:
            print(f"First item: {json.dumps(result[0], indent=2)[:500]}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("3. Testing quote_derivative")
print("=" * 80)

try:
    # Try with a symbol
    result = nse.quote_derivative("RELIANCE")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())}")
        print(f"Full result: {json.dumps(result, indent=2)[:1500]}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("4. Checking option_chain function")
print("=" * 80)

try:
    # Check function signature
    import inspect
    sig = inspect.signature(nse.option_chain)
    print(f"option_chain signature: {sig}")
    
    # Try calling it
    result = nse.option_chain("NIFTY")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        keys = list(result.keys())
        print(f"Keys: {keys[:10]}")
except Exception as e:
    print(f"Error: {e}")
