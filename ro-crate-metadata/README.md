# WorkflowHub Knowledge Graph 

## Getting started

### Obtaining workflowhub-graph

workflowhub-graph is available packaged as a Docker container. You can pull the latest version of the container by running:

```bash
docker pull ghcr.io/uomresearchit/workflowhub-graph:latest
```

This provides the a wrapper for the executable `workflowhub-graph` which can be used to run the various tools provided by the package.

### Running workflowhub-graph

There are several tools provided by the `workflowhub-graph` package. These are:
- 'help': Display help information.
- 'source-crates': Download ROCrates from the WorkflowHub API.
- 'absolutize': Make all paths in an ROCrate absolute.
- 'upload': Upload an ROCrate to Zenodo.
- 'merge': Merge multiple ROCrates into an RDF graph.

To run any of these tools, you can use the following command:

```bash
docker run ghcr.io/uomresearchit/workflowhub-graph:latest <tool> <args>
```

For example, to download ROCrates from the WorkflowHub API, you can run:

```bash
docker run ghcr.io/uomresearchit/workflowhub-graph:latest source-crates
```

## Contributing

### Coding Style

- **Code Formatting**: We use [Python Black](https://black.readthedocs.io/en/stable/) for code formatting. Please format your code using Black before submitting a pull request (PR)
- **Type Hinting**: Please use type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/)), and docstrings ([PEP 257](https://www.python.org/dev/peps/pep-0257/)) in methods and classes.

### Branching Strategy

- **Branch Naming**: When working on a new feature or bug fix, create a branch from `develop`. e.g. `feature/description` or `bugfix/description`.
- **Development Branch**: The `develop` branch is currently our main integration branch. Features and fixes should target `develop` through PRs.
- **Feature Branches**: These feature branches should be short-lived and focused. Once done, please create a pull request to merge it into `develop`.

## Overview

![arch_diagram.png](./docs/images/arch_diagram.png)

## License

[BSD 2-Clause License](https://opensource.org/license/bsd-2-clause)
