import rdflib
import argparse

consolidate_query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
DELETE {
  ?subject ?p ?localObject .
}
INSERT {
  ?subject ?p ?canonical .
}
WHERE {
  ?subject ?p ?localObject .
  ?localObject owl:sameAs+ ?canonical .
  FILTER(?localObject != ?canonical) 
}
"""

cleanup_query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
DELETE {
  ?local ?p ?o .
}
WHERE {
  ?local owl:sameAs ?canonical .
  ?local ?p ?o .
}
"""

def consolidate(input_file):
    g = rdflib.Graph()

    # Read the input file
    g.parse(input_file, format="turtle")

    # Perform the consolidation
    g.update(consolidate_query)
    g.update(cleanup_query)
    
    return g
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output-filename",
        help="The output filename."
    )
    parser.add_argument(
        "-i",
        "--input-file",
        help="A file containing a list of files to merge."
    )
    args = parser.parse_args()

    graph = consolidate(
        input_file=args.input_file,
    )
    graph.serialize(args.output_filename, format="ttl")


if __name__ == "__main__":
    main()
