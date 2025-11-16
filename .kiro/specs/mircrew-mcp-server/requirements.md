# Requirements Document

## Introduction

This feature involves developing a Model Context Protocol (MCP) server that enables programmatic interaction with the MirCrew movie archive website (https://mircrew-releases.org/). Since MirCrew does not provide an official API, the server will use HTTP requests to authenticate, search for movies, retrieve details, interact with content (like), and obtain magnet links. The implementation will use Python with FastMCP framework, analyze captured HAR files to understand the website's interaction patterns, and provide a clean tool-based interface for MCP clients like Q CLI and Amazon Kiro.

## Requirements

### Requirement 1: Authentication System

**User Story:** As an MCP client user, I want the server to authenticate with MirCrew using my credentials, so that I can access protected content and features.

#### Acceptance Criteria

1. WHEN the MCP server starts THEN it SHALL read username and password from environment variables (MIRCREW_USERNAME and MIRCREW_PASSWORD)
2. WHEN authentication is required THEN the server SHALL perform HTTP authentication using the credentials from environment variables
3. IF authentication fails THEN the server SHALL return a clear error message indicating authentication failure
4. WHEN authentication succeeds THEN the server SHALL maintain the session for subsequent requests
5. THE system SHALL analyze the authentication.har file to determine the correct authentication flow and HTTP headers

### Requirement 2: Movie Search Tool

**User Story:** As an MCP client user, I want to search for movies by title, so that I can find specific content in the MirCrew archive.

#### Acceptance Criteria

1. WHEN the user invokes the search tool with a movie title THEN the server SHALL return a list of matching database entries
2. EACH search result SHALL include at minimum an identifier and title
3. THE search functionality SHALL analyze title_search.har to replicate the website's search mechanism
4. IF no results are found THEN the server SHALL return an empty list with appropriate messaging
5. IF the search request fails THEN the server SHALL return a descriptive error message
6. THE search tool SHALL handle special characters and spaces in movie titles correctly

### Requirement 3: Movie Details Retrieval Tool

**User Story:** As an MCP client user, I want to retrieve detailed information about a specific movie using its identifier, so that I can view comprehensive metadata before taking further actions.

#### Acceptance Criteria

1. WHEN the user invokes the details tool with a movie identifier THEN the server SHALL return detailed information about that movie
2. THE details SHALL include all relevant metadata available from the website
3. THE details functionality SHALL analyze get_details.har to replicate the website's detail retrieval mechanism
4. IF the identifier is invalid or not found THEN the server SHALL return an appropriate error message
5. THE returned details SHALL be structured in a clear, parseable format

### Requirement 4: Movie Magnet Link Tool

**User Story:** As an MCP client user, I want to obtain the magnet link for a movie, so that I can download the content using a torrent client.

#### Acceptance Criteria

1. WHEN the user invokes the magnet link tool with a movie identifier THEN the server SHALL perform a "like" action on the movie
2. AFTER the like action completes THEN the server SHALL extract and return the magnet link from the page
3. THE magnet link functionality SHALL analyze like_and_show_magnet_link.har to replicate the website's interaction flow
4. IF the magnet link cannot be obtained THEN the server SHALL return a descriptive error message
5. THE returned magnet link SHALL be in valid magnet URI format
6. THE tool SHALL handle the two-step process (like, then retrieve link) transparently to the user

### Requirement 5: Project Structure and Environment

**User Story:** As a developer, I want a properly structured Python project with dependency management, so that the MCP server can be easily installed and maintained.

#### Acceptance Criteria

1. THE project SHALL use a Python virtual environment located in the venv/ directory
2. THE project SHALL use FastMCP framework for MCP server implementation
3. THE project SHALL include a .gitignore file that excludes virtual environment, credentials, and temporary files
4. THE project SHALL be initialized as a git repository
5. THE project SHALL include a requirements.txt or pyproject.toml file listing all dependencies
6. THE implementation SHALL be simple and essential, avoiding unnecessary complexity

### Requirement 6: Documentation

**User Story:** As a user, I want clear documentation on how to configure and use the MCP server, so that I can integrate it with Q CLI and Amazon Kiro.

#### Acceptance Criteria

1. THE project SHALL include a README.md file with setup instructions
2. THE README SHALL document how to configure the MCP server in Q CLI
3. THE README SHALL document how to configure the MCP server in Amazon Kiro
4. THE README SHALL include instructions for setting MIRCREW_USERNAME and MIRCREW_PASSWORD environment variables
5. THE README SHALL document the HTTP interaction flow with the website including example HTTP calls
6. THE README SHALL list all available tools and their parameters
7. THE documentation SHALL include example usage of each tool

### Requirement 7: Testing and Validation

**User Story:** As a developer, I want the implementation to be tested with real data, so that I can verify it works correctly with the actual MirCrew website.

#### Acceptance Criteria

1. THE implementation SHALL be tested using real HTTP requests to the MirCrew website
2. THE tests SHALL use "Mary Poppins" as the test movie title
3. THE tests SHALL NOT use mocked responses
4. WHEN testing is complete THEN all temporary test files SHALL be cleaned up
5. THE tests SHALL verify all three tools (search, details, magnet link) work end-to-end

### Requirement 8: Security and Configuration

**User Story:** As a user, I want my credentials to be securely managed through environment variables, so that sensitive information is not hardcoded in the source code.

#### Acceptance Criteria

1. THE source code SHALL NOT contain hardcoded usernames or passwords
2. THE system SHALL read credentials exclusively from environment variables
3. THE .gitignore file SHALL prevent credential files from being committed
4. THE MCP server configuration examples SHALL show how to pass environment variables in Q CLI and Kiro
5. IF required environment variables are missing THEN the server SHALL fail with a clear error message indicating which variables are needed
