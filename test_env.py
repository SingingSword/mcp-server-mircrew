#!/usr/bin/env python3
import os
import sys

print("Environment variables check:", file=sys.stderr)
print(f"MIRCREW_USERNAME: {os.getenv('MIRCREW_USERNAME', 'NOT SET')}", file=sys.stderr)
print(f"MIRCREW_PASSWORD: {os.getenv('MIRCREW_PASSWORD', 'NOT SET')}", file=sys.stderr)
print("All environment variables:", file=sys.stderr)
for key, value in os.environ.items():
    if 'MIRCREW' in key:
        print(f"{key}: {value}", file=sys.stderr)
sys.exit(0)
