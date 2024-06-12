import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Provide help and examples for the workflowhub graph builder."
    )
    args = parser.parse_args()

    # Print a list of poetry scripts
    print(
        """
        The following commands are available:

        - 'source-crates': Download ROCrates from the WorkflowHub API.
        - 'absolutize': Make all paths in an ROCrate absolute.
        - 'upload': Upload an ROCrate to Zenodo.
        - 'merge': Merge multiple ROCrates into an RDF graph.
        """
    )

if __name__ == "__main__":
    main()
