"""Foxcape public exceptions."""


class FoxcapeError(Exception):
    """Base exception for Foxcape library errors."""


class BrowserStartupError(FoxcapeError):
    """Raised when the Camoufox browser or page context fails to start."""
