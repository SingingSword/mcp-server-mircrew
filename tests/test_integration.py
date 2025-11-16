"""
Integration tests for MirCrew MCP Server.

Tests all functionality end-to-end with real data using "Mary Poppins" as the test case.
These tests make real HTTP requests to the MirCrew website (no mocking).

Requirements tested:
- 7.1: Test with real HTTP requests to MirCrew website
- 7.2: Use "Mary Poppins" as test movie title
- 7.3: No mocked responses
- 7.4: Clean up temporary test files after execution
- 7.5: Verify all three tools work end-to-end
"""

import asyncio
import os
import sys
from typing import Optional

from mircrew_mcp.client import MirCrewClient
from mircrew_mcp.models import MovieSearchResult, MovieDetails
from mircrew_mcp.exceptions import (
    AuthenticationError,
    MovieNotFoundError,
    ParsingError,
    NetworkError,
    MirCrewError
)


class TestResults:
    """Track test results for reporting."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def pass_test(self, test_name: str):
        """Record a passed test."""
        self.passed += 1
        print(f"  ✓ {test_name}")
    
    def fail_test(self, test_name: str, error: str):
        """Record a failed test."""
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}: {error}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}")
                print(f"    {error}")
        
        if self.failed == 0:
            print("\n✓ All tests passed!")
            return True
        else:
            print(f"\n❌ {self.failed} test(s) failed")
            return False


async def test_authentication(client: MirCrewClient, results: TestResults) -> bool:
    """
    Test authentication with real credentials from environment variables.
    
    Requirements: 7.1, 7.3
    """
    print("\n1. Testing Authentication")
    print("-" * 70)
    
    try:
        # Test that credentials are loaded
        if not client.username or not client.password:
            results.fail_test(
                "Credentials loaded from environment",
                "MIRCREW_USERNAME or MIRCREW_PASSWORD not set"
            )
            return False
        results.pass_test("Credentials loaded from environment")
        
        print(f"  Using username: {client.username}")
        
        # Perform authentication
        success = await client.authenticate()
        
        if not success:
            results.fail_test("Authentication successful", "authenticate() returned False")
            return False
        results.pass_test("Authentication successful")
        
        # Verify session cookies are set
        if not client.session_id:
            results.fail_test("Session ID set", "session_id is None")
            return False
        results.pass_test("Session ID set")
        
        if not client.user_id:
            results.fail_test("User ID set", "user_id is None")
            return False
        results.pass_test("User ID set")
        
        if not client.autologin_key:
            results.fail_test("Autologin key set", "autologin_key is None")
            return False
        results.pass_test("Autologin key set")
        
        # Verify authenticated flag is set
        if not client.authenticated:
            results.fail_test("Authenticated flag set", "authenticated is False")
            return False
        results.pass_test("Authenticated flag set")
        
        print(f"\n  Session ID: {client.session_id[:20]}...")
        print(f"  User ID: {client.user_id}")
        print(f"  Autologin Key: {client.autologin_key[:20]}...")
        
        return True
        
    except AuthenticationError as e:
        results.fail_test("Authentication", f"AuthenticationError: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        results.fail_test("Authentication", f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_movie(client: MirCrewClient, results: TestResults) -> Optional[str]:
    """
    Test search_movie with "Mary Poppins" query.
    
    Requirements: 7.1, 7.2, 7.3
    
    Returns:
        Movie ID from first search result, or None if search failed
    """
    print("\n2. Testing search_movie with 'Mary Poppins'")
    print("-" * 70)
    
    try:
        # Search for Mary Poppins
        results_list = await client.search_movie("Mary Poppins")
        
        # Verify results is a list
        if not isinstance(results_list, list):
            results.fail_test(
                "search_movie returns list",
                f"Expected list, got {type(results_list)}"
            )
            return None
        results.pass_test("search_movie returns list")
        
        # Verify we got results
        if len(results_list) == 0:
            results.fail_test(
                "search_movie finds Mary Poppins",
                "No results found for 'Mary Poppins'"
            )
            return None
        results.pass_test(f"search_movie finds Mary Poppins ({len(results_list)} result(s))")
        
        # Verify first result is a MovieSearchResult
        first_result = results_list[0]
        if not isinstance(first_result, MovieSearchResult):
            results.fail_test(
                "Result is MovieSearchResult",
                f"Expected MovieSearchResult, got {type(first_result)}"
            )
            return None
        results.pass_test("Result is MovieSearchResult")
        
        # Verify result has required fields
        if not first_result.id:
            results.fail_test("Result has id field", "id is empty")
            return None
        results.pass_test("Result has id field")
        
        if not first_result.title:
            results.fail_test("Result has title field", "title is empty")
            return None
        results.pass_test("Result has title field")
        
        if not first_result.url:
            results.fail_test("Result has url field", "url is empty")
            return None
        results.pass_test("Result has url field")
        
        # Verify URL format
        if not first_result.url.startswith("http"):
            results.fail_test(
                "URL is properly formatted",
                f"URL doesn't start with http: {first_result.url}"
            )
            return None
        results.pass_test("URL is properly formatted")
        
        # Verify ID is numeric
        if not first_result.id.isdigit():
            results.fail_test(
                "Movie ID is numeric",
                f"ID is not numeric: {first_result.id}"
            )
            return None
        results.pass_test("Movie ID is numeric")
        
        print(f"\n  Found: {first_result.title}")
        print(f"  ID: {first_result.id}")
        print(f"  URL: {first_result.url}")
        
        # Test empty search
        empty_results = await client.search_movie("")
        if len(empty_results) != 0:
            results.fail_test(
                "Empty search returns empty list",
                f"Expected 0 results, got {len(empty_results)}"
            )
        else:
            results.pass_test("Empty search returns empty list")
        
        return first_result.id
        
    except Exception as e:
        results.fail_test("search_movie", f"Unexpected error: {e}")
        return None


async def test_get_movie_details(
    client: MirCrewClient,
    movie_id: str,
    results: TestResults
) -> bool:
    """
    Test get_movie_details with movie ID from search results.
    
    Requirements: 7.1, 7.3
    """
    print("\n3. Testing get_movie_details")
    print("-" * 70)
    
    try:
        # Get movie details
        details = await client.get_movie_details(movie_id)
        
        # Verify details is a MovieDetails object
        if not isinstance(details, MovieDetails):
            results.fail_test(
                "get_movie_details returns MovieDetails",
                f"Expected MovieDetails, got {type(details)}"
            )
            return False
        results.pass_test("get_movie_details returns MovieDetails")
        
        # Verify required fields
        if details.id != movie_id:
            results.fail_test(
                "Movie ID matches",
                f"Expected {movie_id}, got {details.id}"
            )
            return False
        results.pass_test("Movie ID matches")
        
        if not details.title:
            results.fail_test("Details has title", "title is empty")
            return False
        results.pass_test("Details has title")
        
        if not details.url:
            results.fail_test("Details has url", "url is empty")
            return False
        results.pass_test("Details has url")
        
        if not details.raw_content:
            results.fail_test("Details has raw_content", "raw_content is empty")
            return False
        results.pass_test("Details has raw_content")
        
        # Verify URL format
        if not details.url.startswith("http"):
            results.fail_test(
                "Details URL is properly formatted",
                f"URL doesn't start with http: {details.url}"
            )
            return False
        results.pass_test("Details URL is properly formatted")
        
        print(f"\n  Title: {details.title}")
        print(f"  ID: {details.id}")
        print(f"  URL: {details.url}")
        print(f"  Year: {details.year or 'N/A'}")
        print(f"  Genre: {details.genre or 'N/A'}")
        print(f"  Quality: {details.quality or 'N/A'}")
        print(f"  Size: {details.size or 'N/A'}")
        print(f"  Posted by: {details.posted_by or 'N/A'}")
        print(f"  Posted date: {details.posted_date or 'N/A'}")
        print(f"  Description: {details.description[:100] if details.description else 'N/A'}...")
        print(f"  Raw content length: {len(details.raw_content)} characters")
        
        # Test error handling - invalid movie ID
        try:
            await client.get_movie_details("invalid_id")
            results.fail_test(
                "Invalid ID raises MovieNotFoundError",
                "No exception raised for invalid ID"
            )
        except MovieNotFoundError:
            results.pass_test("Invalid ID raises MovieNotFoundError")
        except Exception as e:
            results.fail_test(
                "Invalid ID raises MovieNotFoundError",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        # Test error handling - empty movie ID
        try:
            await client.get_movie_details("")
            results.fail_test(
                "Empty ID raises MovieNotFoundError",
                "No exception raised for empty ID"
            )
        except MovieNotFoundError:
            results.pass_test("Empty ID raises MovieNotFoundError")
        except Exception as e:
            results.fail_test(
                "Empty ID raises MovieNotFoundError",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        # Test error handling - non-existent movie ID
        try:
            await client.get_movie_details("999999999")
            results.fail_test(
                "Non-existent ID raises MovieNotFoundError",
                "No exception raised for non-existent ID"
            )
        except MovieNotFoundError:
            results.pass_test("Non-existent ID raises MovieNotFoundError")
        except Exception as e:
            results.fail_test(
                "Non-existent ID raises MovieNotFoundError",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        return True
        
    except Exception as e:
        results.fail_test("get_movie_details", f"Unexpected error: {e}")
        return False


async def test_get_magnet_link(
    client: MirCrewClient,
    movie_id: str,
    results: TestResults
) -> bool:
    """
    Test get_magnet_link with movie ID from search results.
    
    Requirements: 7.1, 7.3
    """
    print("\n4. Testing get_magnet_link")
    print("-" * 70)
    
    try:
        # Get magnet link
        magnet_uri = await client.get_magnet_link(movie_id)
        
        # Verify magnet_uri is a string
        if not isinstance(magnet_uri, str):
            results.fail_test(
                "get_magnet_link returns string",
                f"Expected str, got {type(magnet_uri)}"
            )
            return False
        results.pass_test("get_magnet_link returns string")
        
        # Verify magnet URI is not empty
        if not magnet_uri:
            results.fail_test("Magnet URI is not empty", "magnet_uri is empty")
            return False
        results.pass_test("Magnet URI is not empty")
        
        # Verify magnet URI format
        if not magnet_uri.startswith("magnet:?"):
            results.fail_test(
                "Magnet URI has correct format",
                f"URI doesn't start with 'magnet:?': {magnet_uri[:50]}"
            )
            return False
        results.pass_test("Magnet URI has correct format")
        
        # Verify magnet URI contains BitTorrent info hash
        if "xt=urn:btih:" not in magnet_uri:
            results.fail_test(
                "Magnet URI contains info hash",
                "URI doesn't contain 'xt=urn:btih:'"
            )
            return False
        results.pass_test("Magnet URI contains info hash")
        
        print(f"\n  Magnet URI: {magnet_uri[:100]}...")
        print(f"  Full length: {len(magnet_uri)} characters")
        
        # Test error handling - invalid movie ID
        try:
            await client.get_magnet_link("invalid_id")
            results.fail_test(
                "Invalid ID raises MovieNotFoundError",
                "No exception raised for invalid ID"
            )
        except MovieNotFoundError:
            results.pass_test("Invalid ID raises MovieNotFoundError")
        except Exception as e:
            results.fail_test(
                "Invalid ID raises MovieNotFoundError",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        # Test error handling - empty movie ID
        try:
            await client.get_magnet_link("")
            results.fail_test(
                "Empty ID raises MovieNotFoundError",
                "No exception raised for empty ID"
            )
        except MovieNotFoundError:
            results.pass_test("Empty ID raises MovieNotFoundError")
        except Exception as e:
            results.fail_test(
                "Empty ID raises MovieNotFoundError",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        # Test error handling - non-existent movie ID
        try:
            await client.get_magnet_link("999999999")
            results.fail_test(
                "Non-existent ID raises error",
                "No exception raised for non-existent ID"
            )
        except (MovieNotFoundError, ParsingError):
            results.pass_test("Non-existent ID raises error")
        except Exception as e:
            results.fail_test(
                "Non-existent ID raises error",
                f"Wrong exception type: {type(e).__name__}"
            )
        
        return True
        
    except Exception as e:
        results.fail_test("get_magnet_link", f"Unexpected error: {e}")
        return False


async def run_integration_tests():
    """
    Run all integration tests end-to-end.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    print("=" * 70)
    print("MIRCREW MCP SERVER - INTEGRATION TESTS")
    print("=" * 70)
    print("\nTesting with real data using 'Mary Poppins' as test case")
    print("No mocked responses - all requests go to actual MirCrew website")
    print()
    
    # Check for credentials
    username = os.getenv("MIRCREW_USERNAME")
    password = os.getenv("MIRCREW_PASSWORD")
    
    if not username or not password:
        print("❌ Error: MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables must be set")
        print("\nUsage:")
        print("  export MIRCREW_USERNAME='your_username'")
        print("  export MIRCREW_PASSWORD='your_password'")
        print("  python -m pytest tests/test_integration.py")
        print("\nOr run directly:")
        print("  python tests/test_integration.py")
        sys.exit(1)
    
    results = TestResults()
    movie_id = None
    
    try:
        # Initialize client (credentials read from environment variables)
        async with MirCrewClient() as client:
            # Test 1: Authentication
            auth_success = await test_authentication(client, results)
            if not auth_success:
                print("\n❌ Authentication failed. Cannot proceed with other tests.")
                results.print_summary()
                sys.exit(1)
            
            # Test 2: Search movie
            movie_id = await test_search_movie(client, results)
            if not movie_id:
                print("\n❌ Search failed. Cannot proceed with details and magnet tests.")
                results.print_summary()
                sys.exit(1)
            
            # Test 3: Get movie details
            details_success = await test_get_movie_details(client, movie_id, results)
            
            # Test 4: Get magnet link
            magnet_success = await test_get_magnet_link(client, movie_id, results)
            
            # Print summary
            success = results.print_summary()
            
            # Exit with appropriate code
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        results.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during test execution: {e}")
        import traceback
        traceback.print_exc()
        results.print_summary()
        sys.exit(1)
    finally:
        # Cleanup: No temporary files are created by these tests
        # All data is in memory only
        print("\n✓ Cleanup complete (no temporary files created)")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
