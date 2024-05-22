
import glob
import json
import os

import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.constants import BASE_URL


def merge_all_files():
    G = rdflib.Graph()

    filenames = glob.glob("data/*.json")

    # TODO: this can be much accelerated by caching the context
    # TODO: collect statistics about file:// references

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            print(f"Processing {fn}, {i}/{len(filenames)}")

            json_data = json.load(f)
            # TODO: store metadata
            w_id = int(os.path.basename(fn).split("_")[0])
            json_data = make_paths_absolute(json_data, BASE_URL, w_id)

            G.parse(f, format="json-ld")
            # Process the data here


if __name__ == "__main__":
    merge_all_files()