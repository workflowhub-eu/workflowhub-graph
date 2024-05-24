import argparse
import glob
import json
import os

import rdflib

from workflowhub_graph.absolutize import make_paths_absolute
from workflowhub_graph.cached_url_open import patch_rdflib_urlopen
from workflowhub_graph.constants import BASE_URL


# TODO: check if names like "#Husen" are correctly represented in the graph
def merge_all_files(
    pattern="data/*.json", base_url: str = BASE_URL, cache_kwargs: dict | None = None
) -> rdflib.Graph:
    """
    Merges all JSON-LD files in the given pattern into a single RDF graph.
    :param pattern: The pattern to match the files.
    :param base_url: The base URL for the WorkflowHub.
    :param cache_kwargs: Keyword arguments to pass to urllib cache
    :return: The merged RDF graph.
    """

    if cache_kwargs is None:
        cache_kwargs = dict()

    graph = rdflib.Graph()

    filenames = glob.glob(pattern)

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            print(f"Processing {fn}, {i}/{len(filenames)}")

            w_id = int(os.path.basename(fn).split("_")[0])

            json_data = make_paths_absolute(json.load(f), base_url, w_id)

            # TODO: Is there an issue here? Linting shows "Expected type 'str | bytes | None', got 'dict' instead"
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
        "-p",
        "--pattern",
        help="The pattern to match the files.",
        default="data/*.json",
    )
    args = parser.parse_args()

    graph = merge_all_files(pattern=args.pattern)
    graph.serialize(args.output_filename, format="ttl")


if __name__ == "__main__":
    main()
