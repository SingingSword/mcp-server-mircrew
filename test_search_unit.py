"""Unit tests for search_movie method (no real API calls)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from mircrew_mcp.client import MirCrewClient
from mircrew_mcp.models import MovieSearchResult


async def test_search_movie_signature():
    """Test that search_movie has correct signature and returns correct type."""
    print("Testing search_movie method signature...")
    
    # Mock the environment variables
    with patch.dict('os.environ', {'MIRCREW_USERNAME': 'test', 'MIRCREW_PASSWORD': 'test'}):
        client = MirCrewClient()
        client.authenticated = True  # Bypass authentication check
        
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <a href="./viewtopic.php?t=12345">Mary Poppins (1964)</a>
                <a href="./viewtopic.php?t=67890">Mary Poppins Returns (2018)</a>
            </body>
        </html>
        """
        
        client._authenticated_get = AsyncMock(return_value=mock_response)
        
        # Test search
        results = await client.search_movie("Mary Poppins")
        
        # Verify return type
        assert isinstance(results, list), "search_movie should return a list"
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Verify result structure
        for result in results:
            assert isinstance(result, MovieSearchResult), "Results should be MovieSearchResult objects"
            assert hasattr(result, 'id'), "Result should have 'id' field"
            assert hasattr(result, 'title'), "Result should have 'title' field"
            assert hasattr(result, 'url'), "Result should have 'url' field"
        
        print(f"✓ Method signature correct")
        print(f"✓ Returns List[MovieSearchResult]")
        print(f"✓ Results have id, title, url fields")
        
        # Test empty search
        empty_results = await client.search_movie("")
        assert empty_results == [], "Empty search should return empty list"
        print(f"✓ Empty search returns empty list")
        
        # Test whitespace search
        whitespace_results = await client.search_movie("   ")
        assert whitespace_results == [], "Whitespace search should return empty list"
        print(f"✓ Whitespace search returns empty list")
        
        print("\n✓ All unit tests passed!")


if __name__ == "__main__":
    asyncio.run(test_search_movie_signature())
