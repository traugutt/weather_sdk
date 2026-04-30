"""Custom exceptions for the Weather SDK."""


class WeatherSDKError(Exception):
    """Base error for all SDK exceptions."""


class APIError(WeatherSDKError):
    """Raised when the upstream API returns an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"API error {status_code}: {message}")


class StorageKeyError(WeatherSDKError):
    """Raised when a requested key does not exist in storage."""


class StorageDuplicateError(WeatherSDKError):
    """Raised when attempting to create a record that already exists."""
