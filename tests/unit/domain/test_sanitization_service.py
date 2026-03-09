"""Unit tests for SanitizationService."""

from src.domain.services.sanitization_service import SanitizationService


class TestSanitizationService:
    """Tests for domain-level sanitization helpers."""

    def test_sanitize_filename_empty_returns_default(self):
        assert SanitizationService.sanitize_filename("") == "upload.txt"

    def test_sanitize_filename_removes_path_parts_and_invalid_chars(self):
        filename = "..\\..\\unsafe folder\\evil?.txt"
        sanitized = SanitizationService.sanitize_filename(filename)

        assert sanitized == "evil_.txt"
        assert ".." not in sanitized
        assert "\\" not in sanitized
        assert "/" not in sanitized

    def test_sanitize_filename_fallback_when_result_is_empty(self):
        assert SanitizationService.sanitize_filename("...") == "upload.txt"

    def test_sanitize_sample_name_valid(self):
        is_valid, sanitized, error = SanitizationService.sanitize_sample_name("Sample_1-A.2")

        assert is_valid
        assert sanitized == "Sample_1-A.2"
        assert error == ""

    def test_sanitize_sample_name_invalid_chars(self):
        is_valid, sanitized, error = SanitizationService.sanitize_sample_name("<script>")

        assert not is_valid
        assert sanitized == "&lt;script&gt;"
        assert "invalid characters" in error

    def test_sanitize_sample_name_empty(self):
        is_valid, sanitized, error = SanitizationService.sanitize_sample_name("   ")

        assert not is_valid
        assert sanitized == ""
        assert "cannot be empty" in error

    def test_escape_html(self):
        text = "<b>unsafe & text</b>"
        escaped = SanitizationService.escape_html(text)

        assert escaped == "&lt;b&gt;unsafe &amp; text&lt;/b&gt;"

    def test_validate_path_safety_rejects_traversal(self):
        assert not SanitizationService.validate_path_safety("../etc/passwd")

    def test_validate_path_safety_rejects_absolute_windows_path(self):
        assert not SanitizationService.validate_path_safety("C:\\Windows\\System32\\drivers")

    def test_validate_path_safety_allows_safe_relative_path(self):
        assert SanitizationService.validate_path_safety("data/uploads/file.txt")
