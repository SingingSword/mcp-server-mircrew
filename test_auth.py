"""Simple test script to verify authentication works."""

import asyncio
import os
from mircrew_mcp.client import MirCrewClient


async def test_authentication():
    """Test authentication with MirCrew."""
    print("Testing MirCrew authentication...")
    
    # Check if credentials are set
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("❌ Error: MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables must be set")
        return False
    
    print(f"Using username: {username}")
    
    try:
        async with MirCrewClient() as client:
            print("Authenticating...")
            success = await client.authenticate()
            
            if success:
                print("✓ Authentication successful!")
                print(f"  Session ID: {client.session_id[:20]}..." if client.session_id else "  No session ID")
                print(f"  User ID: {client.user_id}")
                print(f"  Autologin Key: {client.autologin_key[:20]}..." if client.autologin_key else "  No autologin key")
                return True
            else:
                print("❌ Authentication failed")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_authentication())
