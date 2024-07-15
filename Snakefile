WORKFLOW_IDS = range(1,11)
VERSIONS = ['1']
OUTPUT_DIRS = "data"
MERGED_FILE = "merged.ttl"


rule all:
    input:
        MERGED_FILE

# TODO - Refactor to input args to the Snakemake file. I.e. replace WORKFLOW_IDS and VERSIONS with input args.
rule source_ro_crates:
    output:
        "created_files.json"
    shell:
        """
        # Create the output directory if it doesn't exist:
        mkdir -p {OUTPUT_DIRS}
        
        # Add the current directory to PYTHONPATH, creating it if it doesn't exist
        export PYTHONPATH="${{PYTHONPATH:+$PYTHONPATH:}}$(pwd)"

        # Run the source_crates script to download the RO Crate metadata, 
        # then check the output files and generate created_files.json:
        
        # - all versions of all workflows:
        python workflowhub_graph/source_crates.py --prod --all-versions
        python workflowhub_graph/check_outputs.py --versions {VERSIONS} --output-dir {OUTPUT_DIRS}
        
        # - all versions of first 10 workflows:
        # python workflowhub_graph/source_crates.py --workflow-ids 1-10 --prod --all-versions
        # python workflowhub_graph/check_outputs.py --workflow-ids 1-10 --versions {VERSIONS} --output-dir {OUTPUT_DIRS}
        """

rule report_created_files:
    input:
        "created_files.json"
    shell:
        """
        echo "Files created:"
        cat created_files.json
        """

rule merge_files:
    input:
        "created_files.json"
    output:
        MERGED_FILE
    run:
        import json
        import os

        # Load the list of created files:
        with open("created_files.json") as f:
            created_files = json.load(f)

        files_to_merge = [f"data/{os.path.basename(file)}" for file in created_files]

        # If no files are available to merge, raise an exception:
        if not files_to_merge:
            raise ValueError("No files in to merge in data directory.")

        file_patterns = " ".join(files_to_merge)

        # Merge the JSON-LD files into a single RDF graph and output as a TTL file
        shell(f"""
            python workflowhub_graph/merge.py {output[0]} -p "data/*.json"
        """)
