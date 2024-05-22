
import glob
import json

import rdflib


def merge_all_files():
    G = rdflib.Graph()

    filenames = glob.glob("data/*.json")

    # TODO: this can be much accelerated by caching the context
    # TODO: collect statistics about file:// references

    for i, fn in enumerate(filenames):
        with open(fn, "r") as f:
            print(f"Processing {fn}, {i}/{len(filenames)}")
            G.parse(f, format="json-ld")
            # Process the data here


if __name__ == "__main__":
    merge_all_files()