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
    :return:
    """
    crate = ROCrate()

    crate.name = "WorkflowHub Knowledge Graph"
    crate.description = (
        "This RO-Crate contains the merged RDF triples from multiple RO-Crates sourced from "
        "WorkflowHub."
    )

    # Add authors:
    alice = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0000-0000-0000",
            properties={"name": "Alice Doe", "affiliation": "University of Flatland"},
        )
    )
    bob = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0000-0000-0001",
            properties={"name": "Bob Doe", "affiliation": "University of Flatland"},
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
            "encodingFormat": "application/yaml",
            "description": "The Dockerfile used to build the Docker images for the workflow.",
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
            "author": [alice["@id"], bob["@id"]],
        },
    )

    workflow_entity = crate.add_workflow(
        source=workflow_file,
        properties={
            "name": "Snakemake Workflow",
            "description": "This is the Snakemake workflow used to generate the merged RDF triples.",
            "author": [alice["@id"], bob["@id"]],
            "output": data_entity["@id"],
        },
        main=True,
        lang="snakemake",
    )

    if "conformsTo" not in crate.root_dataset:
        crate.root_dataset.append_to(
            "conformsTo", {"@id": "https://w3id.org/ro/wfrun/workflow/0.5"}
        )

    crate.add(
        ContextEntity(
            crate,
            identifier=str(uuid.uuid4()),
            properties={
                "@type": "CreateAction",
                "name": "Merge RDF Triples",
                "description": "Merging RDF triples from sourced crates.",
                "agent": [alice["@id"], bob["@id"]],
                "endTime": datetime.now().time().isoformat(),
                "instrument": workflow_entity["@id"],
                "result": data_entity["@id"],
            },
        )
    )

    # Writing the RO-Crate metadata:
    crate.write(output_dir)


if __name__ == "__main__":
    create_ro_crate(
        input_file=sys.argv[1], workflow_file=sys.argv[2], output_dir=sys.argv[3]
    )
