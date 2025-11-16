# MirCrew MCP Server

A Model Context Protocol (MCP) server that provides programmatic access to the MirCrew movie archive website (https://mircrew-releases.org/). Since MirCrew doesn't offer an official API, this server uses HTTP requests and HTML parsing to interact with the website, providing a clean tool-based interface for MCP clients.

## Features

- **Movie Search**: Search for movies by title in the MirCrew archive
- **Movie Details**: Retrieve comprehensive metadata about specific movies
- **Magnet Links**: Obtain torrent magnet links for movies (includes automatic "like" action)
- **Session Management**: Automatic authentication and session handling
- **MCP Integration**: Compatible with Q CLI and Amazon Kiro

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mircrew-mcp-server
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

The server requires MirCrew credentials to be set as environment variables:

```bash
export MIRCREW_USERNAME="your_username"
export MIRCREW_PASSWORD="your_password"
```

### For Windows:
```cmd
set MIRCREW_USERNAME=your_username
set MIRCREW_PASSWORD=your_password
```

### Using .env file (for local development):
Create a `.env` file in the project root:
```
MIRCREW_USERNAME=your_username
MIRCREW_PASSWORD=your_password
```

**⚠️ Security Note**: Never commit credentials to version control. The `.env` file is excluded by `.gitignore`.

## MCP Server Configuration

### Q CLI Configuration

Create or update your `mcp.json` file:

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

### Amazon Kiro Configuration

Create or update `.kiro/settings/mcp.json`:

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

## Available Tools

### 1. search_movie

Search for movies by title in the MirCrew archive.

**Parameters:**
- `title` (string, required): The movie title to search for

**Returns:**
```json
[
  {
    "id": "12345",
    "title": "Movie Title (Year)",
    "url": "https://mircrew-releases.org/viewtopic.php?t=12345"
  }
]
```

**Usage Example:**
```python
# Search for movies containing "Mary Poppins"
results = await search_movie("Mary Poppins")
```

### 2. get_movie_details

Retrieve detailed information about a specific movie using its ID.

**Parameters:**
- `movie_id` (string, required): The movie ID from search results

**Returns:**
```json
{
  "id": "12345",
  "title": "Movie Title (Year)",
  "url": "https://mircrew-releases.org/viewtopic.php?t=12345",
  "description": "Movie plot and description",
  "year": "2023",
  "genre": "Action, Adventure",
  "quality": "1080p BluRay",
  "size": "2.5 GB",
  "posted_by": "username",
  "posted_date": "2023-01-15",
  "raw_content": "Full post HTML content"
}
```

**Usage Example:**
```python
# Get details for a specific movie
details = await get_movie_details("12345")
```

### 3. get_magnet_link

Obtain the magnet link for a movie. This tool automatically performs a "like" action on the movie to reveal the magnet link.

**Parameters:**
- `movie_id` (string, required): The movie ID from search results

**Returns:**
```json
"magnet:?xt=urn:btih:abcdef1234567890&dn=Movie+Title&tr=..."
```

**Usage Example:**
```python
# Get magnet link for a movie
magnet_link = await get_magnet_link("12345")
```

## HTTP Interaction Flow

The server interacts with MirCrew through a series of HTTP requests. Here's the detailed flow:

### 1. Authentication Flow

```http
# Step 1: Get login form
GET /index.php HTTP/1.1
Host: mircrew-releases.org
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0

# Extract form_token and creation_time from response

# Step 2: Submit login credentials
POST /ucp.php?mode=login HTTP/1.1
Host: mircrew-releases.org
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password&autologin=on&login=Login&redirect=./index.php?&creation_time=1234567890&form_token=abcdef123456

# Response: 302 Redirect with session cookies
Set-Cookie: phpbb3_12hgm_u=12345; path=/; domain=.mircrew-releases.org
Set-Cookie: phpbb3_12hgm_k=abcdef123456; path=/; domain=.mircrew-releases.org  
Set-Cookie: phpbb3_12hgm_sid=session123456; path=/; domain=.mircrew-releases.org
```

### 2. Movie Search Flow

```http
GET /search.php?keywords=Mary+Poppins&sf=titleonly&sr=topics HTTP/1.1
Host: mircrew-releases.org
Cookie: phpbb3_12hgm_sid=session123456; phpbb3_12hgm_u=12345; phpbb3_12hgm_k=abcdef123456
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0

# Response: HTML page with search results
# Parse: <a href="./viewtopic.php?t=12345">Movie Title</a>
```

### 3. Movie Details Flow

```http
GET /viewtopic.php?t=12345 HTTP/1.1
Host: mircrew-releases.org
Cookie: phpbb3_12hgm_sid=session123456; phpbb3_12hgm_u=12345; phpbb3_12hgm_k=abcdef123456
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0

# Response: HTML page with movie details
# Parse post content for metadata and description
```

### 4. Magnet Link Flow

```http
# Step 1: Perform "like" action
POST /viewtopic.php?t=12345 HTTP/1.1
Host: mircrew-releases.org
Cookie: phpbb3_12hgm_sid=session123456; phpbb3_12hgm_u=12345; phpbb3_12hgm_k=abcdef123456
Content-Type: application/x-www-form-urlencoded

# Like action parameters (extracted from page)

# Step 2: Retrieve updated page with magnet link
GET /viewtopic.php?t=12345 HTTP/1.1
Host: mircrew-releases.org
Cookie: phpbb3_12hgm_sid=session123456; phpbb3_12hgm_u=12345; phpbb3_12hgm_k=abcdef123456

# Response: HTML page with revealed magnet link
# Parse: magnet:?xt=urn:btih:...
```

## Usage Examples

### Complete Workflow Example

```python
import asyncio
from mircrew_mcp.client import MirCrewClient

async def main():
    # Initialize client with credentials
    client = MirCrewClient(
        username="your_username",
        password="your_password"
    )
    
    # Authenticate
    await client.authenticate()
    
    # Search for movies
    results = await client.search_movie("Mary Poppins")
    print(f"Found {len(results)} movies")
    
    if results:
        movie_id = results[0].id
        
        # Get detailed information
        details = await client.get_movie_details(movie_id)
        print(f"Title: {details.title}")
        print(f"Year: {details.year}")
        print(f"Genre: {details.genre}")
        
        # Get magnet link
        magnet = await client.get_magnet_link(movie_id)
        print(f"Magnet: {magnet}")

if __name__ == "__main__":
    asyncio.run(main())
```

### MCP Client Usage

Once configured with Q CLI or Kiro, you can use the tools directly:

```
# Search for movies
> search_movie "The Matrix"

# Get movie details  
> get_movie_details "12345"

# Get magnet link
> get_magnet_link "12345"
```

## Running the Server

### Direct Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export MIRCREW_USERNAME="your_username"
export MIRCREW_PASSWORD="your_password"

# Run the server
python -m mircrew_mcp
```

### Testing

Run the integration tests to verify everything works:

```bash
# Set environment variables first
export MIRCREW_USERNAME="your_username"
export MIRCREW_PASSWORD="your_password"

# Run tests
python -m pytest tests/test_integration.py -v
```

## Project Structure

```
mircrew-mcp-server/
├── .git/                    # Git repository
├── .gitignore              # Git ignore rules
├── venv/                   # Virtual environment
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── mircrew_mcp/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # MCP server entry point
│   ├── client.py          # MirCrewClient class
│   ├── models.py          # Data models
│   ├── parser.py          # HTML parsing utilities
│   └── exceptions.py      # Custom exceptions
├── tests/                 # Test files
│   └── test_integration.py # Integration tests
└── har/                   # HAR files for reference
    ├── authentication.har
    ├── get_details.har
    ├── like_and_show_magnet_link.har
    └── title_search.har
```

## Dependencies

- **fastmcp**: MCP protocol implementation
- **httpx**: Async HTTP client
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser backend
- **python-dotenv**: Environment variable loading (for development)

## Error Handling

The server provides clear error messages for common issues:

- **Missing Credentials**: Clear message when environment variables are not set
- **Authentication Failed**: Specific error when login credentials are invalid
- **Movie Not Found**: Informative message when movie ID doesn't exist
- **Network Errors**: Timeout and connection error handling
- **Parsing Errors**: Graceful handling of unexpected HTML structure

## Security Considerations

- Credentials are never hardcoded in source code
- Environment variables are used exclusively for sensitive data
- Session cookies are stored securely in memory only
- All requests use HTTPS with SSL verification
- Input validation prevents injection attacks

## Troubleshooting

### Common Issues

1. **"Missing credentials" error**
   - Ensure `MIRCREW_USERNAME` and `MIRCREW_PASSWORD` environment variables are set
   - Check that credentials are valid on the MirCrew website

2. **"Authentication failed" error**
   - Verify your username and password are correct
   - Check if your account is active on MirCrew

3. **"Connection timeout" error**
   - Check your internet connection
   - Verify MirCrew website is accessible

4. **"Movie not found" error**
   - Ensure the movie ID is valid (numeric)
   - The movie may have been removed from the archive

### Debug Mode

For troubleshooting, you can enable debug logging by setting:

```bash
export PYTHONPATH=.
export MIRCREW_DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is for educational and personal use only. Respect MirCrew's terms of service and use responsibly.

## Disclaimer

This tool is not affiliated with or endorsed by MirCrew. It's an independent implementation for programmatic access to publicly available content. Users are responsible for complying with MirCrew's terms of service and applicable laws.