#!/usr/bin/env python3
"""Debug version of MirCrew MCP server"""

import os
import sys

# Set environment variables directly
os.environ["MIRCREW_USERNAME"] = "SingingSword"
# os.environ["MIRCREW_PASSWORD"] = "your_password_here"

# Now import and run the main module
sys.path.insert(0, '/home/enrico/Sorgenti/mcp-server-mircrew')

try:
    from mircrew_mcp.__main__ import mcp
    print("Starting debug MCP server...", file=sys.stderr)
    mcp.run()
except Exception as e:
    print(f"Error starting server: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
