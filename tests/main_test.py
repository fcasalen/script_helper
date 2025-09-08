from script_helper.main import collect_packages_by_author_email, cli
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch
import pytest
import io
import sys
import json
import os

@pytest.fixture
def mock_metadata_files(tmp_path):
    """
    Creates a temporary directory structure with mock .dist-info directories and METADATA files.
    """
    dist_info_1 = tmp_path / "package1-1.0.dist-info"
    dist_info_1.mkdir()
    metadata_1 = dist_info_1 / "METADATA"
    metadata_1.write_text(
        "Metadata-Version: 2.1\n"
        "Name: package1\n"
        "Version: 1.0\n"
        "Summary: A test package\n"
        "Author: Test Author\n"
        "Author-email: test@example.com\n"
        'entry_points: ={"console_scripts": ["test=test.main:cli]}"'
    )

    dist_info_2 = tmp_path / "package2-2.0.dist-info"
    dist_info_2.mkdir()
    metadata_2 = dist_info_2 / "METADATA"
    metadata_2.write_text(
        "Metadata-Version: 2.1\n"
        "Name: package2\n"
        "Version: 2.0\n"
        "Summary: Another test package\n"
        "Author: Another Author\n"
        "Author-email: another@example.com\n"
    )

    return tmp_path

def test_collect_packages_by_author_email_valid_email(mock_metadata_files):
    mock_entry_point = MagicMock()
    mock_entry_point.name = "test_entry_point"
    mock_entry_point.dist = MagicMock()
    mock_entry_point.dist.name = "package1"
    target_emails = ["test@example.com"]
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        result = collect_packages_by_author_email(target_emails, str(mock_metadata_files))
    assert len(result) == 1
    assert "package1" in result
    assert result["package1"]["Version"] == "1.0"
    assert result["package1"]["Author-email"] == "test@example.com"
    assert result["package1"]["entry_points"] == ["test_entry_point"]

def test_collect_packages_by_author_email_multiple_emails(mock_metadata_files):
    target_emails = ["test@example.com", "another@example.com"]
    result = collect_packages_by_author_email(target_emails, str(mock_metadata_files))
    assert len(result) == 2
    assert "package1" in result
    assert "package2" in result

def test_collect_packages_by_author_email_no_matching_email(mock_metadata_files):
    target_emails = ["nomatch@example.com"]
    result = collect_packages_by_author_email(target_emails, str(mock_metadata_files))
    assert len(result) == 0

def test_collect_packages_by_author_email_invalid_folder():
    with pytest.raises(AssertionError, match="Folder .* does not exist"):
        collect_packages_by_author_email(["test@example.com"], "non_existent_folder")

def test_collect_packages_by_author_email_invalid_email_format(mock_metadata_files):
    with pytest.raises(AssertionError, match="All target emails must be valid email addresses"):
        collect_packages_by_author_email(["invalid-email"], str(mock_metadata_files))

def test_cli_valid_email(mock_metadata_files):
    output = io.StringIO()
    sys.argv = ['script_helper/main.py', "--emails", "test@example.com", "--python_packages_folder", str(mock_metadata_files)]
    with redirect_stdout(output):
        cli()
    captured = output.getvalue()
    assert "Found 1 packages by test@example.com:" in captured
    assert "package1:" in captured
    assert "Version: 1.0" in captured
    assert "Summary: A test package" in captured

def test_cli_all_email(mock_metadata_files):
    output = io.StringIO()
    sys.argv = ['script_helper/main.py', "--python_packages_folder", str(mock_metadata_files)]
    with redirect_stdout(output):
        cli()
    captured = output.getvalue()
    assert "Found 2 packages:" in captured
    assert "package1:" in captured
    assert "Version: 1.0" in captured
    assert "Summary: A test package" in captured
    assert "package2:" in captured
    assert "Version: 1.0" in captured
    assert "Summary: Another test package" in captured

def test_cli_multiple_emails(mock_metadata_files):
    output = io.StringIO()
    sys.argv = ['script_helper/main.py', "--emails", "test@example.com", "another@example.com", "--python_packages_folder", str(mock_metadata_files)]
    with redirect_stdout(output):
        cli()
    captured = output.getvalue()
    assert "Found 2 packages by test@example.com, another@example.com:" in captured
    assert "package1:" in captured
    assert "Version: 1.0" in captured
    assert "Summary: A test package" in captured
    assert "package2:" in captured
    assert "Version: 1.0" in captured
    assert "Summary: Another test package" in captured

def test_cli_no_matching_email(mock_metadata_files):
    output = io.StringIO()
    sys.argv = ['script_helper/main.py', "--emails", "test2@example.com", "--python_packages_folder", str(mock_metadata_files)]
    with redirect_stdout(output):
        cli()
    captured = output.getvalue()
    assert "Found 0 packages by test2@example.com:" in captured

def test_cli_save_json(mock_metadata_files):
    if os.path.exists('packages.json'):
        os.remove('packages.json')
    sys.argv = ['script_helper/main.py', "--emails", "test@example.com", "--python_packages_folder", str(mock_metadata_files), '--save_json']
    cli()
    with open('packages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == {
        'package1': {
            'Author': 'Test Author',
            'Author-email': 'test@example.com',
            'Metadata-Version': '2.1',
            'Name': 'package1',
            'Summary': 'A test package',
            'Version': '1.0',
            'entry_points': []
        }
    }
    os.remove('packages.json')