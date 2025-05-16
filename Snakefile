from snakemake.io import directory

configfile: "config.yaml"

rule all:
    output:
        # Final output file
        f"{config['paths']['output-dir']}/{config['filenames']['output-graph']}",

        # Metadata
        directory(f"{config['paths']['run-metadata']}/"),

rule prepare_metadata_dir:
    output:
        directory(config["paths"]["run-metadata"])
    shell:
        "mkdir -p {output}"

rule source_ro_crates:
    output:
        directory(f"{config['paths']['output-dir']}/{config['filenames']['extracted-crates']}")
    params: 
        max_workflow_id = config['constraints']['max-workflow-id']
    shell:
        "python workflowhub_graph/source_crates.py "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--prod "
        "--all-versions"

rule validate_ro_crates:
    input:
        directory(f"{config['paths']['output-dir']}/{config['filenames']['extracted-crates']}")
    output:
        f"{config['paths']['output-dir']}/{config['filenames']['validated-list']}"
    params: 
        max_workflow_id = config['constraints']['max-workflow-id'],
        versions = config['constraints']['versions'],
        output_dir = config['paths']['output-dir']
    shell:
        "python workflowhub_graph/check_outputs.py "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--versions {params.versions} "
        "--output {params.output_dir}"

rule create_graph:
    input:
        f"{config['paths']['output-dir']}/{config['filenames']['validated-list']}"
    output:
        f"{config['paths']['output-dir']}/{config['filenames']['output-graph']}"
    shell:
        "python workflowhub_graph/merge.py {output} -i '{input}'"
