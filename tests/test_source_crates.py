import pytest
import os
from unittest.mock import patch, MagicMock

from requests import Session, RequestException
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib3.exceptions import MaxRetryError

from workflowhub_graph.source_crates import (
    download_and_extract_json_from_metadata_endpoint,
    download_and_extract_json_from_zip,
    download_workflow_ids,
    process_workflow_ids,
)


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


# Source - https://stackoverflow.com/a/49407265
# Posted by Blafkees, modified by community. See post 'Timeline' for change history
# Retrieved 2026-10-15, License - CC BY-SA 3.0
@pytest.fixture
def mock_session_get():
    with patch.object(Session, "get") as mock_get:
        yield mock_get


@pytest.fixture(scope="module")
def setup_session():
    session = Session()
    retries = Retry(
        total=3,
        backoff_factor=0.1,  # much shorter than reality to save time in tests
        status_forcelist=[
            500,
            503,
            *range(520, 531),
        ],  # server availability errors + Cloudflare errors
        allowed_methods={"GET"},
        raise_on_status=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    yield session
    session.close()


@pytest.fixture
def setup_output_dir():
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    yield output_dir
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)


class TestDownloadAndExtractJsonFromMetadataEndpoint:
    def test_json_from_metadata_endpoint_download_successful(
        self, setup_session, mock_session_get
    ):
        """Mock a successful JSON response"""

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"key": "value"}'
        mock_session_get.return_value = mock_response

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/json", setup_session
        )
        assert result == b'{"key": "value"}'

    def test_json_from_metadata_endpoint_no_json_content_type(
        self, capsys, setup_session, mock_session_get
    ):
        """Mock a response with a non-JSON content type"""

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "text/html"}
        mock_session_get.return_value = mock_response

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/html", setup_session
        )
        assert result is None

        captured = capsys.readouterr()
        assert "No JSON file found at: " in captured.out

    def test_json_from_metadata_endpoint_request_exception(
        self, setup_session, mock_session_get
    ):
        """Mock a request exception"""

        mock_session_get.side_effect = RequestException("Error")

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/error", setup_session
        )
        assert result is None

    def test_json_from_metadata_endpoint_max_retries(
        self, capsys, caplog, setup_session
    ):
        """Mock a request exception where max retries were reached.

        This calls a live URL without mocking, so technically it is an integration test.
        However, ensuring the retries actually occur when mocking Session.get
        is not straightforward and this is a much easier way to do it.
        """

        result = download_and_extract_json_from_metadata_endpoint(
            "https://postman-echo.com/status/503", setup_session
        )
        assert result is None

        captured = capsys.readouterr()
        assert "Max retries exceeded" in captured.out


class TestDownloadAndExtractJsonFromZip:
    def test_download_and_extract_json_from_zip_incorrect_file_extension(
        self, setup_session, mock_session_get
    ):
        """Mock a response with a non-Zip file"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [
            b"PK\x03\x04",
            b"PK\x01\x02",
            b"PK\x05\x06",
        ]

        mock_session_get.return_value = mock_response

        with patch("workflowhub_graph.source_crates.ZipFile") as mock_zipfile:
            mock_zipfile.return_value.__enter__.return_value.namelist.return_value = [
                "not-json-file.txt"
            ]

            result = download_and_extract_json_from_zip(
                "http://example.com/test.zip", setup_session
            )
            assert result is None


class TestDownloadWorkflowIds:
    def test_download_workflow_ids_success(self, mock_requests_get):
        """Mock a successful JSON response"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "883"}]}

        mock_requests_get.return_value = mock_response

        result = download_workflow_ids("http://example.com/workflows.json")
        assert result is not None
        assert "data" in result
        assert result["data"][0]["id"] == "883"

    def test_download_workflow_ids_404(self, mock_requests_get):
        """Mock a 404 response"""

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")

        mock_requests_get.return_value = mock_response

        result = download_workflow_ids("http://example.com/workflows.json")
        assert result is None


class TestProcessWorkflowIds:
    @patch("workflowhub_graph.source_crates.get_dot_json_endpoint")
    @patch("workflowhub_graph.source_crates.download_and_extract_json_from_zip")
    @pytest.mark.parametrize("all_versions", [True, False])
    def test_process_workflow_ids(
        self,
        mock_download_and_extract_json_from_zip,
        get_dot_json_endpoint,
        setup_output_dir,
        all_versions,
    ):
        """Mock a successful download and extraction of a JSON file from a zip file"""

        mock_download_and_extract_json_from_zip.return_value = b'{"name": "test"}'

        get_dot_json_endpoint.return_value = {
            "data": {
                "attributes": {
                    "latest_version": 12,
                    "versions": [{"version": 3}, {"version": 4}],
                }
            }
        }

        workflows_data = {"data": [{"id": "883"}]}

        output_dir = setup_output_dir
        process_workflow_ids(workflows_data, output_dir, all_versions=all_versions)

        if all_versions:
            expected_versions = [3, 4]
        else:
            expected_versions = [12]

        for version in expected_versions:
            expected_file_path = os.path.join(
                output_dir, f"883_{version}_ro-crate-metadata.json"
            )
            assert os.path.exists(expected_file_path)

            with open(expected_file_path, "rb") as f:
                content = f.read()
                assert content == b'{"name": "test"}'
