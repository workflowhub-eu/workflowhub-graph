from abc import ABC, abstractmethod

import argparse
import rdflib

class EnrichmentABC(ABC):
    """
    Abstract base class for enrichment operations.
    This class defines the interface for enrichment operations that can be
    performed on a graph.

    Upon instantiation, the enrichment process is run automatically:
      query_base_graph -> enrichment_action 

    Attributes:
        base_graph (object): The base graph to be enriched.
    """

    def __init__(self):
        """
        Initializes the enrichment operation and executes the enrichment
        """
        self.enrichment_graph = rdflib.Graph()

    def _run(self, base_graph):
        """
        Runs the enrichment operation on the provided base graph.

        Args:
            base_graph (str): The path to the base graph file in Turtle format.

        N.B: This method should not be overridden by subclasses.
        """

        # ----------------------------------------------------------------------
        # Fetch and execute the query to retrieve data from the base graph

        # Read the input file into an rdf graph
        g = rdflib.Graph()
        g.parse(base_graph, format="turtle")

        # Fetch the base query defined by the subclass and execute it
        enrichment_query = self.enrichment_base_query()
        enrichment_base_data = g.query(enrichment_query)

        # ----------------------------------------------------------------------
        # Perform the enrichment action on the queried data
        
        enrichment_graph = self.enrichment_action(enrichment_base_data)

    @abstractmethod
    def enrichment_base_query(self):
        """
        Defines a SPARQL query to retrieve data from the base graph used
        for enrichment.

        e.g. Query the base graph for OrcID data
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

