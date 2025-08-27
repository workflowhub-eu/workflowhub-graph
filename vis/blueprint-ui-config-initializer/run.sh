#!/bin/bash
set -e

#export SPARQL_BASE=https://fuseki.oliver-woolland-rse.uk
export SPARQL_BASE=http://localhost:3030
export SPARQL_DATABASE=wfh
export SPARQL_ENDPOINT=$SPARQL_BASE/$SPARQL_DATABASE/query
export SPARQL_USER=admin
export SPARQL_PASS=admin


node --no-deprecation cli.js fetch-classes --output classes.ttl 
node --no-deprecation $cli fetch-links --output links.ttl
node --no-deprecation cli.js fetch-details --output details.ttl

node --no-deprecation cli.js generate-config --output config.ttl

curl -X POST -H "Content-Type: text/turtle" --data-binary @config.ttl http://fuseki:3030/data
