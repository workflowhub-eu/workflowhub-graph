from .enrichmentABC import EnrichmentABC
import rdflib
from rdflib.namespace import RDF
import requests

def query_wikidata(label):
    """
    Query WikiData for a given label.

    Args:
        label (str): The label to search for in WikiData.

    Returns:
        dict: The search results from WikiData.
    """

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

def create_canonical(g, wikidata_id):
    query = f"""
    SELECT ?wikidata_id ?wikidata_idLabel ?description ?homepage ?alias WHERE {{
      VALUES ?wikidata_id {{ wd:{wikidata_id} }}
      OPTIONAL {{ ?wikidata_id wdt:P856 ?homepage }}
      OPTIONAL {{ ?wikidata_id skos:altLabel ?alias FILTER(LANG(?alias) = "en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    # Perform query
    r = requests.get("https://query.wikidata.org/sparql",
                     params={"query": query},
                     headers={"Accept": "application/sparql-results+json"},
                     timeout=10)
    r.raise_for_status()

    # Get bindings
    bindings = r.json()["results"]["bindings"]

    # Create canonical triple for the workflow language
    SCHEMA = rdflib.Namespace("http://schema.org/")
    wiki_uri = rdflib.URIRef(f"https://www.wikidata.org/entity/{wikidata_id}")
    g.add((wiki_uri, RDF.type, SCHEMA.ComputerLanguage))

    # Add additional metadata to node
    print(bindings)
    for binding in bindings:
        if "wikidata_idLabel" in binding:
            g.add((wiki_uri,
                   SCHEMA.name,
                   rdflib.Literal(binding["wikidata_idLabel"]["value"])))
        if "description" in binding:
            g.add((wiki_uri,
                   SCHEMA.description,
                   rdflib.Literal(binding["description"]["value"])))
        if "homepage" in binding:
            g.add((wiki_uri,
                   SCHEMA.url,
                   rdflib.URIRef(binding["homepage"]["value"])))
        if "alias" in binding:
            g.add((wiki_uri,
                   SCHEMA.alternateName,
                   rdflib.Literal(binding["alias"]["value"])))
    
    return None

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

                create_canonical(g, wikidata_id)

            # Check if we got a result from WikiData, continue if not
            if not wikidata_id:
                print(f"No WikiData results for {name} ({identifier})")
                continue

            # Link existing triple to the canonical object (for later consolidation)
            g.add((rdflib.URIRef(line.crate),
                   OWL.sameAs,
                   rdflib.URIRef(f"https://www.wikidata.org/entity/{wikidata_id}")))

        return None
