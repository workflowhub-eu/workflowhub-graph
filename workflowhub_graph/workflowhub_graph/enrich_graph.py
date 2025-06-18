import argparse
import os

from workflowhub_graph.enrichment_strategies import STRATEGY_REGISTRY

def main():
    argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Enrich RDF graph with additional data.")
    parser.add_argument(
        "--graph",
        help="The RDF graph file to enrich.",
        default="graph.ttl",
        required=True
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="The output filename for the enriched graph.",
        default="enriched_graph.ttl",
        required=True
    )

    parser.add_argument(
        "-s",
        "--strategy",
        help="The enrichment strategy to use",
        required=True
    )

    args = parser.parse_args()

    graph_file = args.graph
    enrichment_strategy = args.strategy
    output_file = args.output_file

    print(f"Enriching graph from {graph_file} using strategy {enrichment_strategy}...")
    print(f"Available strategies: {', '.join(STRATEGY_REGISTRY.keys())}")

    if enrichment_strategy not in STRATEGY_REGISTRY:
        raise ValueError(f"Enrichment strategy '{enrichment_strategy}' is not recognized. Available strategies: {', '.join(STRATEGY_REGISTRY.keys())}")

    enrichment_results = STRATEGY_REGISTRY[enrichment_strategy](graph_file)
    
    # with open(output_file, "w") as out_f:
    #     # Here you would implement the logic to enrich the graph based on the strategy
    #     # For now, we just write a placeholder message
    #     out_f.write(f"Enriched graph from {graph_file} using strategy {enrichment_strategy}\n")

    # print(f"Enriched graph written to {output_file}")

if __name__ == "__main__":
    main()
    
