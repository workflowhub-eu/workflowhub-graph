import os

import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()


BASE_URL = "https://workflowhub.eu"
BASE_URL_DEV = "https://dev.workflowhub.eu"
METADATA_ENDPOINT = "/workflows/{w_id}/ro_crate_metadata"
ZIP_ENDPOINT = "/workflows/{w_id}/ro_crate"

TARGET_FILE_NAME = "ro-crate-metadata.json"
WORKFLOWS_URL = "https://workflowhub.eu/workflows.json"
