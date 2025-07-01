from .enrichmentABC import EnrichmentABC
import rdflib

def query_wikidata(label):
    """
    Query WikiData for a given label.

    Args:
        label (str): The label to search for in WikiData.

    Returns:
        dict: The search results from WikiData.
    """
    import requests

    # Construct the API request to WikiData
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json",
        "limit": 1
    }

    # Make the request to WikiData
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"Request failed for label '{label}': {e}")
        return None

    # Get and return the ID
    search_results = data.get("search", [])
    if search_results:
        page_id = search_results[0].get("id")
    else:
        page_id = None
    
    return page_id

class ConsolidateWorkflowLanguages(EnrichmentABC):
    """
    Class to consolidate and enrich workflow languages in a graph.
    """
    
    def enrichment_base_query(self):
        """
        Query for workflow languages
        """

        query = """
        PREFIX schema: <http://schema.org/> 
        SELECT ?crate ?identifier ?name
        WHERE {
        ?crate ?p schema:ComputerLanguage ;
            schema:identifier ?identifier ;
            schema:name ?name .
        }
        """
        return query
    
    def enrichment_action(self, base_data):
        """
        Query WikiData for workflow languages and create consolidated data.
        """
        
        g = self.enrichment_graph
        
        # Allow the addition of sameAs predicates
        OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
        if "owl" not in g.namespaces():
            g.bind("owl", "http://www.w3.org/2002/07/owl#")

        # Create an object to hold mappings in case they can be reused
        mappings = {}

        # Iterate over results and enrich with WikiData
        for line in base_data:
            identifier = str(line.identifier)
            name = str(line.name)

            # Query WikiData for the language name
            if identifier in mappings:
                wikidata_id = mappings[identifier]
            else:
                wikidata_id = query_wikidata(name)
                mappings[identifier] = wikidata_id

            # Check if we got a result from WikiData, continue if not
            if not wikidata_id:
                print(f"No WikiData results for {name} ({identifier})")
                continue

            # Create RDF triples for the workflow language
            g.add((rdflib.URIRef(line.crate),
                   OWL.sameAs,
                   rdflib.URIRef(f"https://www.wikidata.org/entity/{wikidata_id}")))

        return None
