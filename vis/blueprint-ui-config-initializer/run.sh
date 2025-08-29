#!/bin/bash
set -e

node --no-deprecation cli.js fetch-classes --output classes.ttl 
node --no-deprecation cli.js fetch-links --output links.ttl
node --no-deprecation cli.js fetch-details --output details.ttl

node --no-deprecation cli.js generate-config --output config.ttl

curl -X POST -H "Content-Type: text/turtle" --data-binary @config.ttl $SPARQL_UPLOAD_ENDPOINT
