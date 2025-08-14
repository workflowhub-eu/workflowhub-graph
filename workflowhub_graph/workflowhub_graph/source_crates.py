import argparse
import json
import os
import sys
import traceback

import requests
from io import BytesIO
from zipfile import ZipFile

from workflowhub_graph.cli import update_progress_bar
from workflowhub_graph.constants import (
    DOT_JSON_ENDPOINT,
    TARGET_FILE_NAME,
    METADATA_ENDPOINT,
    ZIP_ENDPOINT,
)


def get_dot_json_endpoint(target_url: str) -> dict | None:
    """
    Returns the endpoint to download a JSON file from WorkflowHub.

    :param target_url: URL of the JSON file.
    :return: The endpoint to download the JSON file or None.
    """
    try:
        response = requests.get(target_url)
        response.raise_for_status()

        if "application/vnd.api+json" in response.headers["Content-Type"]:
            return response.json()
        else:
            print(f"No JSON file found at: '{target_url}'")
            return None

    except requests.RequestException as e:
        print(f"Failed to download the JSON file from {target_url}. Error: {e}")
        return None
    except Exception as e:
        print(
            f"An error occurred while downloading the JSON file from {target_url}. Error: {e}"
        )
        return None


def download_and_extract_json_from_metadata_endpoint(target_url: str) -> bytes | None:
    """
    Downloads a JSON file from WorkflowHub (or specified URL) of a specific workflow and returns its content.

    :param target_url: URL of the JSON file to download.
    :return: Returns either the JSON content, or None if no file was found.
    """
    try:
        response = requests.get(target_url)
        response.raise_for_status()

        # Check if the response is a JSON file:
        if "application/json" in response.headers["Content-Type"]:
            return response.content
        else:
            print(f"No JSON file found at: '{target_url}'")
            return None
    except requests.RequestException as e:
        print(f"Failed to download the JSON file from {target_url}. Error: {e}")
        return None
    except Exception as e:
        print(
            f"An error occurred while downloading the JSON file from {target_url}. Error: {e}"
        )
        return None


def download_and_extract_json_from_zip(
    target_url: str, target_file_name: str = TARGET_FILE_NAME
) -> bytes | None:
    """
    Downloads a zip file from WorkflowHub (or specified URL), extracts JSON metadata file and returns its content.
    This method only saves target_file_name to disk.

    :param target_url: URL of the zip file to download.
    :param target_file_name: Name of the file to extract from the zip. By default is TARGET_FILE_NAME.
    :return: Returns either the content of the extracted file, or None if no file was found.
    """
    try:
        response = requests.get(target_url, stream=True)

        if response.status_code == 200:
            zip_file = BytesIO()
            for chunk in response.iter_content(chunk_size=128):
                zip_file.write(chunk)
            zip_file.seek(0)

            with ZipFile(zip_file, "r") as z:
                if target_file_name in z.namelist():
                    with z.open(target_file_name) as target_file:
                        return target_file.read()
                else:
                    print(
                        f"No file named: '{target_file_name}' found in the zip archive"
                    )
                    return None
        else:
            print(
                f"Failed to download the zip file. Status code: {response.status_code}"
            )
            return None
    except requests.RequestException as e:
        print(f"Failed to download the zip archive from {target_url}. Error: {e}")
        return None
    except Exception as e:
        print(
            f"An error occurred while processing the zip archive from {target_url}. Error: {e}"
        )
        return None


def download_workflow_ids(json_url: str) -> dict | None:
    """
    Downloads a JSON file from WorkflowHub that contains a list of publicly available workflows, and returns its
    content as a dictionary.

    :param json_url: The URL of the JSON file.
    :return: A dictionary of WorkflowHub IDs, or None if the download failed.
    """
    print(f"Downloading workflow IDs from {json_url}...")
    try:
        response = requests.get(json_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to download the JSON file from {json_url}. Error: {e}")
        return None
    except Exception as e:
        print(
            f"An error occurred while downloading the JSON file from {json_url}. Error: {e}"
        )
        return None


def process_workflow_ids(
    workflows_data: dict,
    output_dir: str = "data",
    is_metadata_endpoint: bool = False,
    base_url: str = "https://dev.workflowhub.eu",
    all_versions: bool = False,
) -> None:
    """
    Utilises the JSON file downloaded by download_workflow_ids(). This file is used to download a list
    of 'ro-crate-metadata.json' files for each workflow ID.

    :param workflows_data: The data containing workflow IDs and other information.
    :param output_dir: Directory to save the extracted JSON files. By default, this is 'data'.
    :param is_metadata_endpoint: A boolean flag to determine if method should call
        download_and_extract_json_from_zip() or download_and_extract_json_from_metadata_endpoint().
    :param base_url: The base URL.
    :param all_versions: A boolean flag to determine if all versions of a workflow should be processed.
    """
    os.makedirs(output_dir, exist_ok=True)

    n_successful = 0
    manifest = []

    try:
        workflows = workflows_data.get("data", [])

        for i_workflow, workflow in enumerate(workflows):
            workflow_id = workflow["id"]

            update_progress_bar(i_workflow + 1, len(workflows))

            workflow_json = get_dot_json_endpoint(
                base_url + DOT_JSON_ENDPOINT.format(w_id=workflow_id)
            )

            try:
                if all_versions:
                    workflow_versions = [
                        workflow_version_dict["version"]
                        for workflow_version_dict in workflow_json["data"][
                            "attributes"
                        ]["versions"]
                    ]
                else:
                    workflow_versions = [
                        workflow_json["data"]["attributes"]["latest_version"]
                    ]
            except (KeyError, TypeError):
                print(
                    f"Failed to extract workflow versions from:\n",
                    json.dumps(workflow_json, indent=4),
                )
                continue

            for w_version in workflow_versions:
                if is_metadata_endpoint:
                    endpoint = METADATA_ENDPOINT.format(
                        w_id=workflow_id, w_version=w_version
                    )
                    json_content = download_and_extract_json_from_metadata_endpoint(
                        base_url + endpoint
                    )
                else:
                    endpoint = ZIP_ENDPOINT.format(
                        w_id=workflow_id, w_version=w_version
                    )
                    json_content = download_and_extract_json_from_zip(
                        base_url + endpoint
                    )

                if json_content:
                    filename = f"{workflow_id}_{w_version}_ro-crate-metadata.json"
                    output_file_path = os.path.join(
                        output_dir, filename
                    )
                    with open(output_file_path, "wb") as output_file:
                        output_file.write(json_content)

                    # Append filename to the manifest
                    manifest.append(filename)
                    n_successful += 1

                else:
                    print(f"Failed to process workflow ID {workflow_id}")

    except Exception as e:
        print(f"An error occurred while processing workflow IDs. Error: {e}")
        traceback.print_exc()

    finally:
        # Save the manifest to a JSON file
        manifest_file_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_file_path, "w") as manifest_file:
            json.dump(manifest, manifest_file, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workflow-ids",
        type=str,
        help="Range of workflow IDs to process. Use a hyphen to specify a range, e.g. 1-10. "
        "If not provided, all IDs will be processed.",
    )
    parser.add_argument(
        "--zip",
        default=False,
        action="store_true",
        help="Download and extract JSON files from zip archive.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory to save the extracted JSON files. By default, this is 'data'.",
    )

    # TODO: Change this to `dev` to use the development WorkflowHub:
    parser.add_argument(
        "-b",
        "--base-url",
        type=str,
        default="https://dev.workflowhub.eu",
        help="The WorkflowHub URL to use.",
    )
    parser.add_argument(
        "--all-versions",
        default=False,
        action="store_true",
        help="Download all versions of an RO Crate. If not set, only the latest version will be downloaded.",
    )

    args = parser.parse_args()

    # Set workflow URL
    workflows_url = f"{args.base_url}/workflows.json"
    
    # Example usage:
    all_workflow_ids = download_workflow_ids(workflows_url)
    filtered_workflows = all_workflow_ids["data"] # initialise with all workflows

    if args.workflow_ids: # no filtering if option not used
        min_str, max_str = args.workflow_ids.split("-")
        min_workflow_id = int(min_str) if min_str else None
        max_workflow_id = int(max_str) if max_str else None
        
        if (max_workflow_id != 0): # no filtering if max id 0
            filtered_workflows = []
            for workflow in all_workflow_ids["data"]:
                w_id = int(workflow["id"])
                if (w_id >= min_workflow_id) and (w_id <= max_workflow_id):
                    filtered_workflows.append(workflow)

    if not filtered_workflows:
        raise ValueError("No workflows matched the provided workflow ID range.")
    
    process_workflow_ids(
        {"data": filtered_workflows},
        is_metadata_endpoint=not args.zip,
        base_url=args.base_url,
        all_versions=args.all_versions,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
