FROM python:3.11-slim

RUN pip install poetry

# Set the working directory
WORKDIR /app

# Install build tools for Snakemake (gcc, make, etc.)
RUN apt-get update && apt-get install -y build-essential

# Copy the pyproject.toml file
COPY pyproject.toml /app/

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the application files
COPY . /app

# Install the package
RUN poetry install

# Install Snakemake using Poetry
RUN poetry add snakemake

# Set the entry point for the container
ENTRYPOINT ["poetry", "run"]

CMD ["help"]
