# TODO - Refactor to input args to the Snakemake file
WORKFLOW_IDS = range(1,11)
VERSIONS = ['1']
OUTPUT_DIRS = "data"
MERGED_FILE = "merged.ttl"


def list_expected_files():
    files = []
    for wf_id in WORKFLOW_IDS:
        for ver in VERSIONS:
            files.append(f"{OUTPUT_DIRS}/{wf_id}_{ver}_ro-crate-metadata.json")
    return files

rule all:
    input:
        MERGED_FILE

rule source_ro_crates:
    output:
        "created_files.json"
    shell:
        """
        # Create the output directory if it doesn't exist:
        mkdir -p {OUTPUT_DIRS}

        # Run the source_crates script to download the RO Crate metadata:
        python workflowhub_graph/source_crates.py  --workflow-ids 1-10 --prod --all-versions

        # After sourcing, check which files were actually created:
        python workflowhub_graph/check_outputs.py --workflow-ids 1-10 --versions {VERSIONS} --output-dir {OUTPUT_DIRS}
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
