"""Test search_movie functionality with real data."""

import asyncio
import os
from mircrew_mcp.client import MirCrewClient


async def test_search_movie():
    """Test search_movie with Mary Poppins."""
    print("Testing search_movie functionality...")
    
    # Check if credentials are set
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("❌ Error: MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables must be set")
        print("\nTo run this test:")
        print("  export MIRCREW_USERNAME='your_username'")
        print("  export MIRCREW_PASSWORD='your_password'")
        print("  python test_search.py")
        return
    
    # Initialize client with credentials from environment
    client = MirCrewClient()
    
    try:
        # Authenticate
        print("Authenticating...")
        await client.authenticate()
        print(f"✓ Authenticated successfully (user_id: {client.user_id})")
        
        # Search for Mary Poppins
        print("\nSearching for 'Mary Poppins'...")
        results = await client.search_movie("Mary Poppins")
        
        print(f"✓ Search completed. Found {len(results)} result(s)")
        
        if results:
            print("\nSearch Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   ID: {result.id}")
                print(f"   URL: {result.url}")
        else:
            print("No results found for 'Mary Poppins'")
        
        # Test empty search
        print("\n\nTesting empty search...")
        empty_results = await client.search_movie("")
        print(f"✓ Empty search returned {len(empty_results)} results (expected 0)")
        
        # Test search with no results (unlikely title)
        print("\nTesting search with unlikely title...")
        no_results = await client.search_movie("xyzabc123nonexistent")
        print(f"✓ Search for nonexistent movie returned {len(no_results)} results")
        
        print("\n✓ All search tests passed!")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_search_movie())
