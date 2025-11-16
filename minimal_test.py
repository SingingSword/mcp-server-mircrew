#!/usr/bin/env python3
"""Minimal MCP server test"""

import json
import sys
import asyncio

async def main():
    """Minimal MCP server that responds to initialize"""
    
    # Read initialize request
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
        
    try:
        request = json.loads(line)
        print(f"Received: {request}", file=sys.stderr)
        
        if request.get("method") == "initialize":
            # Send initialize response
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "test-server",
                        "version": "1.0.0"
                    }
                }
            }
            print(json.dumps(response))
            sys.stdout.flush()
            
            # Wait for initialized notification
            line = sys.stdin.readline()
            if line:
                notification = json.loads(line)
                print(f"Received notification: {notification}", file=sys.stderr)
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
