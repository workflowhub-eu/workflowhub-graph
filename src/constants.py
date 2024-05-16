import os

import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

WORKFLOWS_URL = 'https://workflowhub.eu/workflows.json'
