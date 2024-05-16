import pytest
import os
from unittest.mock import patch, MagicMock

from src.source_crates import download_and_extract_json, download_workflow_ids, process_workflow_ids


@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def setup_output_dir():
    output_dir = 'test_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    yield output_dir
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)


def test_download_and_extract_json_txt_file(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content = lambda chunk_size: [b'PK\x03\x04', b'PK\x01\x02', b'PK\x05\x06']

    mock_requests_get.return_value = mock_response

    with patch('src.source_crates.ZipFile') as mock_zipfile:
        mock_zipfile.return_value.__enter__.return_value.namelist.return_value = ['not-json-file.txt']

        result = download_and_extract_json('http://example.com/test.zip')
        assert result is None


def test_download_workflow_ids_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": "883"}]}

    mock_requests_get.return_value = mock_response

    result = download_workflow_ids('http://example.com/workflows.json')
    assert result is not None
    assert 'data' in result
    assert result['data'][0]['id'] == '883'


def test_download_workflow_ids_404(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")

    mock_requests_get.return_value = mock_response

    result = download_workflow_ids('http://example.com/workflows.json')
    assert result is None


@patch('src.source_crates.download_and_extract_json')
def test_process_workflow_ids(mock_download_and_extract_json, setup_output_dir):
    mock_download_and_extract_json.return_value = b'{"name": "test"}'

    workflows_data = {"data": [{"id": "883"}]}

    output_dir = setup_output_dir
    process_workflow_ids(workflows_data, output_dir)

    expected_file_path = os.path.join(output_dir, '883_ro-crate-metadata.json')
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, 'rb') as f:
        content = f.read()
        assert content == b'{"name": "test"}'
