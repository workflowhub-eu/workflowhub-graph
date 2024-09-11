# RO-Crate, Workflow RO-Crate and Workflow Run RO-Crate SPARQL queries

This folder contains both and a folder with several SPARQL queries focused
on RO-Crate, Workflow RO-Crate and Workflow Run RO-Crate.

## Queries

The [queries](queries) folder contains all the SPARQL queries related to
RO-Crate detection, as well as Workflow RO-Crate and Workflow Run RO-Crate
exploration.

## Demo program install

It is written using python. Its software dependencies are declared in
[requirements.txt](requirements.txt). The recommended way to use it is
creating a virtual environment. These are the instructions:

```bash
python3 -mvenv .env
source .env/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```

## Usage

The usage is just giving the program as input both a valid SPARQL query
file and one or more files containing valid JSON-LD.

```bash
python query-rocrate-sparql.py queries/01_is_rocrate.sparql some-ro-crate-metadata.json
```