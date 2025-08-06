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

        # RO-Crate
        f"{config['output-dir']}/ro-crate-metadata.json"

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
        f"{config['output-dir']}/{config['base-graph']}"
    shell:
        "merge "
        "{output} "
        "-i '{input}'"

rule enrich_graph:
    input:
        f"{config['output-dir']}/{config['base-graph']}"
    output:
        f"{config['output-dir']}/{{strategy}}.ttl"
    shell:
        """
        enrich-graph \
        --graph {input} \
        --strategy {wildcards.strategy} \
        --output-file {output}
        """

rule merge_graphs:
    input:
        base=f"{config['output-dir']}/{config['base-graph']}",
        fragments=expand(
            f"{config['output-dir']}/{{strategy}}.ttl",
            strategy=config['enrichment-strategies']
        )
    output:
        merged=f"{config['output-dir']}/{config['output-graph']}"
    shell:
        """
        rdfpipe --input-format=turtle --output-format=turtle \
            {input.base} {input.fragments} > {output.merged}
        """

rule create_ro_crate:
    input:
        f"{config['output-dir']}/{config['output-graph']}"
    params:
        workflow_file = "Snakefile",
        output_dir = f"{config['output-dir']}"
    output:
        f"{config['output-dir']}/ro-crate-metadata.json"
    shell:
        """
        create-ro-crate \
        --input-file {input} \
        --workflow-file {params.workflow_file} \
        --output-dir {params.output_dir}
        """
        
