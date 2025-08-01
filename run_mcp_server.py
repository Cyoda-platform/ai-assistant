#!/usr/bin/env python3
"""
Simple script to run the AI Assistant MCP Server
"""

import subprocess
import sys
import os

def main():
    """Run the MCP server"""
    print("🚀 Starting AI Assistant MCP Server...")
    
    # Ensure we're in the project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Activate virtual environment if it exists
    venv_python = os.path.join(project_root, ".venv", "bin", "python")
    if os.path.exists(venv_python):
        python_cmd = venv_python
        print("✅ Using virtual environment")
    else:
        python_cmd = sys.executable
        print("⚠️  Using system Python (consider using virtual environment)")
    
    try:
        # Run the MCP server with virtual environment activation
        if os.path.exists(venv_python):
            # Use virtual environment
            subprocess.run([venv_python, "app_mcp.py"], check=True)
        else:
            # Use system Python with virtual environment activation
            cmd = "source .venv/bin/activate && python app_mcp.py" if os.path.exists(".venv/bin/activate") else "python app_mcp.py"
            subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP Server failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running MCP Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
