from src.presentation.callbacks.sample_dataset_utils import (
    SAMPLE_DATASET_FILENAME,
    resolve_sample_dataset_path,
)


def test_resolve_sample_dataset_path_points_to_bundled_file() -> None:
    """Sample dataset helper should resolve the bundled example dataset."""
    dataset_path = resolve_sample_dataset_path()

    assert dataset_path.exists()
    assert dataset_path.name == SAMPLE_DATASET_FILENAME
    assert dataset_path.parts[-3:] == ("src", "data", SAMPLE_DATASET_FILENAME)
