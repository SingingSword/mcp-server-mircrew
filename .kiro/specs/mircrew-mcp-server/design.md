# Design Document

## Overview

The MirCrew MCP Server is a Python-based Model Context Protocol server that provides programmatic access to the MirCrew movie archive website. Since MirCrew doesn't offer an official API, the server uses HTTP requests and HTML parsing to interact with the website. The implementation uses FastMCP framework for MCP protocol handling and maintains session state for authenticated requests.

The server exposes three primary tools:
1. **search_movie** - Search for movies by title
2. **get_movie_details** - Retrieve detailed information about a specific movie
3. **get_magnet_link** - Obtain the magnet link for a movie (includes automatic "like" action)

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  MCP Client     │
│ (Kiro/Q CLI)    │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  FastMCP Server │
│                 │
│  ┌───────────┐  │
│  │  Tools    │  │
│  │  Layer    │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  Session  │  │
│  │  Manager  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │   HTTP    │  │
│  │  Client   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ HTTPS
         │
┌────────▼────────┐
│   MirCrew       │
│   Website       │
└─────────────────┘
```

### Component Layers

1. **MCP Protocol Layer** (FastMCP)
   - Handles MCP protocol communication
   - Tool registration and invocation
   - Parameter validation

2. **Business Logic Layer**
   - Tool implementations
   - Data extraction and parsing
   - Error handling

3. **Session Management Layer**
   - Authentication handling
   - Cookie management
   - Session persistence

4. **HTTP Client Layer**
   - HTTP request execution
   - HTML parsing
   - Response handling

## Components and Interfaces

### 1. MirCrewClient Class

The main client class that encapsulates all interactions with the MirCrew website.

```python
class MirCrewClient:
    """Client for interacting with MirCrew website."""
    
    def __init__(self, username: str, password: str):
        """Initialize client with credentials from environment."""
        
    async def authenticate(self) -> bool:
        """Authenticate with MirCrew and establish session."""
        
    async def search_movie(self, title: str) -> List[MovieSearchResult]:
        """Search for movies by title."""
        
    async def get_movie_details(self, movie_id: str) -> MovieDetails:
        """Get detailed information about a movie."""
        
    async def get_magnet_link(self, movie_id: str) -> str:
        """Like a movie and retrieve its magnet link."""
```

### 2. Session Manager

Handles authentication and session state management.

**Key Responsibilities:**
- Perform initial authentication via POST to `/ucp.php?mode=login`
- Store and manage session cookies (`phpbb3_12hgm_sid`, `phpbb3_12hgm_u`, `phpbb3_12hgm_k`)
- Maintain session across requests
- Handle re-authentication if session expires

**Authentication Flow (from HAR analysis):**
```
POST /ucp.php?mode=login
Content-Type: application/x-www-form-urlencoded

Parameters:
- username: <from env>
- password: <from env>
- autologin: on
- login: Login
- redirect: ./index.php?
- creation_time: <timestamp>
- form_token: <extracted from login page>

Response: 302 redirect with Set-Cookie headers
- phpbb3_12hgm_u: user ID
- phpbb3_12hgm_k: auto-login key
- phpbb3_12hgm_sid: session ID
```

### 3. HTTP Client Wrapper

Wraps `httpx` or `requests` library with MirCrew-specific configurations.

**Features:**
- Async HTTP client (using `httpx.AsyncClient`)
- Automatic cookie handling
- Standard headers (User-Agent, Accept, etc.)
- Connection pooling and keep-alive
- SSL verification

**Standard Headers:**
```python
{
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,it-IT;q=0.8,it;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
}
```

### 4. HTML Parser

Uses BeautifulSoup4 to extract data from HTML responses.

**Parsing Strategies:**
- **Search Results**: Parse search results page for movie listings
  - Extract topic IDs from links (e.g., `/viewtopic.php?t=12345`)
  - Extract titles from topic links
  - Handle pagination if needed
  
- **Movie Details**: Parse movie detail page
  - Extract metadata from post content
  - Parse structured information (year, genre, quality, etc.)
  - Extract description and technical details
  
- **Magnet Links**: Parse post content after "like" action
  - Locate magnet link in hidden/revealed content
  - Validate magnet URI format

### 5. FastMCP Server Setup

```python
from fastmcp import FastMCP

mcp = FastMCP("MirCrew Movie Archive")

@mcp.tool()
async def search_movie(title: str) -> List[dict]:
    """Search for movies by title in MirCrew archive."""
    
@mcp.tool()
async def get_movie_details(movie_id: str) -> dict:
    """Get detailed information about a specific movie."""
    
@mcp.tool()
async def get_magnet_link(movie_id: str) -> str:
    """Get magnet link for a movie (performs like action)."""
```

## Data Models

### MovieSearchResult

```python
@dataclass
class MovieSearchResult:
    """Result from movie search."""
    id: str              # Topic ID (e.g., "12345")
    title: str           # Movie title
    url: str             # Full URL to movie page
```

### MovieDetails

```python
@dataclass
class MovieDetails:
    """Detailed movie information."""
    id: str
    title: str
    url: str
    description: str     # Movie description/plot
    year: Optional[str]
    genre: Optional[str]
    quality: Optional[str]
    size: Optional[str]
    posted_by: Optional[str]
    posted_date: Optional[str]
    raw_content: str     # Full post content for additional parsing
```

### MagnetLink

```python
@dataclass
class MagnetLink:
    """Magnet link information."""
    movie_id: str
    magnet_uri: str      # Full magnet URI
    title: str           # Movie title
```

## Error Handling

### Error Categories

1. **Authentication Errors**
   - Missing credentials (environment variables not set)
   - Invalid credentials (login failed)
   - Session expired (re-authentication needed)

2. **Network Errors**
   - Connection timeout
   - DNS resolution failure
   - SSL/TLS errors

3. **Parsing Errors**
   - Unexpected HTML structure
   - Missing expected elements
   - Invalid data format

4. **Business Logic Errors**
   - Movie not found
   - Search returned no results
   - Magnet link not available

### Error Handling Strategy

```python
class MirCrewError(Exception):
    """Base exception for MirCrew client errors."""

class AuthenticationError(MirCrewError):
    """Authentication failed or credentials invalid."""

class MovieNotFoundError(MirCrewError):
    """Requested movie not found."""

class ParsingError(MirCrewError):
    """Failed to parse website response."""

class NetworkError(MirCrewError):
    """Network communication error."""
```

**Error Response Format:**
```python
{
    "error": "error_type",
    "message": "Human-readable error message",
    "details": {}  # Optional additional context
}
```

## Website Interaction Flow

### 1. Authentication Flow

```
Step 1: GET /index.php
  → Extract form_token and creation_time from login form

Step 2: POST /ucp.php?mode=login
  Headers:
    Content-Type: application/x-www-form-urlencoded
  Body:
    username=<USERNAME>
    password=<PASSWORD>
    autologin=on
    login=Login
    redirect=./index.php?
    creation_time=<TIMESTAMP>
    form_token=<TOKEN>
  
  Response: 302 Redirect
    Set-Cookie: phpbb3_12hgm_u=<USER_ID>
    Set-Cookie: phpbb3_12hgm_k=<AUTO_LOGIN_KEY>
    Set-Cookie: phpbb3_12hgm_sid=<SESSION_ID>

Step 3: Follow redirect to /index.php?&sid=<SESSION_ID>
  → Verify authentication successful
```

### 2. Search Flow

```
GET /search.php?keywords=<TITLE>&sf=titleonly&sr=topics
  Headers:
    Cookie: phpbb3_12hgm_sid=<SESSION_ID>; phpbb3_12hgm_u=<USER_ID>; phpbb3_12hgm_k=<KEY>
  
  Response: 200 OK
    HTML page with search results
    
Parse HTML:
  - Find all topic links: <a href="./viewtopic.php?t=<ID>">
  - Extract topic ID from URL
  - Extract title from link text
```

### 3. Get Details Flow

```
GET /viewtopic.php?t=<MOVIE_ID>
  Headers:
    Cookie: phpbb3_12hgm_sid=<SESSION_ID>; phpbb3_12hgm_u=<USER_ID>; phpbb3_12hgm_k=<KEY>
  
  Response: 200 OK
    HTML page with movie details
    
Parse HTML:
  - Extract post content from first post
  - Parse structured data (year, genre, quality, etc.)
  - Extract description
```

### 4. Get Magnet Link Flow

```
Step 1: POST /viewtopic.php?t=<MOVIE_ID> (Like action)
  Headers:
    Cookie: phpbb3_12hgm_sid=<SESSION_ID>; phpbb3_12hgm_u=<USER_ID>; phpbb3_12hgm_k=<KEY>
  Body:
    <like_action_parameters>
  
  Response: 200 OK or redirect

Step 2: GET /viewtopic.php?t=<MOVIE_ID> (Retrieve updated page)
  Headers:
    Cookie: phpbb3_12hgm_sid=<SESSION_ID>; phpbb3_12hgm_u=<USER_ID>; phpbb3_12hgm_k=<KEY>
  
  Response: 200 OK
    HTML page with revealed magnet link
    
Parse HTML:
  - Find magnet link in post content
  - Extract magnet URI (starts with "magnet:?")
  - Validate format
```

## Testing Strategy

### Test Approach

Since the requirement specifies testing with REAL DATA and NO MOCKING, the testing strategy focuses on integration testing against the actual MirCrew website.

### Test Cases

1. **Authentication Test**
   - Verify successful login with valid credentials
   - Verify session cookies are stored
   - Verify authenticated requests work

2. **Search Test**
   - Search for "Mary Poppins"
   - Verify results are returned
   - Verify each result has id and title
   - Verify URLs are properly formatted

3. **Get Details Test**
   - Use movie ID from search results
   - Retrieve movie details
   - Verify all expected fields are present
   - Verify data is properly parsed

4. **Get Magnet Link Test**
   - Use movie ID from search results
   - Perform like action
   - Retrieve magnet link
   - Verify magnet URI format (starts with "magnet:?")

5. **End-to-End Test**
   - Complete flow: authenticate → search → get details → get magnet
   - Use "Mary Poppins" as test case
   - Verify all steps complete successfully

### Test Execution

```python
# test_mircrew.py
import asyncio
import os

async def test_full_workflow():
    """Test complete workflow with Mary Poppins."""
    client = MirCrewClient(
        username=os.getenv("MIRCREW_USERNAME"),
        password=os.getenv("MIRCREW_PASSWORD")
    )
    
    # Authenticate
    await client.authenticate()
    
    # Search
    results = await client.search_movie("Mary Poppins")
    assert len(results) > 0
    
    # Get details
    movie_id = results[0].id
    details = await client.get_movie_details(movie_id)
    assert details.title
    
    # Get magnet link
    magnet = await client.get_magnet_link(movie_id)
    assert magnet.startswith("magnet:?")
    
    print("✓ All tests passed")
```

### Test Cleanup

After testing:
- Remove any temporary test files
- Clear test logs
- Do not commit test output or credentials

## Security Considerations

1. **Credential Management**
   - Never hardcode credentials
   - Read from environment variables only
   - Validate environment variables at startup
   - Clear error messages when credentials missing

2. **Session Security**
   - Store session cookies securely in memory only
   - Don't log sensitive cookie values
   - Handle session expiration gracefully

3. **Input Validation**
   - Sanitize search queries
   - Validate movie IDs (numeric format)
   - Prevent injection attacks

4. **HTTPS Only**
   - All requests use HTTPS
   - Verify SSL certificates
   - No fallback to HTTP

## Configuration

### Environment Variables

```bash
# Required
MIRCREW_USERNAME=<your_username>
MIRCREW_PASSWORD=<your_password>

# Optional
MIRCREW_TIMEOUT=30  # Request timeout in seconds
MIRCREW_MAX_RETRIES=3  # Max retry attempts
```

### MCP Server Configuration

**For Q CLI (mcp.json):**
```json
{
  "mcpServers": {
    "mircrew": {
      "command": "python",
      "args": ["-m", "mircrew_mcp"],
      "cwd": "/path/to/mircrew-mcp-server",
      "env": {
        "MIRCREW_USERNAME": "your_username",
        "MIRCREW_PASSWORD": "your_password"
      }
    }
  }
}
```

**For Amazon Kiro (.kiro/settings/mcp.json):**
```json
{
  "mcpServers": {
    "mircrew": {
      "command": "python",
      "args": ["-m", "mircrew_mcp"],
      "cwd": "/path/to/mircrew-mcp-server",
      "env": {
        "MIRCREW_USERNAME": "your_username",
        "MIRCREW_PASSWORD": "your_password"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Implementation Notes

### Dependencies

```
fastmcp>=0.1.0
httpx>=0.25.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0  # For local testing
```

### Project Structure

```
mircrew-mcp-server/
├── .git/
├── .gitignore
├── venv/
├── README.md
├── requirements.txt
├── mircrew_mcp/
│   ├── __init__.py
│   ├── __main__.py      # Entry point
│   ├── client.py        # MirCrewClient class
│   ├── models.py        # Data models
│   ├── parser.py        # HTML parsing utilities
│   └── exceptions.py    # Custom exceptions
└── tests/
    └── test_integration.py
```

### Simplicity Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Minimal Dependencies**: Only essential libraries
3. **Direct Implementation**: No over-engineering or unnecessary abstractions
4. **Clear Error Messages**: Easy to debug and troubleshoot
5. **Straightforward Flow**: Linear execution paths where possible

## Future Considerations

While keeping the initial implementation simple, these could be considered for future enhancements:

- Caching search results to reduce requests
- Rate limiting to be respectful to the website
- Batch operations for multiple movies
- Advanced search filters
- Download progress tracking
- Retry logic with exponential backoff

However, these are explicitly OUT OF SCOPE for the initial implementation to maintain simplicity.
