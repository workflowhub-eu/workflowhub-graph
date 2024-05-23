import argparse
import glob
import json
import os

import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.cachedurlopen import patch_rdflib_urlopen
from workflowhub_graph.constants import BASE_URL


def merge_all_files(pattern="data/*.json") -> rdflib.Graph:
    G = rdflib.Graph()

    filenames = glob.glob(pattern)

    # TODO: this can be much accelerated by caching the context
    # TODO: collect statistics about file:// references

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            print(f"Processing {fn}, {i}/{len(filenames)}")

            json_data = json.load(f)
            # TODO: store metadata
            w_id = int(os.path.basename(fn).split("_")[0])
            json_data = make_paths_absolute(json_data, BASE_URL, w_id)

            # TODO: make this actual caching, and pre-populate in the test
            with patch_rdflib_urlopen(
                lambda x: "tests/test_data/ro-crate-context-1.0.json"
            ):
                G.parse(data=json_data, format="json-ld")

    # TODO: set a total version
    return G


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "output_filename", help="The output filename.", default="merged.ttl"
    )
    args = argparser.parse_args()

    G = merge_all_files()
    G.serialize(args.output_filename, format="ttl")
