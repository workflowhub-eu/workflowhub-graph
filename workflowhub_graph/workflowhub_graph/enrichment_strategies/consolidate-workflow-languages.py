from .enrichmentABC import EnrichmentABC

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
        SELECT ?identifier ?name ?url
        WHERE {
        ?s ?p schema:ComputerLanguage ;
            schema:identifier ?identifier ;
            schema:name ?name ;
            schema:url ?url .     
        }
        """
        return query
    
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
