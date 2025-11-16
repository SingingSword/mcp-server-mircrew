"""MirCrew client for interacting with the website."""

import os
import re
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

from .models import MovieSearchResult, MovieDetails, MagnetLink
from .exceptions import (
    AuthenticationError,
    MovieNotFoundError,
    ParsingError,
    NetworkError,
    MirCrewError
)


class MirCrewClient:
    """Client for interacting with MirCrew website."""
    
    BASE_URL = "https://mircrew-releases.org"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize client with credentials from environment.
        
        Args:
            username: MirCrew username (defaults to MIRCREW_USERNAME env var)
            password: MirCrew password (defaults to MIRCREW_PASSWORD env var)
            
        Raises:
            AuthenticationError: If credentials are not provided
        """
        self.username = username or os.getenv("MIRCREW_USERNAME")
        self.password = password or os.getenv("MIRCREW_PASSWORD")
        
        if not self.username or not self.password:
            raise AuthenticationError(
                "Missing credentials. Please set MIRCREW_USERNAME and MIRCREW_PASSWORD "
                "environment variables or provide them to the constructor."
            )
        
        # Initialize HTTP client with standard headers and automatic cookie handling
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,it-IT;q=0.8,it;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
            },
            follow_redirects=True,
            timeout=30.0,
            verify=True,  # SSL verification enabled
            # Connection pooling is handled automatically by httpx.AsyncClient
            # with default limits (max_connections=100, max_keepalive_connections=20)
        )
        
        # Session cookies
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.autologin_key: Optional[str] = None
        self.authenticated = False
    
    async def authenticate(self) -> bool:
        """
        Authenticate with MirCrew and establish session.
        
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
            NetworkError: If network communication fails
        """
        try:
            # Step 1: GET the login page to extract form tokens
            login_page_url = f"{self.BASE_URL}/index.php"
            response = await self.client.get(login_page_url)
            response.raise_for_status()
            
            # Parse the login form to extract tokens
            soup = BeautifulSoup(response.text, "lxml")
            form_token = None
            creation_time = None
            
            # Find form token
            form_token_input = soup.find("input", {"name": "form_token"})
            if form_token_input:
                form_token = form_token_input.get("value")
            
            # Find creation time
            creation_time_input = soup.find("input", {"name": "creation_time"})
            if creation_time_input:
                creation_time = creation_time_input.get("value")
            
            if not form_token or not creation_time:
                raise AuthenticationError(
                    "Failed to extract form tokens from login page. "
                    "The website structure may have changed."
                )
            
            # Extract the form action URL which includes the session ID
            login_form = soup.find("form", {"action": re.compile(r"ucp\.php\?mode=login")})
            if not login_form:
                raise AuthenticationError("Login form not found on the page")
            
            form_action = login_form.get("action", "")
            if form_action.startswith("./"):
                form_action = form_action[2:]
            login_url = f"{self.BASE_URL}/{form_action}"
            
            # Step 2: POST to login endpoint with credentials
            login_data = {
                "username": self.username,
                "password": self.password,
                "autologin": "on",
                "login": "Login",
                "redirect": "./index.php?",
                "creation_time": creation_time,
                "form_token": form_token
            }
            
            login_response = await self.client.post(
                login_url,
                data=login_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": self.BASE_URL + "/"
                }
            )
            
            # Step 3: Extract session cookies from client cookie jar
            # httpx.AsyncClient automatically stores cookies in its cookie jar
            self.session_id = self.client.cookies.get("phpbb3_12hgm_sid")
            self.user_id = self.client.cookies.get("phpbb3_12hgm_u")
            self.autologin_key = self.client.cookies.get("phpbb3_12hgm_k")
            
            # Verify authentication was successful
            # httpx automatically follows redirects and manages cookies
            # A successful login will have user_id != "1" (anonymous user)
            if not self.session_id or not self.user_id or self.user_id == "1":
                raise AuthenticationError(
                    "Authentication failed. Please check your credentials."
                )
            
            # For successful authentication, we should have been redirected
            # and the response should contain user-specific content
            self.authenticated = True
            return True
                
        except httpx.HTTPError as e:
            raise NetworkError(f"Network error during authentication: {str(e)}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, NetworkError)):
                raise
            raise MirCrewError(f"Unexpected error during authentication: {str(e)}")
    
    def _get_auth_cookies(self) -> dict:
        """
        Get authentication cookies for authenticated requests.
        
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        if self.session_id:
            cookies["phpbb3_12hgm_sid"] = self.session_id
        if self.user_id:
            cookies["phpbb3_12hgm_u"] = self.user_id
        if self.autologin_key:
            cookies["phpbb3_12hgm_k"] = self.autologin_key
        return cookies
    
    async def _authenticated_get(self, url: str, **kwargs) -> httpx.Response:
        """
        Perform authenticated GET request with automatic cookie handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to httpx.get()
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network communication fails
        """
        if not self.authenticated:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")
        
        try:
            # Merge authentication cookies with any provided cookies
            cookies = self._get_auth_cookies()
            if "cookies" in kwargs:
                cookies.update(kwargs["cookies"])
            kwargs["cookies"] = cookies
            
            response = await self.client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            raise NetworkError(f"Network error during GET request: {str(e)}")
    
    async def _authenticated_post(self, url: str, **kwargs) -> httpx.Response:
        """
        Perform authenticated POST request with automatic cookie handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to httpx.post()
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network communication fails
        """
        if not self.authenticated:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")
        
        try:
            # Merge authentication cookies with any provided cookies
            cookies = self._get_auth_cookies()
            if "cookies" in kwargs:
                cookies.update(kwargs["cookies"])
            kwargs["cookies"] = cookies
            
            response = await self.client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            raise NetworkError(f"Network error during POST request: {str(e)}")
    
    async def search_movie(self, title: str) -> List[MovieSearchResult]:
        """
        Search for movies by title.
        
        Args:
            title: Movie title to search for
            
        Returns:
            List of MovieSearchResult objects (empty list if no results)
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network communication fails
            ParsingError: If response parsing fails
        """
        if not title or not title.strip():
            return []
        
        try:
            # Perform GET request to search endpoint
            # Using sf=titleonly to search only in titles, sr=topics to search topics
            search_url = f"{self.BASE_URL}/search.php"
            params = {
                "keywords": title.strip(),
                "sf": "titleonly",
                "sr": "topics"
            }
            
            response = await self._authenticated_get(search_url, params=params)
            
            # Parse HTML response to extract search results
            from .parser import parse_search_results
            results = parse_search_results(response.text, self.BASE_URL)
            
            return results
            
        except (AuthenticationError, NetworkError, ParsingError):
            raise
        except Exception as e:
            raise MirCrewError(f"Unexpected error during movie search: {str(e)}")
    
    async def get_movie_details(self, movie_id: str) -> MovieDetails:
        """
        Get detailed information about a movie.
        
        Args:
            movie_id: Movie/topic ID
            
        Returns:
            MovieDetails object with all metadata fields
            
        Raises:
            AuthenticationError: If not authenticated
            MovieNotFoundError: If movie ID is invalid or movie not found
            NetworkError: If network communication fails
            ParsingError: If response parsing fails
        """
        if not movie_id or not movie_id.strip():
            raise MovieNotFoundError("Movie ID cannot be empty")
        
        # Validate movie ID is numeric
        if not movie_id.strip().isdigit():
            raise MovieNotFoundError(f"Invalid movie ID: {movie_id}. Movie ID must be numeric.")
        
        try:
            # Perform GET request to movie detail page
            detail_url = f"{self.BASE_URL}/viewtopic.php"
            params = {"t": movie_id.strip()}
            
            response = await self._authenticated_get(detail_url, params=params)
            
            # Check if the page indicates movie not found
            # phpBB typically shows "The requested topic does not exist" or similar
            if "does not exist" in response.text.lower() or "not found" in response.text.lower():
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
            
            # Parse HTML response to extract movie details
            from .parser import parse_movie_details
            details = parse_movie_details(response.text, movie_id.strip(), self.BASE_URL)
            
            # Verify we got meaningful data
            if not details.title:
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found or has no title")
            
            return details
            
        except MovieNotFoundError:
            raise
        except (AuthenticationError, ParsingError):
            raise
        except NetworkError as e:
            # Check if this is a 404 error disguised as NetworkError
            if "404" in str(e) or "not found" in str(e).lower():
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
            raise NetworkError(f"HTTP error during movie details retrieval: {str(e)}")
        except Exception as e:
            raise MirCrewError(f"Unexpected error during movie details retrieval: {str(e)}")
    
    async def get_magnet_link(self, movie_id: str) -> str:
        """
        Get magnet link for a movie (performs like action to reveal link).
        
        Args:
            movie_id: Movie/topic ID
            
        Returns:
            Magnet URI string
            
        Raises:
            AuthenticationError: If not authenticated
            MovieNotFoundError: If movie ID is invalid or movie not found
            NetworkError: If network communication fails
            ParsingError: If magnet link not found or parsing fails
        """
        if not movie_id or not movie_id.strip():
            raise MovieNotFoundError("Movie ID cannot be empty")
        
        # Validate movie ID is numeric
        if not movie_id.strip().isdigit():
            raise MovieNotFoundError(f"Invalid movie ID: {movie_id}. Movie ID must be numeric.")
        
        try:
            movie_id = movie_id.strip()
            topic_url = f"{self.BASE_URL}/viewtopic.php"
            
            # Step 1: Get the movie page to extract like action parameters
            # We need to find the like button/form to get the correct parameters
            try:
                response = await self._authenticated_get(topic_url, params={"t": movie_id})
            except NetworkError as e:
                # Check if this is a 404 error (movie not found)
                if "404" in str(e) or "not found" in str(e).lower():
                    raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
                raise
            
            # Check if the page indicates movie not found
            if "does not exist" in response.text.lower() or "not found" in response.text.lower():
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
            
            # Parse the page to find the "thanks" link
            soup = BeautifulSoup(response.text, "lxml")
            
            # Look for the "thanks" link with thumbs-up icon
            # Pattern: <a id='lnk_thanks_post...' href="./viewtopic.php?...&thanks=...">
            thanks_link = soup.find("a", {"id": re.compile(r"lnk_thanks_post\d+")})
            
            # Step 2: Perform the thanks action to reveal magnet link
            if thanks_link and thanks_link.get("href"):
                href = thanks_link.get("href")
                if not href.startswith("http"):
                    # Convert relative URL to absolute
                    if href.startswith("./"):
                        href = href[2:]
                    href = f"{self.BASE_URL}/{href}"
                
                # Click the thanks link
                cookies = self._get_auth_cookies()
                await self.client.get(href, cookies=cookies)
            else:
                # If no thanks link found, the magnet link might already be visible
                # or the page structure has changed
                pass
            
            # Step 3: Retrieve the updated page to get the revealed magnet link
            try:
                response = await self._authenticated_get(topic_url, params={"t": movie_id})
            except NetworkError as e:
                # Check if this is a 404 error (movie not found)
                if "404" in str(e) or "not found" in str(e).lower():
                    raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
                raise
            
            # Step 4: Parse the magnet link from the page
            from .parser import parse_magnet_link
            magnet_uri = parse_magnet_link(response.text)
            
            # Validate magnet URI format
            if not magnet_uri.startswith("magnet:?"):
                raise ParsingError(f"Invalid magnet URI format: {magnet_uri}")
            
            return magnet_uri
            
        except MovieNotFoundError:
            raise
        except (AuthenticationError, NetworkError, ParsingError):
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
            raise NetworkError(f"HTTP error during magnet link retrieval: {str(e)}")
        except Exception as e:
            raise MirCrewError(f"Unexpected error during magnet link retrieval: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
