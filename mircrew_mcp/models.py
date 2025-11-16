"""Data models for MirCrew MCP server."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MovieSearchResult:
    """Result from movie search."""
    id: str              # Topic ID (e.g., "12345")
    title: str           # Movie title
    url: str             # Full URL to movie page


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


@dataclass
class MagnetLink:
    """Magnet link information."""
    movie_id: str
    magnet_uri: str      # Full magnet URI
    title: str           # Movie title
