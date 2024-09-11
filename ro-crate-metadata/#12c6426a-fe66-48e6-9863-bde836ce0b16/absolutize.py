import argparse
import copy
import json
from urllib.parse import urlparse
import arcp
import rdflib


# TODO: following https://github.com/workflowhub-eu/workflowhub-graph/issues/12
#       builing upon is_all_absolute
#       add extended RO-Crate profile validation
#       get information like schema.org domain and check if the graph is compliant with the schema
#       normative schema.org dev docs: https://schema.org/docs/developers.html
#       make a note for validation of the graph


def is_all_absolute(G: rdflib.Graph) -> bool:
    for triple in G:
        for item in triple:
            if isinstance(item, rdflib.URIRef):
                # TODO: is this enough?
                parsed = urlparse(item)

                # we accept file:// with a netloc, even if netloc is not a FQDN,
                # see https://github.com/workflowhub-eu/workflowhub-graph/issues/1#issuecomment-2127351752
                if parsed.netloc == "" and parsed.scheme != "mailto":
                    print(
                        f"found non-absolute path <{item}> {parsed.netloc}, {urlparse(item)}"
                    )
                    return False
    return True


def make_paths_absolute(
    json_data: dict, workflowhub_url: str, workflow_id: int, workflow_version: int
) -> dict:
    """
    Makes all paths in the JSON content absolute by adding an '@base' key to the JSON-LD context.

    :param json_data: The JSON content as a dictionary.
    :param workflowhub_url: The base URL for WorkflowHub.
    :param workflow_id: The workflow ID to construct the absolute paths.
    :param workflow_version: The workflow version.
    :return: The modified JSON content with absolute paths.
    :raises ValueError: If '@context' key is missing or if '@base' key already exists in the JSON content.
    """

    json_data = copy.deepcopy(json_data)

    workflow_url = (
        f"{workflowhub_url}/workflows/{workflow_id}/ro_crate?version={workflow_version}"
    )

    if "@context" not in json_data:
        raise ValueError(
            "The JSON content does not contain a '@context' key, refusing to add it, can not absolutize paths"
        )

    if not isinstance(json_data["@context"], list):
        json_data["@context"] = [json_data["@context"]]

    if any(
        isinstance(item, dict) and "@base" in item for item in json_data["@context"]
    ):
        raise ValueError(
            "The JSON content already contains an '@base' key, it was probably already processed."
        )

    json_data["@context"].append({"@base": arcp.arcp_location(workflow_url)})

    return json_data


def main():
    parser = argparse.ArgumentParser(
        description="Make all paths in a JSON file absolute."
    )
    parser.add_argument("json_file", help="The JSON file to process.")
    parser.add_argument("output_file", help="The output file.")
    parser.add_argument("workflow_id", help="The Workflow ID.")
    parser.add_argument("workflow_version", help="The Workflow version.")
    parser.add_argument(
        "-u",
        "--workflowhub-url",
        help="The WorkflowHub URL.",
        default="https://workflowhub.eu",
    )

    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        json_data = json.load(f)

    processed_json_data = make_paths_absolute(
        json_data, args.workflowhub_url, args.workflow_id, args.workflow_version
    )

    if args.output_file == "-":
        print(json.dumps(processed_json_data, indent=2))
    else:
        with open(args.output_file, "w") as f:
            json.dump(processed_json_data, f, indent=2)


if __name__ == "__main__":
    main()
