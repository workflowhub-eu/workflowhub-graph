# WorkflowHub Knowledge Graph 

## License

[BSD 2-Clause License](https://opensource.org/license/bsd-2-clause)

## Local dev with docker compose

### Setup

To set up a local development environment, first clone the repository.

Now, set the required environment variables in a `.env` file (n.b. the leading '.' is important).

```bash
cp .env.template .env # to create a new .env file
nano .env # to edit the file
```

Then run the following command to bring up the services:

```bash
docker compose up -d # to start the services in the background
docker compose logs -f # to see the logs
```

### Accessing Fuseki

The Fuseki server is available at `http://localhost:3030/`.

The default username and password are `admin` and `admin` respectively.

### Accessing FastAPI

An API for depositing ROCrates is available at `http://localhost:8000/`.

Documentation can be seen at `http://localhost:8000/docs`.