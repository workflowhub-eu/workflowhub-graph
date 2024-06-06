import os

import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()


BASE_URL_PROD = "https://workflowhub.eu"
WORKFLOWS_URL_PROD = "https://workflowhub.eu/workflows.json"

BASE_URL_DEV = "https://dev.workflowhub.eu"
WORKFLOWS_URL_DEV = "https://dev.workflowhub.eu/workflows.json"

# TODO: Why are we duplicating the URLs?
BASE_URL = BASE_URL_DEV
WORKFLOWS_URL = WORKFLOWS_URL_DEV

DOT_JSON_ENDPOINT = "/workflows/{w_id}.json"
METADATA_ENDPOINT = "/workflows/{w_id}/ro_crate_metadata?version={w_version}"
ZIP_ENDPOINT = "/workflows/{w_id}/ro_crate?version={w_version}"

TARGET_FILE_NAME = "ro-crate-metadata.json"
