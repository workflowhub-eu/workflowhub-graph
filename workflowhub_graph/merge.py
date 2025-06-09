import argparse
import glob
import json
import os
import re

import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.cached_url_open import patch_rdflib_urlopen
from workflowhub_graph.cli import update_progress_bar
from workflowhub_graph.constants import BASE_URL


# TODO: check if names like "#Husen" are correctly represented in the graph
def merge_all_files(
    input_file: str,
    base_url: str = BASE_URL,
    cache_kwargs: dict | None = None,
) -> rdflib.Graph:
    """
    Merges all JSON-LD files in the given pattern into a single RDF graph.
    :param input_file: A file containing a list of files to merge.
    :param base_url: The base URL for the WorkflowHub.
    :param cache_kwargs: Keyword arguments to pass to urllib cache
    :return: The merged RDF graph.
    """

    if cache_kwargs is None:
        cache_kwargs = dict()

    graph = rdflib.Graph()

    if input_file:
        with open(input_file, "r") as f:
            filenames = [line.strip() for line in f.readlines()]

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            update_progress_bar(i + 1, len(filenames))

            basename = os.path.basename(fn)

            if matched := re.match("([0-9]+?)_ro-crate-metadata.json", basename):
                w_id = int(matched.group(1))
                w_version = 1
            elif matched := re.match(
                "([0-9]+?)_([0-9]+?)_ro-crate-metadata.json", basename
            ):
                w_id = int(matched.group(1))
                w_version = int(matched.group(2))
            else:
                raise ValueError(f"Could not match the filename {basename}")

            json_data = make_paths_absolute(json.load(f), base_url, w_id, w_version)

            with patch_rdflib_urlopen(**cache_kwargs):
                graph.parse(data=json_data, format="json-ld")

    # TODO: set a total version
    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_filename", help="The output filename.", default="merged.ttl"
    )
    parser.add_argument(
        "-i",
        "--input-file",
        help="A file containing a list of files to merge."
    )
    args = parser.parse_args()

    graph = merge_all_files(input_file=args.input_file)
    graph.serialize(args.output_filename, format="ttl")


if __name__ == "__main__":
    main()
