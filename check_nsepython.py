"""
Check nsepython library capabilities for OI data
"""
try:
    import nsepython as nse
    
    print("nsepython module found!")
    print("\nAvailable functions/classes:")
    
    # Get all attributes
    attrs = dir(nse)
    
    # Filter for OI or open interest related functions
    print("\nOI/Options related functions:")
    for attr in attrs:
        if 'oi' in attr.lower() or 'interest' in attr.lower() or 'spurt' in attr.lower() or 'option' in attr.lower() or 'derivative' in attr.lower():
            print(f"  - {attr}")
    
    # Show all public functions (not starting with _)
    print("\nAll public functions/classes:")
    for attr in sorted(attrs):
        if not attr.startswith('_'):
            obj = getattr(nse, attr)
            if callable(obj):
                print(f"  - {attr}")
    
    # Try to find relevant functions
    print("\n\nTrying to call relevant functions:")
    
    # Common patterns
    if hasattr(nse, 'oi_spurts'):
        print("Found oi_spurts!")
        result = nse.oi_spurts()
        print(f"Result: {result}")
    
    if hasattr(nse, 'get_oi_spurts'):
        print("Found get_oi_spurts!")
        result = nse.get_oi_spurts()
        print(f"Result: {result}")
    
    if hasattr(nse, 'open_interest'):
        print("Found open_interest!")
        
    if hasattr(nse, 'option_chain'):
        print("Found option_chain!")
        
except ImportError:
    print("nsepython not installed")
except Exception as e:
    print(f"Error: {e}")
