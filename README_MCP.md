# MirCrew MCP Server

A FastMCP server that provides tools to search and retrieve movie information from the MirCrew archive.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your MirCrew credentials as environment variables:

```bash
export MIRCREW_USERNAME=your_username
export MIRCREW_PASSWORD=your_password
```

## Running the Server

```bash
python -m mircrew_mcp
```

## Available Tools

### 1. search_movie

Search for movies by title in the MirCrew archive.

**Parameters:**
- `title` (string): The movie title to search for

**Returns:**
- List of search results, each containing:
  - `id`: Movie's unique identifier
  - `title`: Movie's title
  - `url`: Full URL to the movie's detail page

**Example:**
```json
{
  "title": "Mary Poppins"
}
```

### 2. get_movie_details

Get detailed information about a specific movie.

**Parameters:**
- `movie_id` (string): The movie's unique identifier from search results

**Returns:**
- Dictionary containing:
  - `id`: Movie's unique identifier
  - `title`: Movie's title
  - `url`: Full URL to the movie's detail page
  - `description`: Movie description or plot summary
  - `year`: Release year (if available)
  - `genre`: Movie genre(s) (if available)
  - `quality`: Video quality (if available)
  - `size`: File size (if available)
  - `posted_by`: Username of the uploader (if available)
  - `posted_date`: Date when posted (if available)
  - `raw_content`: Full post content

**Example:**
```json
{
  "movie_id": "12345"
}
```

### 3. get_magnet_link

Get the magnet link (torrent URI) for a movie.

**Parameters:**
- `movie_id` (string): The movie's unique identifier from search results

**Returns:**
- String containing the magnet URI

**Example:**
```json
{
  "movie_id": "12345"
}
```

## Error Handling

All tools include comprehensive error handling:
- `AuthenticationError`: Credentials are missing or invalid
- `MovieNotFoundError`: Movie ID is invalid or movie doesn't exist
- `NetworkError`: Network communication error
- `ParsingError`: Response parsing error
- `MirCrewError`: Other unexpected errors

## Testing

The server has been tested with real credentials and successfully:
- ✓ Authenticates with MirCrew
- ✓ Searches for movies
- ✓ Retrieves movie details
- ✓ Handles errors gracefully

## Notes

- The server maintains a single authenticated client instance for efficiency
- Authentication is performed automatically on first tool use
- All tools require valid MirCrew credentials to function
