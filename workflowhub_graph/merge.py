import argparse
import glob
import json
import os
from typing import Optional

import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.cachedurlopen import patch_rdflib_urlopen
from workflowhub_graph.constants import BASE_URL


def merge_all_files(
    pattern="data/*.json", base_url: str = BASE_URL, cache_kwargs: None = Optional[dict]
) -> rdflib.Graph:
    """
    Merges all JSON-LD files in the given pattern into a single RDF graph.
    :param pattern: The pattern to match the files.
    :param base_url: The base URL for the WorkflowHub.
    :param cache_kwargs: Keyword arguments to pass to urllib cache
    :return: The merged RDF graph.
    """

    G = rdflib.Graph()

    filenames = glob.glob(pattern)

    # TODO: this can be much accelerated by caching the context
    # TODO: collect statistics about file:// references

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            print(f"Processing {fn}, {i}/{len(filenames)}")

            w_id = int(os.path.basename(fn).split("_")[0])

            json_data = make_paths_absolute(json.load(f), base_url, w_id)

            with patch_rdflib_urlopen(**cache_kwargs):
                G.parse(data=json_data, format="json-ld")

    # TODO: set a total version
    return G


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "output_filename", help="The output filename.", default="merged.ttl"
    )
    args = argparser.parse_args()

    G = merge_all_files()
    G.serialize(args.output_filename, format="ttl")


if __name__ == "__main__":
    main()
