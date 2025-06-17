import enrichmentABC
import rdflib

class ConsolidateWorkflowLanguages(enrichmentABC.EnrichmentABC):
    """
    Class to consolidate and enrich workflow languages in a graph.
    """
    
    def query_base_graph(self, input_file):
        """
        Perform a SPARQL query for workflow languages in the base graph.

        Returns a graph object or data structure containing the queried
        """

        # Load the base graph
        g = rdflib.Graph()
        g.parse(input_file, format='turtle')

        # Define a SPARQL query to get workflow languages
        query = """
        SELECT *
        WHERE {
          ?s ?p ?o .
        }
        """
    
    def enrichment_action(self):
        """
        Perform the enrichment action on the queried data.

        This method should be implemented by subclasses to define how to
        enrich the data obtained from the base graph.
        
        It should return the enriched data that will be inserted back into the
        graph.

        e.g. Make an API call to enrich the OrcID data with additional metadata
        """
        pass
    
    def insert_enrichment(self):
        """
        Insert the enriched data back into the graph.

        This method should be implemented by subclasses to define how to insert
        the enriched data back into the base graph.
        
        It should handle any necessary transformations or formatting of the
        enriched data before insertion.

        e.g. Insert the enriched OrcID data back into the graph
        """
        pass
