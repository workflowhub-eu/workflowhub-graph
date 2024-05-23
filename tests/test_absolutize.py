import json
import os

import pytest
import rdflib

from workflowhub_graph.absolutize import is_all_absolute, make_paths_absolute
from workflowhub_graph.cachedurlopen import patch_rdflib_urlopen
from workflowhub_graph.constants import BASE_URL
from workflowhub_graph.merge import merge_all_files


def get_test_data_file(filename=""):
    """Returns the path to a test data file given it's relative path."""

    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tests_dir, "test_data", filename)


class TestAbsolutizePaths:  # (unittest.TestCase):
    # NOTE: ids can not be found, like 634, or forbidden, like 678
    @pytest.mark.parametrize("workflow_id", [41, 31, 552, 883])
    def test_make_paths_absolute(self, workflow_id):
        with patch_rdflib_urlopen(get_test_data_file(), write_cache=False):
            with open(
                get_test_data_file(f"{workflow_id}_ro-crate-metadata.json"), "r"
            ) as f:
                json_data = json.load(f)

            assert not is_all_absolute(
                rdflib.Graph().parse(data=json.dumps(json_data), format="json-ld")
            )

            json_data_abs_paths = make_paths_absolute(json_data, BASE_URL, 41)

            G = rdflib.Graph().parse(
                data=json.dumps(json_data_abs_paths), format="json-ld"
            )

            assert is_all_absolute(G)

    def test_merged(self):
        G = merge_all_files(
            get_test_data_file("[0-9]*ro-crate*.json"),
            cache_kwargs=dict(
                cache_base_dir=get_test_data_file(),
                write_cache=False,
            ),
        )

        assert is_all_absolute(G)

        # checking that we got some useful data about the authors

        bindings = G.query(
            """SELECT DISTINCT ?author
            WHERE {
                ?s <http://schema.org/author> ?author
            }"""
        ).bindings

        assert set([b["author"] for b in bindings]) == set(
            [rdflib.term.Literal("Arnaud Meng, Maxim Scheremetjew, Michael Crusoe")]
        )
