FROM snakemake/snakemake:v9.21.1
ARG BUILD_TEST=false # Override at build time to install test dependencies

# Working directory
WORKDIR /app

# Copy the python scripts and install as a module
COPY workflowhub_graph/ /app/workflowhub_graph/
RUN pip install /app/workflowhub_graph

# Install additional dependencies if specified
RUN if [ "$BUILD_TEST" = "true" ]; then pip install /app/workflowhub_graph[test]; fi

# Copy the Snakefile and config file
COPY Snakefile /app/Snakefile
COPY config.yaml /app/config.yaml

# Copy files needed for the RO-Crate
COPY Dockerfile /app/Dockerfile
COPY README.md /app/README.md
COPY config-ro-crate-metadata.json /app/config-ro-crate-metadata.json

# Set the entry point
ENV XDG_CACHE_HOME=/app/output/
ENTRYPOINT ["snakemake", "--snakefile", "Snakefile", "--configfile", "config.yaml", "--cores", "all", "--directory", "/app/output"]
CMD []
