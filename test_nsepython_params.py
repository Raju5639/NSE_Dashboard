#!/usr/bin/env python
"""Test nsepython OI functions with proper parameters"""

import nsepython as nse
import json
from datetime import datetime, timedelta
import pytz

print("Testing nsepython OI functions with parameters...\n")

print("=" * 80)
print("1. Testing oi_chain_builder with RELIANCE")
print("=" * 80)

try:
    result = nse.oi_chain_builder("RELIANCE")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())[:20]}")
        # Show first few items
        items = list(result.items())[:3]
        for key, val in items:
            print(f"  {key}: {val}")
    else:
        print(f"Result (first 500 chars): {str(result)[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("2. Testing get_fao_participant_oi with today's date")
print("=" * 80)

try:
    # Use today's date
    today = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%b-%Y')
    print(f"Using date: {today}")
    
    result = nse.get_fao_participant_oi(today)
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())}")
        print(f"Sample data: {json.dumps(result, indent=2)[:1000]}")
    elif isinstance(result, list):
        print(f"List with {len(result)} items")
        if result:
            print(f"First 3 items:")
            for i, item in enumerate(result[:3]):
                print(f"  {i+1}. {json.dumps(item, indent=2)[:300]}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("3. Testing option_chain with RELIANCE")
print("=" * 80)

try:
    result = nse.option_chain("RELIANCE")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())[:10]}")
        if result:
            items = list(result.items())[:2]
            for key, val in items:
                print(f"  Key: {key}")
                if isinstance(val, list):
                    print(f"    List with {len(val)} items")
                    if val:
                        print(f"    First item: {json.dumps(val[0], indent=2)[:300]}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("4. Testing quote_derivative with detailed output")
print("=" * 80)

try:
    result = nse.quote_derivative("RELIANCE")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        # Check for stocks array which might have OI data
        if 'stocks' in result:
            print(f"'stocks' key found with {len(result['stocks'])} items")
            if result['stocks']:
                first = result['stocks'][0]
                print(f"First stock item keys: {list(first.keys())[:10]}")
                # Print first stock with OI info
                print(f"First stock (relevant fields):")
                for key in first.keys():
                    if any(x in key.lower() for x in ['oi', 'interest', 'chng', 'change']):
                        print(f"  {key}: {first[key]}")
        
        # Check for expiryDates
        if 'expiryDates' in result:
            print(f"Expiry dates: {result['expiryDates']}")
            
except Exception as e:
    print(f"Error: {e}")
