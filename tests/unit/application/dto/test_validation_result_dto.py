"""
Unit tests for ValidationResultDTO.

This module tests the ValidationResultDTO immutable data transfer object,
which encapsulates validation results with errors and warnings.

Test Categories:
- Initialization: Test DTO creation with various scenarios
- Validation: Test __post_init__ validation logic
- Error/Warning Checking: Test has_errors() and has_warnings()
- Counting: Test error_count() and warning_count()
- Immutability: Test frozen dataclass behavior
- Edge Cases: Test boundary conditions
- Typical Use Cases: Test real-world validation scenarios
"""

import pytest

from src.application.dto.validation_result_dto import ValidationResultDTO


# ============================================================================
# INITIALIZATION TESTS - VALID CASES
# ============================================================================

class TestValidationResultDTOValidInitialization:
    """Test ValidationResultDTO initialization for valid cases."""

    def test_initialization_valid_no_errors_or_warnings(self):
        """Test successful validation with no errors or warnings."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=10,
            message="All validations passed"
        )

        assert dto.is_valid is True
        assert dto.errors is None
        assert dto.warnings is None
        assert dto.validated_items == 10
        assert dto.message == "All validations passed"

    def test_initialization_valid_with_warnings_only(self):
        """Test valid case with warnings but no errors."""
        warnings = ["Warning: Low KO count in Sample1"]

        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=warnings,
            validated_items=5,
            message="Valid with warnings"
        )

        assert dto.is_valid is True
        assert dto.errors is None
        assert dto.warnings == warnings
        assert dto.validated_items == 5

    def test_initialization_valid_with_empty_lists(self):
        """Test valid case with empty error and warning lists."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=[],
            warnings=[],
            validated_items=3
        )

        assert dto.is_valid is True
        assert dto.errors == []
        assert dto.warnings == []

    def test_initialization_valid_with_zero_items(self):
        """Test valid case with zero validated items."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=0,
            message="No items to validate"
        )

        assert dto.validated_items == 0

    def test_initialization_default_message(self):
        """Test that message defaults to empty string."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        assert dto.message == ""


# ============================================================================
# INITIALIZATION TESTS - INVALID CASES
# ============================================================================

class TestValidationResultDTOInvalidInitialization:
    """Test ValidationResultDTO initialization for invalid cases."""

    def test_initialization_invalid_with_errors(self):
        """Test invalid case with error messages."""
        errors = ["Sample1 has no KOs", "Invalid KO format"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=None,
            validated_items=2,
            message="Validation failed"
        )

        assert dto.is_valid is False
        assert dto.errors == errors
        assert dto.validated_items == 2

    def test_initialization_invalid_with_errors_and_warnings(self):
        """Test invalid case with both errors and warnings."""
        errors = ["Critical error"]
        warnings = ["Minor warning"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            validated_items=1
        )

        assert dto.is_valid is False
        assert dto.errors == errors
        assert dto.warnings == warnings

    def test_initialization_invalid_preserves_error_list_reference(self):
        """Test that error list reference is preserved."""
        errors = ["Error 1", "Error 2"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=None,
            validated_items=2
        )

        assert dto.errors is errors

    def test_initialization_invalid_preserves_warning_list_reference(self):
        """Test that warning list reference is preserved."""
        errors = ["Error"]
        warnings = ["Warning 1", "Warning 2"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            validated_items=1
        )

        assert dto.warnings is warnings


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidationResultDTOValidation:
    """Test __post_init__ validation logic."""

    def test_validation_rejects_invalid_without_errors(self):
        """Test that is_valid=False with no errors raises ValueError."""
        with pytest.raises(ValueError, match="is_valid=False requires error messages"):
            ValidationResultDTO(
                is_valid=False,
                errors=None,  # Invalid for is_valid=False
                warnings=None,
                validated_items=5
            )

    def test_validation_rejects_invalid_with_empty_error_list(self):
        """Test that is_valid=False with empty errors raises ValueError."""
        with pytest.raises(ValueError, match="is_valid=False requires error messages"):
            ValidationResultDTO(
                is_valid=False,
                errors=[],  # Invalid - empty list
                warnings=None,
                validated_items=5
            )

    def test_validation_rejects_negative_validated_items(self):
        """Test that negative validated_items raises ValueError."""
        with pytest.raises(ValueError, match="validated_items cannot be negative"):
            ValidationResultDTO(
                is_valid=True,
                errors=None,
                warnings=None,
                validated_items=-1  # Invalid
            )

    def test_validation_rejects_invalid_negative_items(self):
        """Test negative items with invalid case."""
        with pytest.raises(ValueError, match="validated_items cannot be negative"):
            ValidationResultDTO(
                is_valid=False,
                errors=["Error"],
                warnings=None,
                validated_items=-5  # Invalid
            )

    def test_validation_accepts_zero_validated_items(self):
        """Test that zero validated_items is valid."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=0  # Valid
        )

        assert dto.validated_items == 0

    def test_validation_allows_valid_with_no_errors(self):
        """Test that is_valid=True with no errors is valid."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,  # Valid for is_valid=True
            warnings=None,
            validated_items=5
        )

        assert dto.is_valid is True
        assert dto.errors is None

    def test_validation_allows_valid_with_warnings_only(self):
        """Test that is_valid=True with warnings but no errors is valid."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Warning"],
            validated_items=5
        )

        assert dto.is_valid is True
        assert dto.warnings == ["Warning"]


# ============================================================================
# ERROR CHECKING TESTS
# ============================================================================

class TestErrorChecking:
    """Test has_errors() method."""

    def test_has_errors_returns_false_when_none(self):
        """Test has_errors returns False when errors is None."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        assert dto.has_errors() is False

    def test_has_errors_returns_false_when_empty_list(self):
        """Test has_errors returns False when errors is empty list."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=[],
            warnings=None,
            validated_items=5
        )

        assert dto.has_errors() is False

    def test_has_errors_returns_true_when_errors_exist(self):
        """Test has_errors returns True when errors exist."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=None,
            validated_items=2
        )

        assert dto.has_errors() is True

    def test_has_errors_returns_true_with_single_error(self):
        """Test has_errors returns True with single error."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Single error"],
            warnings=None,
            validated_items=1
        )

        assert dto.has_errors() is True


# ============================================================================
# WARNING CHECKING TESTS
# ============================================================================

class TestWarningChecking:
    """Test has_warnings() method."""

    def test_has_warnings_returns_false_when_none(self):
        """Test has_warnings returns False when warnings is None."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        assert dto.has_warnings() is False

    def test_has_warnings_returns_false_when_empty_list(self):
        """Test has_warnings returns False when warnings is empty list."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=[],
            validated_items=5
        )

        assert dto.has_warnings() is False

    def test_has_warnings_returns_true_when_warnings_exist(self):
        """Test has_warnings returns True when warnings exist."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Warning 1", "Warning 2"],
            validated_items=5
        )

        assert dto.has_warnings() is True

    def test_has_warnings_returns_true_with_single_warning(self):
        """Test has_warnings returns True with single warning."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Single warning"],
            validated_items=5
        )

        assert dto.has_warnings() is True

    def test_has_warnings_with_invalid_case(self):
        """Test has_warnings works with invalid case (has errors)."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error"],
            warnings=["Warning"],
            validated_items=1
        )

        assert dto.has_warnings() is True


# ============================================================================
# COUNTING TESTS
# ============================================================================

class TestCounting:
    """Test error_count() and warning_count() methods."""

    def test_error_count_returns_zero_when_none(self):
        """Test error_count returns 0 when errors is None."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        assert dto.error_count() == 0

    def test_error_count_returns_zero_when_empty(self):
        """Test error_count returns 0 when errors is empty list."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=[],
            warnings=None,
            validated_items=5
        )

        assert dto.error_count() == 0

    def test_error_count_returns_correct_count(self):
        """Test error_count returns correct number of errors."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error 1", "Error 2", "Error 3"],
            warnings=None,
            validated_items=3
        )

        assert dto.error_count() == 3

    def test_error_count_with_single_error(self):
        """Test error_count with single error."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Single error"],
            warnings=None,
            validated_items=1
        )

        assert dto.error_count() == 1

    def test_warning_count_returns_zero_when_none(self):
        """Test warning_count returns 0 when warnings is None."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        assert dto.warning_count() == 0

    def test_warning_count_returns_zero_when_empty(self):
        """Test warning_count returns 0 when warnings is empty list."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=[],
            validated_items=5
        )

        assert dto.warning_count() == 0

    def test_warning_count_returns_correct_count(self):
        """Test warning_count returns correct number of warnings."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Warning 1", "Warning 2"],
            validated_items=5
        )

        assert dto.warning_count() == 2

    def test_warning_count_with_single_warning(self):
        """Test warning_count with single warning."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Single warning"],
            validated_items=5
        )

        assert dto.warning_count() == 1

    def test_counts_with_both_errors_and_warnings(self):
        """Test both counts when errors and warnings exist."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1", "Warning 2", "Warning 3"],
            validated_items=5
        )

        assert dto.error_count() == 2
        assert dto.warning_count() == 3


# ============================================================================
# IMMUTABILITY TESTS
# ============================================================================

class TestImmutability:
    """Test frozen dataclass behavior."""

    def test_cannot_modify_is_valid(self):
        """Test that is_valid attribute cannot be modified."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        with pytest.raises(AttributeError):
            dto.is_valid = False

    def test_cannot_modify_errors(self):
        """Test that errors attribute cannot be reassigned."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error"],
            warnings=None,
            validated_items=1
        )

        with pytest.raises(AttributeError):
            dto.errors = ["New error"]

    def test_cannot_modify_warnings(self):
        """Test that warnings attribute cannot be reassigned."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=["Warning"],
            validated_items=5
        )

        with pytest.raises(AttributeError):
            dto.warnings = ["New warning"]

    def test_cannot_modify_validated_items(self):
        """Test that validated_items attribute cannot be modified."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        with pytest.raises(AttributeError):
            dto.validated_items = 10

    def test_cannot_modify_message(self):
        """Test that message attribute cannot be modified."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5,
            message="Original"
        )

        with pytest.raises(AttributeError):
            dto.message = "Modified"

    def test_cannot_add_new_attribute(self):
        """Test that new attributes cannot be added."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        with pytest.raises(AttributeError):
            dto.new_field = "value"

    def test_error_list_content_can_be_modified(self):
        """Test that error list content can be modified (not the reference)."""
        errors = ["Error 1"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=None,
            validated_items=1
        )

        # List itself is mutable
        dto.errors.append("Error 2")

        assert len(dto.errors) == 2
        assert dto.error_count() == 2

    def test_warning_list_content_can_be_modified(self):
        """Test that warning list content can be modified (not the reference)."""
        warnings = ["Warning 1"]

        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=warnings,
            validated_items=5
        )

        # List itself is mutable
        dto.warnings.append("Warning 2")

        assert len(dto.warnings) == 2
        assert dto.warning_count() == 2


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_large_number_of_validated_items(self):
        """Test with very large validated_items count."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=1_000_000
        )

        assert dto.validated_items == 1_000_000

    def test_many_errors(self):
        """Test with many error messages."""
        errors = [f"Error {i}" for i in range(100)]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=None,
            validated_items=100
        )

        assert dto.error_count() == 100
        assert dto.has_errors() is True

    def test_many_warnings(self):
        """Test with many warning messages."""
        warnings = [f"Warning {i}" for i in range(50)]

        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=warnings,
            validated_items=100
        )

        assert dto.warning_count() == 50
        assert dto.has_warnings() is True

    def test_messages_with_unicode(self):
        """Test error and warning messages with Unicode."""
        errors = ["Erro: café não encontrado", "エラー: データが無効"]
        warnings = ["Aviso: dados incompletos ⚠️"]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            validated_items=2,
            message="Falha de validação 🚫"
        )

        assert "café" in dto.errors[0]
        assert "エラー" in dto.errors[1]
        assert "⚠️" in dto.warnings[0]
        assert "🚫" in dto.message

    def test_messages_with_special_characters(self):
        """Test messages with special characters and newlines."""
        errors = [
            "Error with 'quotes'",
            "Error with \"double quotes\"",
            "Error with\nnewline",
            "Error with\ttab"
        ]

        dto = ValidationResultDTO(
            is_valid=False,
            errors=errors,
            warnings=None,
            validated_items=4
        )

        assert len(dto.errors) == 4

    def test_empty_message_string(self):
        """Test with explicit empty message."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5,
            message=""
        )

        assert dto.message == ""

    def test_very_long_message(self):
        """Test with very long message."""
        long_message = "Validation failed: " + "error " * 100

        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error"],
            warnings=None,
            validated_items=1,
            message=long_message
        )

        assert len(dto.message) > 500

    def test_multiple_instances_are_independent(self):
        """Test that multiple DTO instances are independent."""
        dto1 = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5,
            message="Valid"
        )

        dto2 = ValidationResultDTO(
            is_valid=False,
            errors=["Error"],
            warnings=["Warning"],
            validated_items=1,
            message="Invalid"
        )

        assert dto1.is_valid is not dto2.is_valid
        assert dto1.message != dto2.message
        assert dto1.validated_items != dto2.validated_items


# ============================================================================
# TYPICAL USE CASE TESTS
# ============================================================================

class TestTypicalUseCases:
    """Test typical validation scenarios."""

    def test_successful_validation_no_issues(self):
        """Test typical successful validation with no issues."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=10,
            message="All 10 samples validated successfully"
        )

        assert dto.is_valid is True
        assert dto.has_errors() is False
        assert dto.has_warnings() is False
        assert dto.error_count() == 0
        assert dto.warning_count() == 0

    def test_validation_with_warnings_only(self):
        """Test validation that passes but has warnings."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=[
                "Sample1 has only 1 KO",
                "Sample2 KO count is below average"
            ],
            validated_items=2,
            message="Validation passed with warnings"
        )

        assert dto.is_valid is True
        assert dto.has_errors() is False
        assert dto.has_warnings() is True
        assert dto.warning_count() == 2

    def test_failed_validation_with_errors(self):
        """Test typical failed validation."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=[
                "Sample1 has no KOs",
                "Invalid KO format in Sample2: XYZ123"
            ],
            warnings=None,
            validated_items=2,
            message="Validation failed: 2 errors found"
        )

        assert dto.is_valid is False
        assert dto.has_errors() is True
        assert dto.has_warnings() is False
        assert dto.error_count() == 2

    def test_failed_validation_with_errors_and_warnings(self):
        """Test failed validation with both errors and warnings."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=[
                "Sample1 is empty",
                "Sample2 has duplicate KOs"
            ],
            warnings=[
                "Sample3 has low KO count",
                "Sample4 name is very long"
            ],
            validated_items=4,
            message="Validation failed with 2 errors and 2 warnings"
        )

        assert dto.is_valid is False
        assert dto.has_errors() is True
        assert dto.has_warnings() is True
        assert dto.error_count() == 2
        assert dto.warning_count() == 2

    def test_validation_of_empty_dataset(self):
        """Test validation of dataset with no items."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=0,
            message="No items to validate"
        )

        assert dto.validated_items == 0
        assert dto.is_valid is True


# ============================================================================
# STRING REPRESENTATION TESTS
# ============================================================================

class TestStringRepresentation:
    """Test string representation of DTO."""

    def test_repr_contains_key_attributes(self):
        """Test that repr contains important attributes."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error 1"],
            warnings=["Warning 1"],
            validated_items=5,
            message="Test"
        )

        repr_str = repr(dto)

        assert 'ValidationResultDTO' in repr_str
        assert 'is_valid=False' in repr_str
        assert 'validated_items=5' in repr_str

    def test_repr_is_deterministic(self):
        """Test that repr is deterministic."""
        dto = ValidationResultDTO(
            is_valid=True,
            errors=None,
            warnings=None,
            validated_items=5
        )

        repr1 = repr(dto)
        repr2 = repr(dto)

        assert repr1 == repr2

    def test_repr_with_errors_and_warnings(self):
        """Test repr with both errors and warnings."""
        dto = ValidationResultDTO(
            is_valid=False,
            errors=["Error"],
            warnings=["Warning"],
            validated_items=1
        )

        repr_str = repr(dto)

        assert 'errors=' in repr_str
        assert 'warnings=' in repr_str
