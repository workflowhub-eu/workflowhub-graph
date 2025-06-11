FROM snakemake/snakemake:latest

# Working directory
WORKDIR /app

# Copy the requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the python scripts and install as a module
COPY workflowhub_graph/ /app/workflowhub_graph/
RUN pip install /app/workflowhub_graph

# Copy the Snakefile and config file
COPY Snakefile /app/Snakefile
COPY config.yaml /app/config.yaml

# Set the entry point
ENTRYPOINT ["snakemake", "--snakefile", "Snakefile", "--configfile", "config.yaml", "--cores", "all"]
