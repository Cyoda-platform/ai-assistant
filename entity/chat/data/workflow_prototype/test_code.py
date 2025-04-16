def run_sandboxed_code(code):
    # Provide a very limited __builtins__
    safe_globals = {
        '__builtins__': {
            'print': print,
            'range': range,
            # Add other safe functions as needed
        }
    }
    safe_locals = {}
    exec(code, safe_globals, safe_locals)
    return safe_locals

user_code = """
for i in range(3):
    print("Hello from sandbox", i)
"""
def main():
    run_sandboxed_code(user_code)

if __name__ == "__main__":
    main()
