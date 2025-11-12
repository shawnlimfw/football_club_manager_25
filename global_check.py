import ast

with open("mainbase.py", "r") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Find all assigned variable names (x = ..., x += ...)
        assigned = {
            n.id
            for n in ast.walk(node)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
        }

        # Find all declared global names
        globals_declared = {
            name
            for n in ast.walk(node)
            if isinstance(n, ast.Global)
            for name in n.names
        }

        # Compare
        missing_globals = assigned - globals_declared
        if missing_globals:
            print(f"In function '{node.name}', variables assigned but not declared global: {missing_globals}")