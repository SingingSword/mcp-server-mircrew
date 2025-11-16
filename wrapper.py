#!/usr/bin/env python3
"""Wrapper script for MirCrew MCP server to ensure proper environment setup"""

import os
import sys
import subprocess

def main():
    # Ensure environment variables are set
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("Error: MIRCREW_USERNAME and MIRCREW_PASSWORD must be set", file=sys.stderr)
        sys.exit(1)
    
    # Set up the environment
    env = os.environ.copy()
    env["MIRCREW_USERNAME"] = username
    env["MIRCREW_PASSWORD"] = password
    
    # Run the actual MCP server using current python
    try:
        result = subprocess.run([
            sys.executable, "-m", "mircrew_mcp"
        ], env=env)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
