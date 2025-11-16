"""HTML parsing utilities for MirCrew website."""

import re
from typing import List, Optional
from bs4 import BeautifulSoup

from .models import MovieSearchResult, MovieDetails
from .exceptions import ParsingError


def parse_search_results(html: str, base_url: str) -> List[MovieSearchResult]:
    """
    Parse search results page to extract movie listings.
    
    Args:
        html: HTML content of search results page
        base_url: Base URL of the website
        
    Returns:
        List of MovieSearchResult objects
        
    Raises:
        ParsingError: If parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        results = []
        
        # Find all topic links in search results
        # phpBB search results typically have links like: ./viewtopic.php?t=12345
        topic_links = soup.find_all("a", href=re.compile(r"\.?/viewtopic\.php\?t=\d+"))
        
        for link in topic_links:
            href = link.get("href", "")
            
            # Extract topic ID from URL
            match = re.search(r"[?&]t=(\d+)", href)
            if not match:
                continue
            
            topic_id = match.group(1)
            title = link.get_text(strip=True)
            
            # Skip empty titles
            if not title:
                continue
            
            # Build full URL
            if href.startswith("./"):
                href = href[2:]
            if not href.startswith("http"):
                url = f"{base_url}/{href}"
            else:
                url = href
            
            # Avoid duplicates (same topic ID)
            if not any(r.id == topic_id for r in results):
                results.append(MovieSearchResult(
                    id=topic_id,
                    title=title,
                    url=url
                ))
        
        return results
        
    except Exception as e:
        raise ParsingError(f"Failed to parse search results: {str(e)}")


def parse_movie_details(html: str, movie_id: str, base_url: str) -> MovieDetails:
    """
    Parse movie detail page to extract metadata.
    
    Args:
        html: HTML content of movie detail page
        movie_id: Movie/topic ID
        base_url: Base URL of the website
        
    Returns:
        MovieDetails object
        
    Raises:
        ParsingError: If parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Extract title from page title or h2 tag
        title = ""
        title_tag = soup.find("h2", class_=re.compile(r"topic-title"))
        if title_tag:
            title_link = title_tag.find("a")
            title = title_link.get_text(strip=True) if title_link else title_tag.get_text(strip=True)
        
        if not title:
            # Fallback: try to get from page title
            page_title = soup.find("title")
            if page_title:
                title = page_title.get_text(strip=True)
                # Remove common suffixes like " - MirCrew"
                title = re.sub(r"\s*-\s*MirCrew.*$", "", title)
        
        # Extract post content (first post contains movie details)
        post_content = soup.find("div", class_=re.compile(r"content"))
        if not post_content:
            # Alternative: look for post body
            post_content = soup.find("div", class_="postbody")
        
        raw_content = post_content.get_text(strip=True) if post_content else ""
        
        # Extract metadata from post content
        year = _extract_field(raw_content, r"(?:Anno|Year):\s*(\d{4})")
        genre = _extract_field(raw_content, r"(?:Genere|Genre):\s*([^\n]+)")
        quality = _extract_field(raw_content, r"(?:Qualità|Quality):\s*([^\n]+)")
        size = _extract_field(raw_content, r"(?:Dimensione|Size):\s*([^\n]+)")
        
        # Extract poster information
        posted_by = None
        posted_date = None
        author_tag = soup.find("p", class_="author")
        if author_tag:
            author_link = author_tag.find("a", class_=re.compile(r"username"))
            if author_link:
                posted_by = author_link.get_text(strip=True)
            
            # Extract date
            date_text = author_tag.get_text()
            date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", date_text)
            if date_match:
                posted_date = date_match.group(1)
        
        # Extract description (usually the first paragraph or text block)
        description = ""
        if post_content:
            # Try to find description in paragraphs
            paragraphs = post_content.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Skip short lines that are likely metadata
                if len(text) > 50:
                    description = text
                    break
            
            # If no good paragraph found, use first chunk of text
            if not description:
                text_parts = raw_content.split("\n")
                for part in text_parts:
                    part = part.strip()
                    if len(part) > 50:
                        description = part
                        break
        
        url = f"{base_url}/viewtopic.php?t={movie_id}"
        
        return MovieDetails(
            id=movie_id,
            title=title,
            url=url,
            description=description,
            year=year,
            genre=genre,
            quality=quality,
            size=size,
            posted_by=posted_by,
            posted_date=posted_date,
            raw_content=raw_content
        )
        
    except Exception as e:
        raise ParsingError(f"Failed to parse movie details: {str(e)}")


def parse_magnet_link(html: str) -> str:
    """
    Parse movie page to extract magnet link.
    
    Args:
        html: HTML content of movie page (after like action)
        
    Returns:
        Magnet URI string
        
    Raises:
        ParsingError: If magnet link not found or parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Look for magnet links in the page
        # Magnet links typically appear as: <a href="magnet:?xt=urn:btih:...">
        magnet_link = soup.find("a", href=re.compile(r"^magnet:\?"))
        
        if magnet_link:
            magnet_uri = magnet_link.get("href", "")
            if magnet_uri.startswith("magnet:?"):
                return magnet_uri
        
        # Alternative: search for magnet URI in text content
        # Sometimes magnet links are in plain text or code blocks
        text_content = soup.get_text()
        magnet_match = re.search(r"(magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^\s]*)", text_content)
        if magnet_match:
            return magnet_match.group(1)
        
        # If still not found, look in all links and text more broadly
        all_links = soup.find_all("a")
        for link in all_links:
            href = link.get("href", "")
            if "magnet:" in href:
                # Extract just the magnet part
                magnet_match = re.search(r"(magnet:\?[^\s\"'<>]+)", href)
                if magnet_match:
                    return magnet_match.group(1)
        
        raise ParsingError(
            "Magnet link not found in page. "
            "The movie may not have a magnet link available, "
            "or the like action may not have been performed correctly."
        )
        
    except ParsingError:
        raise
    except Exception as e:
        raise ParsingError(f"Failed to parse magnet link: {str(e)}")


def _extract_field(text: str, pattern: str) -> Optional[str]:
    """
    Extract a field from text using regex pattern.
    
    Args:
        text: Text to search
        pattern: Regex pattern with one capture group
        
    Returns:
        Extracted value or None if not found
    """
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        value = match.group(1).strip()
        # Clean up common artifacts
        value = re.sub(r"\s+", " ", value)  # Normalize whitespace
        return value if value else None
    return None
