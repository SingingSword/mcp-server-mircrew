"""FastMCP server entry point for MirCrew Movie Archive."""

import os
import sys
import asyncio
from typing import List, Dict, Any

try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: fastmcp is not installed. Please install it with: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

from .client import MirCrewClient
from .exceptions import (
    MirCrewError,
    AuthenticationError,
    MovieNotFoundError,
    ParsingError,
    NetworkError
)


# Initialize FastMCP server
mcp = FastMCP("MirCrew Movie Archive")

# Global client instance
_client: MirCrewClient = None


async def get_client() -> MirCrewClient:
    """
    Get or create the MirCrew client instance.
    
    Returns:
        Authenticated MirCrewClient instance
        
    Raises:
        AuthenticationError: If credentials are missing or authentication fails
    """
    global _client
    
    if _client is None or not _client.authenticated:
        try:
            # Create client (will read credentials from environment)
            _client = MirCrewClient()
            
            # Authenticate
            await _client.authenticate()
            
        except AuthenticationError as e:
            # Reset client on auth failure
            _client = None
            raise AuthenticationError(
                f"Failed to authenticate with MirCrew: {str(e)}. "
                "Please ensure MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables are set."
            )
        except Exception as e:
            # Reset client on any failure
            _client = None
            raise MirCrewError(f"Failed to initialize MirCrew client: {str(e)}")
    
    return _client


@mcp.tool()
async def search_movie(title: str) -> List[Dict[str, str]]:
    """
    Search for movies by title in the MirCrew archive.
    
    This tool searches the MirCrew movie archive for movies matching the provided title.
    It returns a list of search results, each containing the movie ID, title, and URL.
    
    Args:
        title: The movie title to search for (e.g., "Mary Poppins", "The Matrix")
    
    Returns:
        A list of dictionaries, each containing:
        - id: The movie's unique identifier (topic ID)
        - title: The movie's title
        - url: The full URL to the movie's detail page
        
        Returns an empty list if no results are found.
    
    Example:
        >>> results = await search_movie("Mary Poppins")
        >>> print(results[0])
        {'id': '12345', 'title': 'Mary Poppins (1964)', 'url': 'https://mircrew-releases.org/viewtopic.php?t=12345'}
    
    Raises:
        AuthenticationError: If not authenticated or credentials are invalid
        NetworkError: If there's a network communication error
        MirCrewError: For other unexpected errors
    """
    try:
        client = await get_client()
        results = await client.search_movie(title)
        
        # Convert dataclass objects to dictionaries for JSON serialization
        return [
            {
                "id": result.id,
                "title": result.title,
                "url": result.url
            }
            for result in results
        ]
    
    except (AuthenticationError, NetworkError, MirCrewError) as e:
        raise Exception(f"Search failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error during search: {str(e)}")


@mcp.tool()
async def get_movie_details(movie_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific movie.
    
    This tool retrieves comprehensive metadata about a movie from the MirCrew archive
    using its unique movie ID. The ID can be obtained from search results.
    
    Args:
        movie_id: The movie's unique identifier (topic ID) as a string (e.g., "12345")
    
    Returns:
        A dictionary containing detailed movie information:
        - id: The movie's unique identifier
        - title: The movie's title
        - url: The full URL to the movie's detail page
        - description: Movie description or plot summary
        - year: Release year (if available)
        - genre: Movie genre(s) (if available)
        - quality: Video quality (e.g., "1080p", "720p") (if available)
        - size: File size (if available)
        - posted_by: Username of the uploader (if available)
        - posted_date: Date when the movie was posted (if available)
        - raw_content: Full post content for additional parsing
    
    Example:
        >>> details = await get_movie_details("12345")
        >>> print(details['title'])
        'Mary Poppins (1964)'
    
    Raises:
        MovieNotFoundError: If the movie ID is invalid or movie doesn't exist
        AuthenticationError: If not authenticated or credentials are invalid
        NetworkError: If there's a network communication error
        ParsingError: If the response cannot be parsed
        MirCrewError: For other unexpected errors
    """
    try:
        client = await get_client()
        details = await client.get_movie_details(movie_id)
        
        # Convert dataclass to dictionary for JSON serialization
        return {
            "id": details.id,
            "title": details.title,
            "url": details.url,
            "description": details.description,
            "year": details.year,
            "genre": details.genre,
            "quality": details.quality,
            "size": details.size,
            "posted_by": details.posted_by,
            "posted_date": details.posted_date,
            "raw_content": details.raw_content
        }
    
    except MovieNotFoundError as e:
        raise Exception(f"Movie not found: {str(e)}")
    except (AuthenticationError, NetworkError, ParsingError, MirCrewError) as e:
        raise Exception(f"Failed to get movie details: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error getting movie details: {str(e)}")


@mcp.tool()
async def get_magnet_link(movie_id: str) -> str:
    """
    Get the magnet link for a movie.
    
    This tool retrieves the magnet link (torrent URI) for a specific movie from the
    MirCrew archive. It automatically performs the necessary "like" action to reveal
    the magnet link if required by the website.
    
    Args:
        movie_id: The movie's unique identifier (topic ID) as a string (e.g., "12345")
    
    Returns:
        The magnet URI as a string, which can be used with torrent clients.
        Format: "magnet:?xt=urn:btih:..."
    
    Example:
        >>> magnet = await get_magnet_link("12345")
        >>> print(magnet)
        'magnet:?xt=urn:btih:abc123...'
    
    Raises:
        MovieNotFoundError: If the movie ID is invalid or movie doesn't exist
        AuthenticationError: If not authenticated or credentials are invalid
        NetworkError: If there's a network communication error
        ParsingError: If the magnet link cannot be found or parsed
        MirCrewError: For other unexpected errors
    """
    try:
        client = await get_client()
        magnet_uri = await client.get_magnet_link(movie_id)
        
        return magnet_uri
    
    except MovieNotFoundError as e:
        raise Exception(f"Movie not found: {str(e)}")
    except ParsingError as e:
        raise Exception(f"Magnet link not found or unavailable: {str(e)}")
    except (AuthenticationError, NetworkError, MirCrewError) as e:
        raise Exception(f"Failed to get magnet link: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error getting magnet link: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    try:
        # Verify credentials are available before starting
        username = os.getenv("MIRCREW_USERNAME")
        password = os.getenv("MIRCREW_PASSWORD")
        
        if not username or not password:
            print(
                "Error: Missing required environment variables.\n"
                "Please set MIRCREW_USERNAME and MIRCREW_PASSWORD before starting the server.\n"
                "\nExample:\n"
                "  export MIRCREW_USERNAME=your_username\n"
                "  export MIRCREW_PASSWORD=your_password\n"
                "  python -m mircrew_mcp",
                file=sys.stderr
            )
            sys.exit(1)
        
        # Run the FastMCP server
        mcp.run()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
