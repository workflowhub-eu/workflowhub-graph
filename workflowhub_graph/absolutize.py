import argparse
import json
import arcp

def make_paths_absolute(json_data: dict, workflowhub_url: str, workflow_id: int) -> dict:
    """
    Makes all paths in the JSON content absolute.

    :param json_content: The JSON content as a dictionary.
    """

    # TODO: where version comes from?
    workflow_url = f"{workflowhub_url}/workflows/{workflow_id}/ro_crate?version=1"

    if "@context" not in json_data:
        raise ValueError("The JSON content does not contain a '@context' key, refusing to add it, can not absolutize paths")

    if not isinstance(json_data["@context"], list):
        json_data["@context"] = [json_data["@context"]]

    if any(isinstance(item, dict) and "@base" in item for item in json_data["@context"]):
        raise ValueError("The JSON content already contains an '@base' key, it was probably already processed.")
    
    json_data["@context"].append({"@base": arcp.arcp_location(workflow_url)})

    return json_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make all paths in a JSON file absolute.")
    parser.add_argument("json_file", help="The JSON file to process.")
    parser.add_argument("output_file", help="The output file.")
    parser.add_argument("workflow_id", help="The WorkflowHub ID.")
    parser.add_argument("-u", "--workflowhub-url", help="The WorkflowHub URL.", default="https://workflowhub.eu")

    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        json_data = json.load(f)

    processed_json_data = make_paths_absolute(json_data, args.workflowhub_url, args.workflow_id)

    if args.output_file == "-":
        print(json.dumps(processed_json_data, indent=2))
    else:
        with open(args.output_file, "w") as f:
            json.dump(processed_json_data, f, indent=2)