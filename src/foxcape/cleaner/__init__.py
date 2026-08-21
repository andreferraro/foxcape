"""
HTML Cleaner module for Foxcape.
"""

from .cleaner import HTMLCleaner, clean_html
from .rules import DEFAULT_RULES, CleanerRules

__all__ = [
    "HTMLCleaner",
    "clean_html",
    "CleanerRules",
    "DEFAULT_RULES",
]
