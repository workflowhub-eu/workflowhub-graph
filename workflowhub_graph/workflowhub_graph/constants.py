import os

import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

DOT_JSON_ENDPOINT = "/workflows/{w_id}.json"
METADATA_ENDPOINT = "/workflows/{w_id}/ro_crate_metadata?version={w_version}"
ZIP_ENDPOINT = "/workflows/{w_id}/ro_crate?version={w_version}"

TARGET_FILE_NAME = "ro-crate-metadata.json"
