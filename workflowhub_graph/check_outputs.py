import argparse
import json
import os


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate list of created files based on workflow IDs and versions."
    )
    parser.add_argument(
        "--workflow-ids",
        type=str,
        required=True,
        help="Range of workflow IDs to process (e.g., '1-10').",
    )
    parser.add_argument(
        "--versions",
        type=str,
        required=True,
        help="Comma-separated list of versions to process (e.g., '1,2,3').",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory where the output files are stored (default: 'data').",
    )
    return parser.parse_args()


def generate_expected_files(
    output_dir: str, workflow_ids: range, versions: list[str]
) -> list[str]:
    """
    Generate a list of expected file paths based on the workflow IDs and versions.

    :param output_dir: The directory where output files are stored.
    :param workflow_ids: The range of workflow IDs to process.
    :param versions: The list of versions to process.

    :return: A list of expected file paths.
    """

    expected_files = []
    for wf_id in workflow_ids:
        for ver in versions:
            expected_files.append(f"{output_dir}/{wf_id}_{ver}_ro-crate-metadata.json")
    return expected_files


def verify_created_files(expected_files: list[str]) -> list[str]:
    """
    Verify which files from the list of expected files actually exist.

    :param expected_files: The list of expected file paths.
    :return: A list of file paths that actually exist.
    """
    return [f for f in expected_files if os.path.exists(f)]


def main():
    # Parse workflow IDs and versions:
    args = parse_args()
    min_id, max_id = map(int, args.workflow_ids.split("-"))
    workflow_ids = range(min_id, max_id + 1)
    versions = args.versions.split(",")

    # Generate expected file paths
    expected_files = generate_expected_files(args.output_dir, workflow_ids, versions)

    # Check which files were actually created
    created_files = verify_created_files(expected_files)

    # Output the list of created files to a JSON file
    with open("created_files.json", "w") as f:
        json.dump(created_files, f)

    print("Created files list written to created_files.json")
    print(f"Created files: {created_files}")


if __name__ == "__main__":
    main()
