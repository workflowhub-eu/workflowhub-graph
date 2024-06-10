# WorkflowHub Knowledge Graph 

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
