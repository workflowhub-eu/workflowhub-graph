import argparse
import os
import shutil
import sys
import uuid
from datetime import datetime

from rocrate.model import ContextEntity, Person
from rocrate.rocrate import ROCrate


def create_ro_crate(
    full_graph_file: str,
    base_graph_file: str,
    enrichments_dir: str,
    workflow_file: str,
    output_dir: str,
) -> None:
    """
    Create an RO-Crate metadata file for the given input file and output directory.
    :param full_graph_file: The full, enriched knowledge graph.
    :param base_graph_file: The base knowledge graph prior to enrichment.
    :param enrichments_dir: Directory containing individual enrichments.
    :param workflow_file: Reference to the Snakemake workflow.
    :param output_dir: The output directory to store the RO-Crate metadata file.
    """
    crate = ROCrate()

    crate.name = "WorkflowHub Knowledge Graph"
    crate.description = (
        "This RO-Crate contains a knowledge graph built from RO-Crates "
        "on WorkflowHub, enriched with metadata from additional sources. "
        "The source code used to create the knowledge graph, including the enrichments, "
        "is also included."
    )

    org_uniman = crate.add(
        ContextEntity(
            crate,
            "https://ror.org/027m9bs27",
            properties={"@type": "Organization", "name": "University of Manchester"},
        )
    )
    org_geneva = crate.add(
        ContextEntity(
            crate,
            "https://ror.org/01swzsf04",
            properties={"@type": "Organization", "name": "University of Geneva"},
        )
    )
    org_epfl = crate.add(
        ContextEntity(
            crate,
            "https://ror.org/02s376052",
            properties={
                "@type": "Organization",
                "name": "École Polytechnique Fédérale de Lausanne",
            },
        )
    )

    # Add authors:
    auth_alex = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0003-1193-6632",
            properties={
                "givenName": "Alexander",
                "familyName": "Hambley",
            },
        )
    )
    auth_alex["affiliation"] = org_uniman
    auth_eli = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0002-0035-6475",
            properties={
                "givenName": "Eli",
                "familyName": "Chadwick",
            },
        )
    )
    auth_eli["affiliation"] = org_uniman
    auth_oliver = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0002-4565-9760",
            properties={
                "givenName": "Oliver",
                "familyName": "Woolland",
            },
        )
    )
    auth_oliver["affiliation"] = org_uniman
    auth_stian = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0001-9842-9718",
            properties={
                "givenName": "Stian",
                "familyName": "Soiland-Reyes",
            },
        )
    )
    auth_stian["affiliation"] = org_uniman
    auth_volodymyr = crate.add(
        Person(
            crate,
            "https://orcid.org/0000-0001-6353-0808",
            properties={
                "givenName": "Volodymyr",
                "familyName": "Savchenko",
            },
        )
    )
    auth_volodymyr["affiliation"] = [org_geneva, org_epfl]

    crate.root_dataset["author"] = [
        auth_alex,
        auth_eli,
        auth_oliver,
        auth_stian,
        auth_volodymyr,
    ]

    # Add dataset and files:
    crate.add_dataset(
        "/app/workflowhub_graph/",
        properties={
            "@type": ["Dataset", "SoftwareSourceCode"],
            "name": "WorkflowHub Graph source code",
            "description": "A directory containing modules used by the workflow.",
        },
    )

    crate.add_file(
        "/app/Dockerfile",
        properties={
            "@type": "File",
            "name": "Dockerfile",
            "encodingFormat": "text/plain",
            "description": "The Dockerfile used to build the Docker images for the workflow.",
            "conformsTo": {"@id": "https://docs.docker.com/reference/dockerfile/"},
        },
    )

    crate.add_file("/app/README.md")

    config_file = crate.add_file(
        "/app/config.yaml",
        properties={
            "name": "Workflow configuration",
            "description": "YAML file containing the configuration of parameters used for the workflow execution.",
            "encodingFormat": "application/yaml",
        },
    )

    # Add data and workflow entities:
    full_graph_entity = crate.add_file(
        full_graph_file,
        properties={
            "name": "Enriched WorkflowHub Knowledge Graph",
            "description": "This file contains merged RDF triples from multiple RO-Crates sourced from WorkflowHub, enriched with metadata from related sources.",
            "encodingFormat": "text/turtle",
        },
    )

    full_graph_entity["author"] = [
        auth_alex,
        auth_eli,
        auth_oliver,
        auth_stian,
        auth_volodymyr,
    ]

    # Add data and workflow entities:
    enrichment_files = crate.add_dataset(
        enrichments_dir,
        properties={
            "name": "Graph enrichment files",
            "description": "This directory contains RDF files for each enrichment strategy. These files are combined with the base graph to create the final knowledge graph.",
            "encodingFormat": "text/turtle",
        },
    )

    # Add data and workflow entities:
    base_graph_entity = crate.add_file(
        base_graph_file,
        properties={
            "name": "Base WorkflowHub knowledge graph",
            "description": "This file contains merged RDF triples from multiple RO-Crates sourced from WorkflowHub, before enrichment.",
            "encodingFormat": "text/turtle",
        },
    )

    full_graph_entity["isBasedOn"] = [enrichment_files, base_graph_entity]

    # workflow
    # add parameters
    config_file_param = crate.add(
        ContextEntity(
            crate,
            "#param-config",
            properties={
                "@type": "FormalParameter",
                "additionalType": "File",
                "name": "configfile",
                "description": "A YAML file with parameter configuration for the workflow.",
                "encodingFormat": "application/yaml",
                "valueRequired": True,
            },
        )
    )
    config_file_param["workExample"] = config_file
    config_file["exampleOfWork"] = config_file_param
    full_graph_file_param = crate.add(
        ContextEntity(
            crate,
            "#param-full-graph-file",
            properties={
                "@type": "FormalParameter",
                "additionalType": "File",
                "name": "Full knowledge graph RDF",
                "description": "An RDF file containing the full knowledge graph.",
                "encodingFormat": "text/turtle",
            },
        )
    )
    full_graph_file_param["workExample"] = full_graph_entity
    full_graph_entity["exampleOfWork"] = full_graph_file_param
    base_graph_file_param = crate.add(
        ContextEntity(
            crate,
            "#param-base-graph-file",
            properties={
                "@type": "FormalParameter",
                "additionalType": "File",
                "name": "Base knowledge graph RDF",
                "description": "An RDF file containing the base knowledge graph prior to enrichment.",
                "encodingFormat": "text/turtle",
            },
        )
    )
    base_graph_file_param["workExample"] = base_graph_entity
    base_graph_entity["exampleOfWork"] = base_graph_file_param
    enrichment_files_param = crate.add(
        ContextEntity(
            crate,
            "#param-graph-enrichment-files",
            properties={
                "@type": "FormalParameter",
                "additionalType": "Dataset",
                "name": "Enrichment outputs",
                "description": "RDF files containing the outputs of each enrichment strategy.",
                "encodingFormat": "text/turtle",
            },
        )
    )
    enrichment_files_param["workExample"] = enrichment_files
    enrichment_files["exampleOfWork"] = enrichment_files_param
    ro_crate_param = crate.add(
        ContextEntity(
            crate,
            "#param-ro-crate",
            properties={
                "@type": "FormalParameter",
                "additionalType": "Dataset",
                "name": "RO-Crate output",
                "description": "An RO-Crate containing the workflow and its outputs.",
            },
        )
    )
    enrichment_files_param["workExample"] = crate.root_dataset
    crate.root_dataset["exampleOfWork"] = ro_crate_param

    workflow_entity = crate.add_workflow(
        source=workflow_file,
        properties={
            "name": "Snakemake Workflow",
            "description": "This is the Snakemake workflow used to generate the merged RDF triples.",
        },
        main=True,
        lang="snakemake",
    )

    workflow_entity["author"] = [auth_alex, auth_eli, auth_oliver, auth_stian]
    workflow_entity["input"] = config_file_param
    workflow_entity["output"] = [
        full_graph_file_param,
        base_graph_file_param,
        enrichment_files_param,
    ]

    # workflow execution action
    execution = crate.add_action(
        instrument=workflow_entity,
        identifier=f"#workflow-run-{uuid.uuid4()}",
        object=config_file,
        result=[full_graph_entity, base_graph_entity, enrichment_files],
        properties={"name": "Run of knowledge graph creation workflow"},
    )

    # add conforms to WRROC
    wrroc_profile = crate.add(
        ContextEntity(
            crate,
            "https://w3id.org/ro/wfrun/workflow/0.5",
            properties={
                "@type": "CreativeWork",
                "name": "Workflow Run Crate",
                "version": "0.4",
            },
        )
    )

    crate.root_dataset.append_to("conformsTo", wrroc_profile)

    # Add license:
    license = crate.add(
        ContextEntity(
            crate,
            "https://spdx.org/licenses/BSD-2-Clause.html",
            properties={
                "@type": "CreativeWork",
                "name": 'BSD 2-Clause "Simplified" License',
            },
        )
    )
    crate.license = license

    # Writing the RO-Crate metadata:
    crate.write(output_dir)

    # remove package build files from crate
    shutil.rmtree(os.path.join(output_dir, "workflowhub_graph", "build"))
    shutil.rmtree(
        os.path.join(output_dir, "workflowhub_graph", "workflowhub_graph.egg-info")
    )


def main():

    parser = argparse.ArgumentParser(description="Create RO-Crate for the RDF graph.")
    parser.add_argument(
        "--full-graph", help="The full (enriched) RDF graph file.", required=True
    )
    parser.add_argument("--base-graph", help="The base RDF graph file.", required=True)
    parser.add_argument(
        "--enrichments-dir",
        help="Directory containing enrichment files.",
        required=True,
    )
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
    full_graph_file = args.full_graph
    base_graph_file = args.base_graph
    enrichments_dir = args.enrichments_dir
    workflow_file = args.workflow_file
    output_dir = args.output_dir

    create_ro_crate(
        full_graph_file=full_graph_file,
        base_graph_file=base_graph_file,
        enrichments_dir=enrichments_dir,
        workflow_file=workflow_file,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    main()
