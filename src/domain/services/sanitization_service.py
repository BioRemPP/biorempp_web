"""
Sanitization Service.

Domain service for input sanitization and security.

This module provides comprehensive input sanitization to prevent common
security vulnerabilities such as XSS, path traversal, and injection attacks.

Classes
-------
SanitizationService
    Static methods for sanitizing various types of user input

Notes
-----
All methods are static and can be called directly from the class.
Methods use logging for security event tracking.
"""

import html
import logging
import re
from pathlib import Path
from typing import Tuple

from src.shared.logging import get_logger, log_execution

logger = get_logger(__name__)


class SanitizationService:
    """
    Domain service for input sanitization.

    Provides methods to sanitize user inputs and prevent common
    security vulnerabilities (XSS, path traversal, injection).

    Notes
    -----
    This is a Domain Service following Clean Architecture principles.
    All methods are static and stateless.
    """

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.

        Removes path components and restricts characters to alphanumeric,
        underscore, dash, and dot only.

        Parameters
        ----------
        filename : str
            Original filename from upload

        Returns
        -------
        str
            Sanitized filename (basename only, safe characters)

        Notes
        -----
        - Removes path components (../, /)
        - Allows only alphanumeric, underscore, dash, dot
        - Falls back to 'upload.txt' if empty after sanitization
        """
        if not filename:
            logger.warning("Empty filename provided, using default")
            return "upload.txt"

        original_filename = filename
        filename = Path(filename).name
        sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
        sanitized = re.sub(r"_{2,}", "_", sanitized)
        sanitized = re.sub(r"\.{2,}", ".", sanitized)
        sanitized = sanitized.strip("_.")

        if not sanitized or sanitized == ".":
            logger.warning(
                "Filename sanitization resulted in empty string",
                extra={"original_filename": original_filename},
            )
            return "upload.txt"

        if sanitized != original_filename:
            logger.info(
                f"Filename sanitized: '{original_filename}' → '{sanitized}'",
                extra={"original": original_filename, "sanitized": sanitized},
            )

        return sanitized

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def sanitize_sample_name(name: str) -> Tuple[bool, str, str]:
        """
        Sanitize and validate sample name.

        Parameters
        ----------
        name : str
            Original sample name from input

        Returns
        -------
        Tuple[bool, str, str]
            Tuple (is_valid, sanitized_name, error_message)

        Notes
        -----
        - HTML-escapes the name for safe display (prevents XSS)
        - Validates against allowed pattern
        """
        if not name or not name.strip():
            logger.warning("Empty sample name provided")
            return False, "", "Sample name cannot be empty"

        name = name.strip()
        escaped = html.escape(name)
        allowed_pattern = r"^[a-zA-Z0-9_\-\.]+$"

        if not re.match(allowed_pattern, name):
            logger.warning(
                f"Sample name contains invalid characters: '{name}'",
                extra={"sample_name": name},
            )
            return (
                False,
                escaped,
                f"Sample name contains invalid characters. Allowed: letters, numbers, _, -, .",
            )

        logger.debug(f"Sample name validated successfully: '{name}'")
        return True, escaped, ""

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def escape_html(text: str) -> str:
        """
        Escape HTML special characters to prevent XSS attacks.

        Parameters
        ----------
        text : str
            Text to escape

        Returns
        -------
        str
            HTML-escaped text

        Notes
        -----
        Uses Python's built-in html.escape() function.
        Escapes: <, >, &, ", '
        """
        return html.escape(text)

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_path_safety(path: str) -> bool:
        """
        Check if path is safe (no traversal attempts).

        Parameters
        ----------
        path : str
            Path to validate

        Returns
        -------
        bool
            True if path is safe, False if dangerous patterns detected

        Notes
        -----
        Dangerous patterns detected:
        - Path traversal: .., /../, ..\\
        - Absolute Unix/Windows paths
        - Logs security events for detected attacks
        """
        dangerous_patterns = [
            "..",
            "/..",
            "../",
            "\\..\\",
            "/etc/",
            "/usr/",
            "/root/",
            "/var/",
            "/tmp/",
            "C:\\",
            "C:/",
            "D:\\",
            "D:/",
        ]

        path_lower = path.lower()

        for pattern in dangerous_patterns:
            if pattern.lower() in path_lower:
                logger.error(
                    f"Path traversal/absolute path attempt detected: '{path}'",
                    extra={"path": path, "pattern": pattern},
                )
                return False

        logger.debug(f"Path safety check passed: '{path}'")
        return True
