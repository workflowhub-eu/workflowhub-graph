#!/usr/bin/env python3

import copy
import json
import aiohttp
# Using PyLD to ensure full support of all compact forms.
import pyld  # type: ignore[import]
import rdflib
import rdflib.plugins.sparql
import sys
import urllib.parse

CUSTOM_SCHEME = "rocrate"
CUSTOM_BASE = CUSTOM_SCHEME + ":"

WRROC_SPARQL_NS = {
    "dc":  "http://purl.org/dc/elements/1.1/",
    "dcterms":  "http://purl.org/dc/terms/",
    "rocrate": CUSTOM_BASE,
    "s": "http://schema.org/",
    "bs": "https://bioschemas.org/",
    "bsworkflow": "https://bioschemas.org/profiles/ComputationalWorkflow/",
    "rocrate": "https://w3id.org/ro/crate/",
    "wfcrate": "https://w3id.org/workflowhub/workflow-ro-crate/",
    "wfhprofile": "https://about.workflowhub.eu/Workflow-RO-Crate/",
    "wrprocess": "https://w3id.org/ro/wfrun/process/",
    "wrwf": "https://w3id.org/ro/wfrun/workflow/",
    "wrterm": "https://w3id.org/ro/terms/workflow-run#",
    "wikidata": "https://www.wikidata.org/wiki/",
}

if __name__ == "__main__":
    if len(sys.argv) > 2:
        # This is needed to have a behaving urllib.parse
        urllib.parse.uses_relative.append(CUSTOM_SCHEME)
        urllib.parse.uses_fragment.append(CUSTOM_SCHEME)
        
        # First, read the sparql query
        with open(sys.argv[1], mode="r", encoding="utf-8") as qH:
            sparql_query = qH.read()

        q = rdflib.plugins.sparql.prepareQuery(
            sparql_query,
            initNs=WRROC_SPARQL_NS,
        )
        
        print(f"Query read from {sys.argv[1]}\n")
        print(sparql_query)
        print()

        # Then, use it against all the input files
        for filename in sys.argv[2:]:
            print(f"Reading {filename}")
            with open(filename, mode="r", encoding="utf-8") as IJD:
                input_jld = json.load(IJD)
            context = input_jld["@context"]
            
            g = rdflib.Graph()
            parsed = g.parse(data={'@graph': pyld.jsonld.expand(input_jld, {"keepFreeFloatingNodes": True})}, format='json-ld', base=CUSTOM_BASE)

            print(f"File {filename} {parsed} {len(parsed)} {g.connected()} {len(g)} {context}")
            
            qres = g.query(q)
            # Let's show the results
            for i_row, row in enumerate(qres):
                print(f"\nTuple {i_row}")
                for key, val in row.asdict().items():
                    print(f"{key} => {val}")

    else:
        print(f"Usage: {sys.argv[0]} SPARQL_QUERY_FILE {{JSON_LD_RO_CRATE_FILE}}+", file=sys.stderr)
        sys.exit(1)
