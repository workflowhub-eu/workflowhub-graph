import logging
import rdflib
import requests_cache
import requests

from abc import ABC

from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF

from workflowhub_graph.enrichment_strategies.enrichmentABC import EnrichmentABC



requests_cache.install_cache('orcid_cache', backend='filesystem', expire_after=86400)

# TODO: add ABC-based structure here similar to consolidate-workflow-languages.py

def fetch_orcid_json_data(orcid_id):
    """
    Fetch ORCID data for a given ORCID ID using the ORCID public API.
    """

    base_url = "https://pub.orcid.org/v3.0/"
    headers = {
        "Accept": "application/json"
    }
    
    # Use a cached session to avoid redundant requests

    session = requests.Session()
    
    try:
        response = session.get(f"{base_url}{orcid_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed for ORCID ID '{orcid_id}': {e}")
        return None
    

def graph_for_orcid(orcid_id, orcid_data):
    """
    Add ORCID data to the RDF graph.

    Args:
        orcid_id (str): The ORCID ID of the author.
        orcid_data (dict): The ORCID data fetched from the API.
    """

    graph = rdflib.Graph()

    SCHEMA = Namespace("http://schema.org/")
    
    orcid_uri = URIRef(f"https://orcid.org/{orcid_id}")
    
    # Add basic information
    graph.add((orcid_uri, RDF.type, SCHEMA.Person))
    
    person_data = orcid_data.get('person', {})
    name_data = person_data.get('name', {})

    try:
        if name_data:
            given_name = name_data.get('given-names', {}).get('value')
            if given_name:
                graph.add((orcid_uri, SCHEMA.givenName, Literal(given_name)))
                logging.debug(f"Added ORCID ID {orcid_id} with given name {given_name}")

            family_name = name_data.get('family-name', {}).get('value')
            if family_name:
                graph.add((orcid_uri, SCHEMA.familyName, Literal(family_name)))
                logging.debug(f"Added ORCID ID {orcid_id} with name {given_name} {family_name}")

        # add employment information
        #  jq '._decoded_content["activities-summary"].employments["affiliation-group"] | .[] | .summaries[0]["employment-summary"].organization.name'

        activities = orcid_data.get('activities-summary', {})
        if activities:
            employments = activities.get('employments', {}).get('affiliation-group', [])
            for employment in employments:
                summaries = employment.get('summaries', [])
                if summaries and len(summaries) > 0:
                    employment_summary = summaries[0].get('employment-summary', {})
                    organization = employment_summary.get('organization', {})
                    org_name = organization.get('name')
                    if org_name:
                        graph.add((orcid_uri, SCHEMA.affiliation, Literal(org_name)))
                        logging.debug(f"Added affiliation {org_name} for ORCID ID {orcid_id}")
    except Exception as e:
        logging.warn(f"Error creating ORCID object {e}")
    
    return graph


class ORCIDEnrichment(EnrichmentABC):
    """
    Class to enrich a graph with ORCID data.
    """

    def enrichment_base_query(self):
        """
        Query for ORCID identifiers in the graph
        """

        query = """
        PREFIX schema: <http://schema.org/> 
        SELECT DISTINCT ?orcid
        WHERE {
            ?author schema:identifier ?orcid .
            FILTER(CONTAINS(STR(?orcid), "orcid.org"))
        }
        """

        return query

    def enrichment_action(self, enrichment_base_data):
        """
        Enrich the graph with ORCID data.

        Args:
            enrichment_base_data (rdflib.query.Result): The result of the base query.
            graph (rdflib.Graph): The RDF graph to be enriched.
        """

    
        logging.info(f"Found {len(enrichment_base_data)} unique ORCID identifiers in the base graph.")

        for row in enrichment_base_data:
            orcid_uri = str(row['orcid'])
            orcid_id = orcid_uri.split("/")[-1]
            orcid_data = fetch_orcid_json_data(orcid_id)
            if orcid_data:
                self.enrichment_graph = self.enrichment_graph + graph_for_orcid(orcid_id, orcid_data)
