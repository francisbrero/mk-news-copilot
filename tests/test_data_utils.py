import pytest
import json
from pathlib import Path
from app.utils.data_utils import read_json_file, save_json_file
from unittest.mock import patch

TEST_DATA_DIR = Path("tests/test_data")

@pytest.fixture(autouse=True)
def ensure_test_dir():
    TEST_DATA_DIR.mkdir(exist_ok=True)
    yield
    # Don't cleanup the directory itself after tests

@pytest.fixture
def test_file():
    file_path = TEST_DATA_DIR / "test.json"
    TEST_DATA_DIR.mkdir(exist_ok=True)  # Ensure directory exists
    # Ensure the file exists with valid initial JSON for save_json_file
    file_path.write_text(json.dumps({"items": []}))
    yield file_path
    if file_path.exists():
        file_path.unlink()

def test_read_json_file(test_file):
    # Test reading non-existent file (create a unique non-existent path)
    non_existent_file = TEST_DATA_DIR / "non_existent.json"
    assert read_json_file(str(non_existent_file)) == [] # Use full path

    # Test reading existing file
    test_data = [{"key": "value"}]
    # write using save_json_file which expects {'items': ...} structure
    save_json_file(str(test_file), {"items": test_data})
    # read_json_file returns the list inside 'items'
    assert read_json_file(str(test_file)) == test_data

# Renamed test function to reflect the function being tested
def test_save_json_file(test_file):
    test_data_list = [{"key": "value"}]
    test_data_dict = {"items": test_data_list}
    save_json_file(str(test_file), test_data_dict)

    # Verify file was written correctly
    # save_json_file writes the dict, so we load the dict back
    assert json.loads(test_file.read_text()) == test_data_dict

# Test the atomicity aspect of save_json_file
def test_save_json_file_atomicity(test_file):
    initial_data_list = [{"key": "initial"}]
    initial_data_dict = {"items": initial_data_list}
    save_json_file(str(test_file), initial_data_dict)
    assert json.loads(test_file.read_text()) == initial_data_dict

    new_data_list = [{"key": "new_value"}]
    new_data_dict = {"items": new_data_list}

    # Simulate failure during write (after opening temp file, before replace)
    def mock_dump_fails(*args, **kwargs):
        # First call (writing to temp file) succeeds
        if mock_dump_fails.call_count == 0:
            mock_dump_fails.call_count += 1
            # Call the original json.dump
            return original_dump(*args, **kwargs)
        # Subsequent calls (potentially within error handling, though unlikely here)
        # Or, more relevantly, simulate failure *before* os.replace
        # We'll simulate this by raising an error *after* the successful dump
        raise IOError("Simulated write failure before replace")

    mock_dump_fails.call_count = 0
    original_dump = json.dump

    # Comments explaining the patching strategy
    # We patch json.dump to simulate a failure *during* the write to the temporary file
    # and os.replace to simulate a failure *during* the final atomic rename.
    # We expect os.replace's failure to propagate as an IOError.
    with (
        patch('json.dump', side_effect=mock_dump_fails),
        patch('os.replace', side_effect=IOError("Simulated replace failure"))
    ):
        with pytest.raises(IOError):  # Expect the IOError from the patched os.replace
            save_json_file(str(test_file), new_data_dict)

    # Check if the original data is still intact after the failed atomic write attempt.
    # Because os.replace failed, the original file should not have been overwritten.
    assert json.loads(test_file.read_text()) == initial_data_dict

# Cleanup: Remove the old test_atomic_write if it exists (it doesn't in the snippet, but ensuring)
# No need for the explicit function test_atomic_write anymore. 