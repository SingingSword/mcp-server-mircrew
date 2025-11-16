# Implementation Plan

- [x] 1. Set up project structure and environment
  - Create virtual environment in venv/ directory
  - Initialize git repository with .gitignore
  - Create project directory structure (mircrew_mcp/ package)
  - Create requirements.txt with dependencies (fastmcp, httpx, beautifulsoup4, lxml, python-dotenv)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 2. Implement core data models and exceptions
  - Create mircrew_mcp/models.py with MovieSearchResult, MovieDetails, and MagnetLink dataclasses
  - Create mircrew_mcp/exceptions.py with custom exception hierarchy (MirCrewError, AuthenticationError, MovieNotFoundError, ParsingError, NetworkError)
  - _Requirements: 8.1, 8.5_

- [x] 3. Implement session manager and authentication
  - Create MirCrewClient class in mircrew_mcp/client.py with __init__ method that reads MIRCREW_USERNAME and MIRCREW_PASSWORD from environment variables
  - Implement authenticate() method that performs GET to extract form tokens, then POST to /ucp.php?mode=login with credentials
  - Implement session cookie storage (phpbb3_12hgm_sid, phpbb3_12hgm_u, phpbb3_12hgm_k)
  - Add error handling for missing credentials and failed authentication
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.5_

- [x] 4. Implement HTTP client wrapper
  - Configure httpx.AsyncClient in MirCrewClient with standard headers (User-Agent, Accept, etc.)
  - Implement automatic cookie handling for authenticated requests
  - Add connection pooling and SSL verification
  - _Requirements: 1.4_

- [x] 5. Implement HTML parser utilities
  - Create mircrew_mcp/parser.py with BeautifulSoup4 parsing functions
  - Implement parse_search_results() to extract topic IDs and titles from search page
  - Implement parse_movie_details() to extract metadata from movie detail page
  - Implement parse_magnet_link() to extract magnet URI from post content
  - Add error handling for parsing failures
  - _Requirements: 2.2, 2.3, 3.2, 4.2_

- [x] 6. Implement search_movie tool
  - Create async search_movie() method in MirCrewClient that performs GET to /search.php with title parameter
  - Parse HTML response to extract list of MovieSearchResult objects
  - Handle empty results and search errors
  - Return list of results with id, title, and url fields
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 7. Implement get_movie_details tool
  - Create async get_movie_details() method in MirCrewClient that performs GET to /viewtopic.php with movie ID
  - Parse HTML response to extract MovieDetails object with all metadata fields
  - Handle invalid movie IDs and missing movies
  - Return structured MovieDetails object
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 8. Implement get_magnet_link tool
  - Create async get_magnet_link() method in MirCrewClient that performs POST like action to movie page
  - Retrieve updated page with GET request to extract revealed magnet link
  - Parse magnet URI from post content and validate format
  - Handle cases where magnet link is not available
  - Return magnet URI string
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 9. Implement FastMCP server setup
  - Create mircrew_mcp/__main__.py as entry point
  - Initialize FastMCP server with name "MirCrew Movie Archive"
  - Register search_movie tool with @mcp.tool() decorator
  - Register get_movie_details tool with @mcp.tool() decorator
  - Register get_magnet_link tool with @mcp.tool() decorator
  - Add tool descriptions and parameter documentation
  - Implement server startup with proper error handling
  - _Requirements: 5.2_

- [x] 10. Test with real data using Mary Poppins
  - Create tests/test_integration.py with end-to-end test
  - Test authentication with real credentials from environment variables
  - Test search_movie with "Mary Poppins" query
  - Test get_movie_details with movie ID from search results
  - Test get_magnet_link with movie ID from search results
  - Verify all tools return expected data formats
  - Clean up any temporary test files after execution
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11. Create comprehensive documentation
  - Create README.md with project overview and features
  - Document installation steps (clone, create venv, install dependencies)
  - Document environment variable configuration (MIRCREW_USERNAME, MIRCREW_PASSWORD)
  - Document MCP server configuration for Q CLI with example mcp.json
  - Document MCP server configuration for Amazon Kiro with example .kiro/settings/mcp.json
  - Document all three tools with parameters and return types
  - Document HTTP interaction flow with example requests for authentication, search, details, and magnet link
  - Add usage examples for each tool
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 8.4_

- [x] 12. Finalize project setup
  - Ensure .gitignore excludes venv/, credentials, __pycache__, *.pyc, .env, and temporary files
  - Verify git repository is properly initialized
  - Verify all dependencies are listed in requirements.txt
  - Verify project can be installed and run as a module (python -m mircrew_mcp)
  - _Requirements: 5.3, 5.4, 8.3_
