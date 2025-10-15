def inspect_object(obj):
    props = {}
    methods = {}

    print(f"\nInspecting object: {obj}")
    print(f"Type: {type(obj)}")

    for attr_name in dir(obj):
        # Skip special (dunder) methods like __init__, __repr__
        if attr_name.startswith("__"):
            continue

        try:
            attr = getattr(obj, attr_name)
            if callable(attr):
                methods[attr_name] = attr
            else:
                props[attr_name] = attr
        except Exception as e:
            props[attr_name] = f"Error: {e}"

    print("\nProperties (non-callable attributes):")
    for key, value in props.items():
        print(f"  {key}: {value}")

    print("\nMethods (callable functions):")
    for key in methods.keys():
        print(f"  {key}()")
