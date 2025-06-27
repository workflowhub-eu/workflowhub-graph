import argparse
import json
import os
import re


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
        help="Range of workflow IDs to process (e.g., '1-10').",
    )
    parser.add_argument(
        "--versions",
        type=str,
        required=True,
        help="Comma-separated list of versions to process (e.g., '1,2,3').",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/created_files.json",
        help="Path to output file (default: 'data/created_files.json').",
    )
    return parser.parse_args()


def get_max_id_from_files(output_dir: str) -> int:
    """
    If no workflow ID parameter is provided, get the maximum workflow ID from the files in the output directory.

    :param output_dir: The directory where output files are stored.
    :return: The maximum workflow ID.
    """
    max_id = 0
    pattern = re.compile(r"^(\d+)_\d+_ro-crate-metadata\.json$")
    for filename in os.listdir(output_dir):
        match = pattern.match(filename)
        if match:
            wf_id = int(match.group(1))
            if wf_id > max_id:
                max_id = wf_id
    return max_id


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
    args = parse_args()
    output_dir = os.path.dirname(args.output)

    if args.workflow_ids:
        min_id, max_id = map(int, args.workflow_ids.split("-"))
        if max_id == 0:
            max_id = get_max_id_from_files(output_dir)
        workflow_ids = range(min_id, max_id + 1)
    else:
        max_id = get_max_id_from_files(output_dir)
        workflow_ids = range(1, max_id + 1)

    versions = args.versions.split(",")

    # Generate expected file paths
    expected_files = generate_expected_files(output_dir, workflow_ids, versions)

    # Check which files were actually created
    created_files = verify_created_files(expected_files)

    # Output the list of created files to a JSON file
    with open(args.output, "w") as f:
        json.dump(created_files, f)

    print(f"Created files saved to {args.output}")


if __name__ == "__main__":
    main()
