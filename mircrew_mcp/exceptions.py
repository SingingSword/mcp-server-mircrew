"""Custom exceptions for MirCrew MCP server."""


class MirCrewError(Exception):
    """Base exception for MirCrew client errors."""
    pass


class AuthenticationError(MirCrewError):
    """Authentication failed or credentials invalid."""
    pass


class MovieNotFoundError(MirCrewError):
    """Requested movie not found."""
    pass


class ParsingError(MirCrewError):
    """Failed to parse website response."""
    pass


class NetworkError(MirCrewError):
    """Network communication error."""
    pass
