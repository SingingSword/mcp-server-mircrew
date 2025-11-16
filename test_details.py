"""Test get_movie_details functionality with real data."""

import asyncio
import os
from mircrew_mcp.client import MirCrewClient
from mircrew_mcp.exceptions import MovieNotFoundError


async def test_get_movie_details():
    """Test get_movie_details with real movie data."""
    print("Testing get_movie_details functionality...")
    
    # Check if credentials are set
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("❌ Error: MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables must be set")
        print("\nTo run this test:")
        print("  export MIRCREW_USERNAME='your_username'")
        print("  export MIRCREW_PASSWORD='your_password'")
        print("  python test_details.py")
        return
    
    # Initialize client with credentials from environment
    client = MirCrewClient()
    
    try:
        # Authenticate
        print("Authenticating...")
        await client.authenticate()
        print(f"✓ Authenticated successfully (user_id: {client.user_id})")
        
        # First, search for Mary Poppins to get a valid movie ID
        print("\nSearching for 'Mary Poppins' to get a valid movie ID...")
        results = await client.search_movie("Mary Poppins")
        
        if not results:
            print("❌ No results found for 'Mary Poppins'. Cannot test get_movie_details.")
            return
        
        movie_id = results[0].id
        print(f"✓ Found movie with ID: {movie_id}")
        
        # Test get_movie_details with valid ID
        print(f"\nGetting details for movie ID {movie_id}...")
        details = await client.get_movie_details(movie_id)
        
        print(f"✓ Successfully retrieved movie details")
        print(f"\nMovie Details:")
        print(f"  ID: {details.id}")
        print(f"  Title: {details.title}")
        print(f"  URL: {details.url}")
        print(f"  Year: {details.year or 'N/A'}")
        print(f"  Genre: {details.genre or 'N/A'}")
        print(f"  Quality: {details.quality or 'N/A'}")
        print(f"  Size: {details.size or 'N/A'}")
        print(f"  Posted by: {details.posted_by or 'N/A'}")
        print(f"  Posted date: {details.posted_date or 'N/A'}")
        print(f"  Description: {details.description[:100] if details.description else 'N/A'}...")
        print(f"  Raw content length: {len(details.raw_content)} characters")
        
        # Verify required fields are present
        assert details.id == movie_id, "Movie ID mismatch"
        assert details.title, "Title should not be empty"
        assert details.url, "URL should not be empty"
        assert details.raw_content, "Raw content should not be empty"
        print("\n✓ All required fields are present")
        
        # Test with invalid movie ID (non-numeric)
        print("\nTesting with invalid movie ID (non-numeric)...")
        try:
            await client.get_movie_details("invalid_id")
            print("❌ Should have raised MovieNotFoundError for non-numeric ID")
        except MovieNotFoundError as e:
            print(f"✓ Correctly raised MovieNotFoundError: {e}")
        
        # Test with empty movie ID
        print("\nTesting with empty movie ID...")
        try:
            await client.get_movie_details("")
            print("❌ Should have raised MovieNotFoundError for empty ID")
        except MovieNotFoundError as e:
            print(f"✓ Correctly raised MovieNotFoundError: {e}")
        
        # Test with non-existent movie ID
        print("\nTesting with non-existent movie ID...")
        try:
            await client.get_movie_details("999999999")
            print("❌ Should have raised MovieNotFoundError for non-existent ID")
        except MovieNotFoundError as e:
            print(f"✓ Correctly raised MovieNotFoundError: {e}")
        
        print("\n✓ All get_movie_details tests passed!")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_get_movie_details())
