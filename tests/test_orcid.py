
# https://github.com/workflowhub-eu/workflowhub-graph/issues/51

# Use case: I want to look up all workflows from a particular author

# .. for all authors from a particular institution.

import pytest
import rdflib

from workflowhub_graph.enrichment_strategies.orcid import fetch_orcid_json_data, graph_for_orcid



@pytest.fixture(scope="module")
def graph():
    return rdflib.Graph().parse(
        data=open("merged.ttl", "r").read(),
        format="turtle",
    )


@pytest.mark.parametrize("orcid", ["https://orcid.org/0000-0001-6353-0808"])
def test_workflows_of_an_author(graph, orcid):
    # TBD: what had to be consolidated to make this work?
    # check partial matches of ORCID names, use possible name variants?

    bindings = graph.query(
        """
        PREFIX schema: <http://schema.org/>
        SELECT DISTINCT ?workflow
        WHERE {
            ?workflow schema:author <%(orcid)s> .
        }
        """
        % {"orcid": orcid}
    ).bindings

    assert len(bindings) == 3
    assert str(sorted(bindings, key=lambda x: str(x["workflow"]))[0]["workflow"]) == "arcp://uuid,4e1e9fb8-78e1-5437-93b3-cec2ce55e5d6/"


    # check we can fetch data from ORCID API
    orcid_data = fetch_orcid_json_data(orcid.split("/")[-1])

    assert orcid_data is not None
    assert orcid_data["person"]["name"]["given-names"]["value"] == "Volodymyr"

    # check that graph has been enriched with ORCID data

    graph += graph_for_orcid(orcid.split("/")[-1], orcid_data)

    bindings = graph.query(
        """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?givenName ?familyName
        WHERE {
            <%(orcid)s> foaf:givenName ?givenName ;
                        foaf:familyName ?familyName .
        }
        """
        % {"orcid": orcid}
    ).bindings

    assert len(bindings) == 1
    assert str(bindings[0]["givenName"]) == "Volodymyr"
    assert str(bindings[0]["familyName"]) == "Savchenko"


@pytest.mark.xfail(reason="issue #51 not yet resolved")
def test_fetch_workflows_institution(graph):
    # Use case: I want to know more about the authors of a given workflow, e.g. their affiliation or social media contact details.

    bindings = graph.query(
        """
        PREFIX schema: <http://schema.org/>
        SELECT DISTINCT ?workflow ?author ?institution
        WHERE {
            ?workflow schema:author ?author .
            ?author schema:affiliation ?institution .
            FILTER(CONTAINS(LCASE(STR(?institution)), "european bioinformatics institute"))
        }
        """
    ).bindings

    assert len(bindings) == 3
    assert str(sorted(bindings, key=lambda x: str(x["workflow"]))[0]["workflow"]) == "arcp://uuid,4e1e9fb8-78e1-5437-93b3-cec2ce55e5d6/"
    assert str(sorted(bindings, key=lambda x: str(x["workflow"]))[0]["author"]) == "https://orcid.org/0000-0001-6353-0808"
    assert str(sorted(bindings, key=lambda x: str(x["workflow"]))[0]["institution"]) == "https://ror.org/03yrm5c26"
