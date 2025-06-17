from abc import ABC, abstractmethod
import argparse

class EnrichmentABC(ABC):
    """
    Abstract base class for enrichment operations.
    This class defines the interface for enrichment operations that can be
    performed on a graph.

    Subclasses should implement the methods to query the base graph, perform
    enrichment actions and insert the enriched data back into the graph.

    Upon instantiation, the enrichment process is run automatically:
      query_base_graph -> enrichment_action -> insert_enrichment

    Attributes:
        base_graph (object): The base graph to be enriched.
    """

    def __init__(self, base_graph):
        """
        Perform the enrichment operation defined by the subclass.
        Args:
            base_graph (object): The base graph to be enriched.
        """

        base_data = self.query_base_graph(base_graph)
        enrichment_data = self.enrichment_action(base_data)
        self.insert_enrichment(enrichment_data)

    @abstractmethod
    def query_base_graph(self):
        """
        Query the base graph for data.

        This method should be implemented by subclasses to define how to query
        the base graph.
        
        It should return a graph object or data structure that contains the
        queried information which is used for enrichment.

        e.g. SPARQL query to get the OrcID of all users in the graph
        """
        pass

    @abstractmethod
    def enrichment_action(self, base_data):
        """
        Perform the enrichment action on the queried data.

        This method should be implemented by subclasses to define how to
        enrich the data obtained from the base graph.
        
        It should return the enriched data that will be inserted back into the
        graph.

        e.g. Make an API call to enrich the OrcID data with additional metadata

        Args:
            base_data (object): The data obtained from the base graph to be enriched.
        """
        pass

    @abstractmethod
    def insert_enrichment(self, enriched_data):
        """
        Insert the enriched data back into the graph.

        This method should be implemented by subclasses to define how to insert
        the enriched data back into the base graph.
        
        It should handle any necessary transformations or formatting of the
        enriched data before insertion.

        e.g. Insert the enriched OrcID data back into the graph

        Args:
            enriched_data (object): The enriched data to be inserted back into the graph.
        """
        pass

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Enrichment ABC Example")
    arg_parser.add_argument(
        "--base-graph",
        help="The base graph to enrich.",
        required=True
    )

    args = arg_parser.parse_args()
    base_graph = args.base_graph

    # Perform the enrichment operation
    # This would typically involve instantiating a subclass of EnrichmentABC
    # and passing the base_graph to it.
    # For example:
    
    
