import argparse
import os
import traceback

import requests
from io import BytesIO
from zipfile import ZipFile

from workflowhub_graph.constants import (
    TARGET_FILE_NAME,
    WORKFLOWS_URL,
    METADATA_ENDPOINT,
    BASE_URL,
    ZIP_ENDPOINT,
    BASE_URL_DEV,
)


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
    workflows_data: dict, output_dir: str = "data", is_metadata_endpoint: bool = False
) -> None:
    """
    Utilises the JSON file downloaded by download_workflow_ids(). This file is used to download a list
    of 'ro-crate-metadata.json' files for each workflow ID.

    :param workflows_data: The data containing workflow IDs and other information.
    :param output_dir: Directory to save the extracted JSON files. By default, this is 'data'.
    :param is_metadata_endpoint: A boolean flag to determine if method should call
        download_and_extract_json_from_zip() or download_and_extract_json_from_metadata_endpoint().
    """
    os.makedirs(output_dir, exist_ok=True)

    n_successful = 0

    try:
        workflows = workflows_data.get("data", [])

        for i_workflow, workflow in enumerate(workflows):
            workflow_id = workflow["id"]

            print(
                f"Processing workflow ID {workflow_id} ({i_workflow + 1}/{len(workflows)})..."
            )

            # TODO: Remove dev WorkflowHub URL:
            if is_metadata_endpoint:
                endpoint = METADATA_ENDPOINT.format(w_id=workflow_id)
                json_content = download_and_extract_json_from_metadata_endpoint(
                    BASE_URL_DEV + endpoint
                )
            else:
                # TODO: Where does version come from?
                endpoint = ZIP_ENDPOINT.format(w_id=workflow_id, w_version=1)
                json_content = download_and_extract_json_from_zip(BASE_URL + endpoint)

            if json_content:
                output_file_path = os.path.join(
                    output_dir, f"{workflow_id}_ro-crate-metadata.json"
                )
                with open(output_file_path, "wb") as output_file:
                    output_file.write(json_content)
                print(f"Content saved to {output_file_path}")
                n_successful += 1

            else:
                print(f"Failed to process workflow ID {workflow_id}")

    except Exception as e:
        print(f"An error occurred while processing workflow IDs. Error: {e}")
        traceback.print_exc()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--workflows-url",
        type=str,
        default=WORKFLOWS_URL,
        help="URL of the JSON file containing workflow IDs.",
    )
    argparser.add_argument(
        "--worklow-ids",
        type=str,
        default="-",
        help="Range of workflow IDs to process. Use a hyphen to specify a range, e.g. 1-10.",
    )
    args = argparser.parse_args()

    min_workflow_id, max_workflow_id = args.worklow_ids.split("-")

    # Example usage:
    workflows_ids = download_workflow_ids(args.workflows_url)

    if min_workflow_id != "":
        workflows_ids["data"] = [
            workflow
            for workflow in workflows_ids["data"]
            if int(workflow["id"]) >= int(min_workflow_id)
        ]

    if max_workflow_id != "":
        workflows_ids["data"] = [
            workflow
            for workflow in workflows_ids["data"]
            if int(workflow["id"]) <= int(max_workflow_id)
        ]

    # Check if root key 'data' exists
    if workflows_ids and "data" in workflows_ids:
        process_workflow_ids(workflows_ids, is_metadata_endpoint=True)


if __name__ == "__main__":
    main()
