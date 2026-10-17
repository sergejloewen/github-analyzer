class GithubAppError(Exception):
    """
    Base class for exceptions in this module.
    Inherits from the built-in Exception class.
    """
    pass

# Potential exceptions to add:
# parsing error - validation error
# timeout exception - GitHubTimeoutError

class GitHubUserNotFoundError(GithubAppError):
    """Exception raised when a GitHub user is not found or does not exist."""
    pass

class GitHubRateLimitError(GithubAppError):
    """Exception raised when the GitHub API rate limit is exceeded. (HTTP status code 403 or 429)"""
    pass

class GitHubNetworkError(GithubAppError):
    """Exception raised for network-related errors when accessing the GitHub API."""
    pass

class GitHubAPIError(GithubAppError):
    """Exception raised for general GitHub API Errors (HTTP Status codes 5xx or broken/ corrupt json response)"""
    pass