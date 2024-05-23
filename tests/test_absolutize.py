import io
import json
import os
from unittest.mock import patch

import pytest
import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.constants import BASE_URL_DEV


def get_test_data_file(filename):
    """Returns the path to a test data file."""

    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tests_dir, "test_data", filename)


def is_all_absolute(graph) -> bool:
    """Checks if all URIs in the RDF graph are absolute URIs."""

    for triple in graph:
        for item in triple:
            if isinstance(item, rdflib.URIRef):
                # TODO: is this enough?
                if item.startswith("file://"):
                    return False
    return True


class TestAbsolutizePaths:
    # TODO: 552 already has file:// paths https://dev.workflowhub.eu/workflows/552/ro_crate?version=1
    # NOTE: ids can not be found, like 634, or forbidden, like 678
    @pytest.mark.parametrize("workflow_id", [41])
    def test_make_paths_absolute(self, workflow_id):
        """Test if paths in the RO-Crate metadata are correctly made absolute."""

        def local_urlopen():
            """Mocks the urlopen function to return local test data."""

            class Response(io.StringIO):
                content_type = "text/html"
                headers = {"Content-Type": "text/html"}

                def get_info(self):
                    return self.headers

                def get_url(self):
                    return "https://w3id.org/ro/crate/1.0/context"

            content = open(get_test_data_file("ro-crate-context.json"), "rt").read()

            return Response(content)

        with patch("urllib.request.urlopen", local_urlopen):
            with open(
                get_test_data_file(f"{workflow_id}_ro-crate-metadata.json"), "r"
            ) as f:
                json_data = json.load(f)

            assert not is_all_absolute(
                rdflib.Graph().parse(data=json.dumps(json_data), format="json-ld")
            )

            json_data_abs_paths = make_paths_absolute(
                json_data, BASE_URL_DEV, workflow_id=41
            )

            graph = rdflib.Graph().parse(
                data=json.dumps(json_data_abs_paths), format="json-ld"
            )

            assert is_all_absolute(graph)
