from snakemake.io import directory

configfile: "config.yaml"

rule all:
    input:
        # Final output file
        f"{config['output-dir']}/{config['output-graph']}",

        # Enrichment outputs
        expand("{output_dir}/{enrichment_dir}/{strategy}.ttl",
               output_dir=config['output-dir'],
               enrichment_dir=config['enrichment-output-dir'],
               strategy=config['enrichment-strategies']),

        # Metadata
        #directory(f"{config['paths']['run-metadata']}/"),

        # RO-Crate
        f"{config['output-dir']}/crate/ro-crate-metadata.json"

rule source_ro_crates:
    output:
        f"{config['output-dir']}/{config['sourced-list']}"
    params: 
        max_workflow_id = config['max-workflow-id'],
        output_dir = config['output-dir'],
        base_url = config['base-url']
    shell:
        "source-crates "
        "--workflow-ids 1-{params.max_workflow_id} "
        "--output-dir {params.output_dir} "
        "--base-url {params.base_url} "

rule create_graph:
    input:
        f"{config['output-dir']}/{config['sourced-list']}"
    output:
        f"{config['output-dir']}/{config['base-graph']}"
    params: 
        base_url = config['base-url'],
        files_path = config['output-dir']
    shell:
        "merge "
        "{output} "
        "-i '{input}' "
        "--files-path '{params.files_path}' "
        "--base-url '{params.base_url}' "

rule enrich_graph:
    input:
        f"{config['output-dir']}/{config['base-graph']}"
    output:
        f"{config['output-dir']}/{config['enrichment-output-dir']}/{{strategy}}.ttl"
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
            f"{config['output-dir']}/{config['enrichment-output-dir']}/{{strategy}}.ttl",
            strategy=config['enrichment-strategies']
        )
    output:
        merged=f"{config['output-dir']}/{config['merged-graph']}"
    shell:
        """
        rdfpipe --input-format=turtle --output-format=turtle \
            {input.base} {input.fragments} > {output.merged}
        """

rule consolidate:
    input:
        merged=f"{config['output-dir']}/{config['merged-graph']}"
    output:
        consolidated=f"{config['output-dir']}/{config['output-graph']}"
    shell:
        """
        consolidate \
        --input-file {input.merged} \
        --output-filename {output.consolidated}
        """
        
rule create_ro_crate:
    input:
        full_graph = f"{config['output-dir']}/{config['output-graph']}",
        base_graph = f"{config['output-dir']}/{config['base-graph']}"
    params:
        enrichments_dir = f"{config['output-dir']}/{config['enrichment-output-dir']}/",
        workflow_file = "/app/Snakefile",
        output_dir = f"{config['output-dir']}/crate"
    output:
        f"{config['output-dir']}/crate/ro-crate-metadata.json"
    shell:
        """
        create-ro-crate \
        --full-graph {input.full_graph} \
        --base-graph {input.base_graph} \
        --enrichments-dir {params.enrichments_dir} \
        --workflow-file {params.workflow_file} \
        --output-dir {params.output_dir}
        """