from snakemake.io import directory

configfile: "config.yaml"

rule all:
    input:
        # Final output file
        f"{config['output-dir']}/{config['output-graph']}",

        # Enrichment outputs
        expand("{output_dir}/{strategy}.ttl",
               output_dir=config['output-dir'],
               strategy=config['enrichment-strategies']),

        # Metadata
        #directory(f"{config['paths']['run-metadata']}/"),

rule source_ro_crates:
    output:
        f"{config['output-dir']}/{config['sourced-list']}"
    params: 
        max_workflow_id = config['max-workflow-id'],
        output_dir = config['output-dir']
    shell:
        "source-crates "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--output-dir {params.output_dir} "
        "--prod "
        "--all-versions"

rule validate_ro_crates:
    input:
        f"{config['output-dir']}/{config['sourced-list']}"
    output:
        f"{config['output-dir']}/{config['validated-list']}"
    params: 
        max_workflow_id = config['max-workflow-id'],
        versions = config['versions'],
        output_dir = config['output-dir'],
        validated_list = config['validated-list']
    shell:
        "check-outputs "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--versions {params.versions} "
        "--output {params.output_dir}/{params.validated_list} "

rule create_graph:
    input:
        f"{config['output-dir']}/{config['validated-list']}"
    output:
        f"{config['output-dir']}/{config['output-graph']}"
    shell:
        "merge "
        "{output} "
        "-i '{input}'"

rule enrich_graph:
    input:
        f"{config['output-dir']}/{config['output-graph']}"
    output:
        f"{config['output-dir']}/{{strategy}}.ttl"
    shell:
        """
        enrich-graph \
        --graph {input} \
        --strategy {wildcards.strategy} \
        --output {output}
        """
