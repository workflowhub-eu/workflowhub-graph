import sys

from rocrate.model import Person
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

    data_entity = crate.add_file(
        input_file,
        properties={
            "name": "Merged Data File",
            "description": "This file contains merged RDF triples from multiple RO-Crates sourced from WorkflowHub.",
            "encodingFormat": "text/turtle",
        },
    )

    workflow_entity = crate.add_file(
        workflow_file,
        properties={
            "name": "Snakemake Workflow",
            "description": "This is the Snakemake workflow used to generate the merged RDF triples.",
            "programmingLanguage": {
                "@id": "https://w3id.org/workflowhub/workflow-ro-crate#Snakemake",
                "name": "Snakemake",
            },
            "url": workflow_file,
        },
    )

    # Linking the data file to the workflow:
    workflow_entity["output"] = data_entity

    # Authors:
    alice_id = "https://orcid.org/0000-0000-0000-0000"
    bob_id = "https://orcid.org/0000-0000-0000-0001"
    alice = crate.add(
        Person(
            crate,
            alice_id,
            properties={"name": "Alice Doe", "affiliation": "University of Flatland"},
        )
    )
    bob = crate.add(
        Person(
            crate,
            bob_id,
            properties={"name": "Bob Doe", "affiliation": "University of Flatland"},
        )
    )

    data_entity["author"] = [alice, bob]
    workflow_entity["author"] = [alice, bob]

    # Writing the RO-Crate metadata:
    crate.write(output_dir)


if __name__ == "__main__":
    create_ro_crate(
        input_file=sys.argv[1], workflow_file=sys.argv[2], output_dir=sys.argv[3]
    )
