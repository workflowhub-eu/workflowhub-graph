import sys
import uuid
from datetime import datetime

from rocrate.model import ContextEntity, Person
from rocrate.rocrate import ROCrate


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
    auth_1 = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0000-0000-0000",
            properties={
                "name": "Alexander Hambley",
                "affiliation": "University of Manchester",
            },
        )
    )
    auth_2 = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0002-0035-6475",
            properties={
                "name": "Eli Chadwick",
                "affiliation": "University of Manchester",
            },
        )
    )
    auth_3 = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0002-4565-9760",
            properties={
                "name": "Oliver Woolland",
                "affiliation": "University of Manchester",
            },
        )
    )
    auth_4 = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0001-9842-9718",
            properties={
                "name": "Stian Soiland-Reyes",
                "affiliation": "University of Manchester",
            },
        )
    )
    auth_5 = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0001-6353-0808",
            properties={
                "name": "Volodymyr Savchenko",
                "affiliation": "University of Geneva",
            },
        )
    )

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

    data_entity["author"] = [auth_1, auth_2, auth_3, auth_4, auth_5]
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

    workflow_entity["author"] = [auth_1, auth_2, auth_3, auth_4]
    workflow_entity["output"] = data_entity

    if "conformsTo" not in crate.root_dataset:
        crate.root_dataset.append_to(
            "conformsTo", {"@id": "https://w3id.org/ro/wfrun/workflow/0.5"}
        )

    # Add license:
    crate.license = "https://opensource.org/license/bsd-2-clause"

    # Writing the RO-Crate metadata:
    crate.write(output_dir)


if __name__ == "__main__":
    create_ro_crate(
        input_file=sys.argv[1], workflow_file=sys.argv[2], output_dir=sys.argv[3]
    )
