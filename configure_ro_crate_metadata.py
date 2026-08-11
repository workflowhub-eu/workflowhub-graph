# disable pylint check which triggers when setting properties on Entity objects
# pylint: disable=unsupported-assignment-operation

import argparse
import os
import shutil
import sys
import uuid
from datetime import datetime

from rocrate.model import ContextEntity, Person
from rocrate.rocrate import ROCrate

"""Generate a RO-Crate "fragment" with reusable information about authors, affiliations, and license.
This script generates a file called `config-ro-crate-metadata.json`,
and that file is used in the `create_ro_crate.py` Snakemake step.
"""

crate = ROCrate()

crate.name = "WorkflowHub Knowledge Graph"
crate.description = (
    "This RO-Crate contains a knowledge graph built from RO-Crates "
    "on WorkflowHub, enriched with metadata from additional sources. "
    "The source code used to create the knowledge graph, including the enrichments, "
    "is also included."
)

org_uniman = crate.add(
    ContextEntity(
        crate,
        "https://ror.org/027m9bs27",
        properties={"@type": "Organization", "name": "University of Manchester"},
    )
)
org_geneva = crate.add(
    ContextEntity(
        crate,
        "https://ror.org/01swzsf04",
        properties={"@type": "Organization", "name": "University of Geneva"},
    )
)
org_epfl = crate.add(
    ContextEntity(
        crate,
        "https://ror.org/02s376052",
        properties={
            "@type": "Organization",
            "name": "École Polytechnique Fédérale de Lausanne",
        },
    )
)

# Add authors:
auth_alex = crate.add(
    Person(
        crate,
        "https://orcid.org/0000-0003-1193-6632",
        properties={
            "givenName": "Alexander",
            "familyName": "Hambley",
        },
    )
)
auth_alex["affiliation"] = org_uniman
auth_eli = crate.add(
    Person(
        crate,
        "https://orcid.org/0000-0002-0035-6475",
        properties={
            "givenName": "Eli",
            "familyName": "Chadwick",
        },
    )
)
auth_eli["affiliation"] = org_uniman
auth_oliver = crate.add(
    Person(
        crate,
        "https://orcid.org/0000-0002-4565-9760",
        properties={
            "givenName": "Oliver",
            "familyName": "Woolland",
        },
    )
)
auth_oliver["affiliation"] = org_uniman
auth_stian = crate.add(
    Person(
        crate,
        "https://orcid.org/0000-0001-9842-9718",
        properties={
            "givenName": "Stian",
            "familyName": "Soiland-Reyes",
        },
    )
)
auth_stian["affiliation"] = org_uniman
auth_volodymyr = crate.add(
    Person(
        crate,
        "https://orcid.org/0000-0001-6353-0808",
        properties={
            "givenName": "Volodymyr",
            "familyName": "Savchenko",
        },
    )
)
auth_volodymyr["affiliation"] = [org_geneva, org_epfl]

crate.root_dataset["author"] = [
    auth_alex,
    auth_eli,
    auth_oliver,
    auth_stian,
    auth_volodymyr,
]

# Add license:
license = crate.add(
    ContextEntity(
        crate,
        "https://spdx.org/licenses/BSD-2-Clause.html",
        properties={
            "@type": "CreativeWork",
            "name": 'BSD 2-Clause "Simplified" License',
        },
    )
)
crate.license = license

# Writing the RO-Crate metadata:
crate.write_detached("config-ro-crate-metadata.json")
