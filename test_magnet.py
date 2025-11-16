"""Test magnet link retrieval with real API calls."""

import asyncio
import os
import sys

from mircrew_mcp.client import MirCrewClient
from mircrew_mcp.exceptions import (
    AuthenticationError,
    MovieNotFoundError,
    ParsingError,
    NetworkError
)


async def test_magnet_link():
    """Test magnet link retrieval with Mary Poppins."""
    
    # Check for credentials
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("❌ Error: MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables must be set")
        print("\nUsage:")
        print("  export MIRCREW_USERNAME='your_username'")
        print("  export MIRCREW_PASSWORD='your_password'")
        print("  python test_magnet.py")
        sys.exit(1)
    
    print("Testing MirCrew Magnet Link Retrieval")
    print("=" * 50)
    
    async with MirCrewClient(username, password) as client:
        # Authenticate
        print("\n1. Authenticating...")
        try:
            await client.authenticate()
            print(f"✓ Authentication successful")
            print(f"  Session ID: {client.session_id[:20]}..." if client.session_id else "  No session ID")
            print(f"  User ID: {client.user_id}")
        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            sys.exit(1)
        
        # Search for Mary Poppins to get a valid movie ID
        print("\n2. Searching for 'Mary Poppins'...")
        try:
            results = await client.search_movie("Mary Poppins")
            if not results:
                print("❌ No results found for 'Mary Poppins'")
                sys.exit(1)
            
            print(f"✓ Found {len(results)} result(s)")
            movie_id = results[0].id
            movie_title = results[0].title
            print(f"  Using movie: {movie_title} (ID: {movie_id})")
        except Exception as e:
            print(f"❌ Search failed: {e}")
            sys.exit(1)
        
        # Get magnet link
        print(f"\n3. Getting magnet link for movie ID {movie_id}...")
        try:
            magnet_uri = await client.get_magnet_link(movie_id)
            print(f"✓ Magnet link retrieved successfully")
            print(f"\nMagnet URI:")
            print(f"  {magnet_uri[:100]}..." if len(magnet_uri) > 100 else f"  {magnet_uri}")
            
            # Validate format
            if magnet_uri.startswith("magnet:?"):
                print(f"\n✓ Magnet URI format is valid")
            else:
                print(f"\n❌ Invalid magnet URI format")
                
            # Check for required magnet components
            if "xt=urn:btih:" in magnet_uri:
                print(f"✓ Contains BitTorrent info hash")
            else:
                print(f"⚠ Warning: Missing BitTorrent info hash")
                
        except MovieNotFoundError as e:
            print(f"❌ Movie not found: {e}")
            sys.exit(1)
        except ParsingError as e:
            print(f"❌ Parsing error: {e}")
            print("\nThis might mean:")
            print("  - The magnet link is not visible on the page")
            print("  - The like action didn't work as expected")
            print("  - The page structure has changed")
            sys.exit(1)
        except NetworkError as e:
            print(f"❌ Network error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Test error handling
        print("\n4. Testing error handling...")
        
        # Test with invalid movie ID (non-numeric)
        print("  Testing with non-numeric movie ID...")
        try:
            await client.get_magnet_link("invalid_id")
            print("  ❌ Should have raised MovieNotFoundError")
        except MovieNotFoundError as e:
            print(f"  ✓ Correctly raised MovieNotFoundError: {e}")
        
        # Test with empty movie ID
        print("  Testing with empty movie ID...")
        try:
            await client.get_magnet_link("")
            print("  ❌ Should have raised MovieNotFoundError")
        except MovieNotFoundError as e:
            print(f"  ✓ Correctly raised MovieNotFoundError: {e}")
        
        # Test with non-existent movie ID
        print("  Testing with non-existent movie ID...")
        try:
            await client.get_magnet_link("999999999")
            print("  ❌ Should have raised MovieNotFoundError or ParsingError")
        except (MovieNotFoundError, ParsingError) as e:
            print(f"  ✓ Correctly raised error: {type(e).__name__}")
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_magnet_link())
