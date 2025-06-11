from snakemake.io import directory

configfile: "config.yaml"

rule all:
    input:
        # Final output file
        f"{config['paths']['output-dir']}/{config['filenames']['output-graph']}",

        # Metadata
        #directory(f"{config['paths']['run-metadata']}/"),

rule source_ro_crates:
    output:
        f"{config['paths']['output-dir']}/{config['filenames']['sourced-list']}"
    params: 
        max_workflow_id = config['constraints']['max-workflow-id'],
        output_dir = config['paths']['output-dir']
    shell:
        "source-crates "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--output-dir {params.output_dir} "
        "--prod "
        "--all-versions"

rule validate_ro_crates:
    input:
        f"{config['paths']['output-dir']}/{config['filenames']['sourced-list']}"
    output:
        f"{config['paths']['output-dir']}/{config['filenames']['validated-list']}"
    params: 
        max_workflow_id = config['constraints']['max-workflow-id'],
        versions = config['constraints']['versions'],
        output_dir = config['paths']['output-dir'],
        validated_list = config['filenames']['validated-list']
    shell:
        "check-outputs "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--versions {params.versions} "
        "--output {params.output_dir}/{params.validated_list} "

rule create_graph:
    input:
        f"{config['paths']['output-dir']}/{config['filenames']['validated-list']}"
    output:
        f"{config['paths']['output-dir']}/{config['filenames']['output-graph']}"
    shell:
        "merge "
        "{output} "
        "-i '{input}'"
