# Stage 1: Build environment
FROM python:3.11-slim AS build-stage

# Install build tools and Poetry
RUN apt-get update && apt-get install -y build-essential \
    && pip install poetry

WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock README.md Snakefile /app/
COPY workflowhub_graph /app/workflowhub_graph/
RUN poetry config virtualenvs.create false

# Copy and install the application
RUN poetry install --no-interaction --no-ansi

# Stage 2: Snakemake runtime environment
FROM snakemake/snakemake:latest

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy the application from the build stage
COPY --from=build-stage /app /app

# Install dependencies
RUN pip install -r <(poetry export --format requirements.txt --without-hashes) \
    && pip install -e .

# Set up non-root user
RUN groupadd -r snakemake && useradd -r -g snakemake snakemake \
    && chown -R snakemake:snakemake /app

USER snakemake

# Configure Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Set the entry point
ENTRYPOINT ["snakemake"]
