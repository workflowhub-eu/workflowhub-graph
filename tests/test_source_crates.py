from io import StringIO, TextIOWrapper
import json
import time
import unittest
import pytest
import os
from unittest.mock import patch, MagicMock

import rdflib
import requests

from src.absolutize import make_paths_absolute
from src.source_crates import (
    download_and_extract_json_from_metadata_endpoint,
    download_and_extract_json_from_zip,
    download_workflow_ids,
    process_workflow_ids,
)
from src.constants import BASE_URL_DEV


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get



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
    def test_json_from_metadata_endpoint_download_successful(self, mock_requests_get):
        # Mock a successful JSON response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"key": "value"}'
        mock_requests_get.return_value = mock_response

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/json"
        )
        assert result == b'{"key": "value"}'

    def test_json_from_metadata_endpoint_no_json_content_type(self, mock_requests_get):
        # Mock a response with a non-JSON content type
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "text/html"}
        mock_requests_get.return_value = mock_response

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/html"
        )
        assert result is None

    def test_json_from_metadata_endpoint_request_exception(self, mock_requests_get):
        # Mock a request exception
        mock_requests_get.side_effect = requests.RequestException("Error")

        result = download_and_extract_json_from_metadata_endpoint(
            "http://example.com/error"
        )
        assert result is None


class TestDownloadAndExtractJsonFromZip:
    def test_download_and_extract_json_from_zip_incorrect_file_extension(
        self, mock_requests_get
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [
            b"PK\x03\x04",
            b"PK\x01\x02",
            b"PK\x05\x06",
        ]

        mock_requests_get.return_value = mock_response

        with patch("src.source_crates.ZipFile") as mock_zipfile:
            mock_zipfile.return_value.__enter__.return_value.namelist.return_value = [
                "not-json-file.txt"
            ]

            result = download_and_extract_json_from_zip("http://example.com/test.zip")
            assert result is None


class TestDownloadWorkflowIds:

    def test_download_workflow_ids_success(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "883"}]}

        mock_requests_get.return_value = mock_response

        result = download_workflow_ids("http://example.com/workflows.json")
        assert result is not None
        assert "data" in result
        assert result["data"][0]["id"] == "883"

    def test_download_workflow_ids_404(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")

        mock_requests_get.return_value = mock_response

        result = download_workflow_ids("http://example.com/workflows.json")
        assert result is None


class TestProcessWorkflowIds:
    @patch("src.source_crates.download_and_extract_json_from_zip")
    def test_process_workflow_ids(
        self, mock_download_and_extract_json_from_zip, setup_output_dir
    ):
        mock_download_and_extract_json_from_zip.return_value = b'{"name": "test"}'

        workflows_data = {"data": [{"id": "883"}]}

        output_dir = setup_output_dir
        process_workflow_ids(workflows_data, output_dir)

        expected_file_path = os.path.join(output_dir, "883_ro-crate-metadata.json")
        assert os.path.exists(expected_file_path)

        with open(expected_file_path, "rb") as f:
            content = f.read()
            assert content == b'{"name": "test"}'


class TestAbsolutizePaths: #(unittest.TestCase):

    def get_test_data_file(self, filename) -> str:
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(tests_dir, "test_data", filename)
    
    def is_all_absolute(self, G: rdflib.Graph) -> bool:
        for triple in G:
            for item in triple:
                if isinstance(item, rdflib.URIRef):
                    # TODO: is this enough?
                    if item.startswith("file://"):
                        return False
        return True

    # @pytest.mark.parametrize("workfltestow_id", [41, 552, 634, 678])
    @pytest.mark.parametrize("workflow_id", [41])
    def test_make_paths_absolute(self, workflow_id):
        
        # TODO: complete this mock
        def local_urlopen(request):
            r = MagicMock()
            c = open(self.get_test_data_file("ro-crate-context.json"), "rt").read()
            # r.geturl = MagicMock(return_value="https://w3id.org/ro/crate/1.0/context")
            # r.read = MagicMock(return_value=c)
            # r.getByteStream = MagicMock(return_value=TextIOWrapper(StringIO(c)))
            return r
       
        with patch("rdflib.parser.urlopen", local_urlopen):
            rdflib.Graph().parse("https://w3id.org/ro/crate/1.0/context", format="json-ld")

        return

        with open(self.get_test_data_file(f"{workflow_id}_ro-crate-metadata.json"), "r") as f:
            json_data = json.load(f)

        # TODO: 552 already has file:// paths https://dev.workflowhub.eu/workflows/552/ro_crate?version=1
        # NOTE: ids can not be found, like 634, or forbidden, like 678

        assert not self.is_all_absolute(rdflib.Graph().parse(data=json.dumps(json_data), format="json-ld"))

        json_data_abs_paths = make_paths_absolute(json_data, BASE_URL_DEV, 41)

        G = rdflib.Graph().parse(data=json.dumps(json_data_abs_paths), format="json-ld")
        for s, p, o in G:
            print(s, p, o) 

        assert self.is_all_absolute(G)