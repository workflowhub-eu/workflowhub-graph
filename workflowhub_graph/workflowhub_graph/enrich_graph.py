import argparse
import logging

from workflowhub_graph.enrichment_strategies import STRATEGY_REGISTRY

def main():
    parser = argparse.ArgumentParser(description="Enrich RDF graph with additional data.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--graph",
        help="The RDF graph file to enrich.",
        required=True
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="The output filename for the enriched graph.",
        required=True
    )

    parser.add_argument(
        "-s",
        "--strategy",
        help="The enrichment strategy to use",
        required=True,
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Extract the arguments
    graph_file = args.graph
    enrichment_strategy = args.strategy
    output_file = args.output_file

    # Error if the strategy is not recognized
    if enrichment_strategy not in STRATEGY_REGISTRY:
        raise ValueError(f"Enrichment strategy '{enrichment_strategy}' is not recognized. Available strategies: {', '.join(STRATEGY_REGISTRY.keys())}")

    # Create the strategy instance to perform enrichment
    enrichment_obj = STRATEGY_REGISTRY[enrichment_strategy]()

    # Run the enrichment operation
    enrichment_obj._run(graph_file)
    enrichment_results = enrichment_obj.enrichment_graph

    # Serialise to output file
    enrichment_results.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    main()
    
