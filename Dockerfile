# Docker container with poetry for python package management

FROM python:3.10-slim

# Install poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml
COPY pyproject.toml /app/

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the files
COPY . /app

# Install the package
RUN poetry install

# Run the application
CMD ["help"]
ENTRYPOINT ["poetry", "run"]
