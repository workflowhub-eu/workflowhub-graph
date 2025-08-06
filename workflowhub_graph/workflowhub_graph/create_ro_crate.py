import argparse
import sys
import uuid
from datetime import datetime

from rocrate.model import ContextEntity, Person
from rocrate.rocrate import ROCrate

AUTHORS = {
    "https://orcid.org/0000-0003-1193-6632": {
        "givenName": "Alexander",
        "familyName": "Hambley",
        "affiliation": "University of Manchester",
    },
    "https://orcid.org/0000-0002-0035-6475": {
        "givenName": "Eli",
        "familyName": "Chadwick",
        "affiliation": "University of Manchester",
    },
    "https://orcid.org/0000-0002-4565-9760": {
        "givenName": "Oliver",
        "familyName": "Woolland",
        "affiliation": "University of Manchester",
    },
    "https://orcid.org/0000-0001-9842-9718": {
        "givenName": "Stian",
        "familyName": "Soiland-Reyes",
        "affiliation": "University of Manchester",
    },
    "https://orcid.org/0000-0001-6353-0808": {
        "givenName": "Volodymyr",
        "familyName": "Savchenko",
        "affiliation": "University of Geneva",
    },
}


def create_ro_crate(input_file: str, workflow_file: str, output_dir: str) -> None:
    """
    Create an RO-Crate metadata file for the given input file and output directory.
    :param input_file: The input file provided by the Snakemake workflow (e.g., merged data file).
    :param workflow_file: Reference to the Snakemake workflow.
    :param output_dir: The output directory to store the RO-Crate metadata file.
    """
    crate = ROCrate()

    crate.name = "WorkflowHub Knowledge Graph"
    crate.description = (
        "This RO-Crate contains the merged RDF triples from multiple RO-Crates sourced from "
        "WorkflowHub."
    )

    # Add authors:
    for a in AUTHORS.keys():
        author = crate.add(
            Person(
                crate,
                a,
                properties=AUTHORS[a],
            )
        )
        crate.root_dataset.append_to("author", author)

    # Add dataset and files:
    crate.add_dataset(
        "./workflowhub_graph/",
        properties={
            "name": "WorkflowHub Graph",
            "description": "A directory containing modules used by the workflow.",
        },
    )

    crate.add_file(
        "./Dockerfile",
        properties={
            "@type": "File",
            "name": "Dockerfile",
            "encodingFormat": "text/plain",
            "description": "The Dockerfile used to build the Docker images for the workflow.",
            "conformsTo": {"@id": "https://docs.docker.com/reference/dockerfile/"},
        },
    )

    created_files = crate.add_file(
        "./created_files.json",
        properties={
            "@type": "File",
            "name": "created_files.json",
            "encodingFormat": "application/json",
            "description": "A JSON file containing the list of files sourced by the workflow.",
            "conformsTo": {"@id": "https://docs.docker.com/reference/dockerfile/"},
        },
    )

    crate.add_file("./poetry.lock")
    crate.add_file("./README.md")

    # Add data and workflow entities:
    data_entity = crate.add_file(
        input_file,
        properties={
            "name": "Merged Data File",
            "description": "This file contains merged RDF triples from multiple RO-Crates sourced from WorkflowHub.",
            "encodingFormat": "text/turtle",
        },
    )

    # data_entity["author"] = [auth_1, auth_2, auth_3, auth_4, auth_5]
    data_entity["isBasedOn"] = created_files

    workflow_entity = crate.add_workflow(
        source=workflow_file,
        properties={
            "name": "Snakemake Workflow",
            "description": "This is the Snakemake workflow used to generate the merged RDF triples.",
        },
        main=True,
        lang="snakemake",
    )

    # workflow_entity["author"] = [auth_1, auth_2, auth_3, auth_4]
    workflow_entity["output"] = data_entity

    if "conformsTo" not in crate.root_dataset:
        crate.root_dataset.append_to(
            "conformsTo", {"@id": "https://w3id.org/ro/wfrun/workflow/0.5"}
        )

    # Add license:
    crate.license = "https://spdx.org/licenses/BSD-2-Clause.html"

    # Writing the RO-Crate metadata:
    crate.write(output_dir)


def main():

    parser = argparse.ArgumentParser(description="Create RO-Crate for the RDF graph.")
    parser.add_argument("-i", "--input-file", help="The RDF graph file.", required=True)
    parser.add_argument(
        "-o",
        "--output-dir",
        help="The output directory for the RO-Crate.",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--workflow-file",
        help="The workflow file used to generate the RDF graph.",
        required=True,
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Extract the arguments
    input_file = args.input_file
    workflow_file = args.workflow_file
    output_dir = args.output_dir

    create_ro_crate(
        input_file=input_file, workflow_file=workflow_file, output_dir=output_dir
    )


if __name__ == "__main__":
    main()
