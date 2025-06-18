import importlib
import pkgutil
import inspect
from .enrichmentABC import EnrichmentABC

STRATEGY_REGISTRY = {}

# Discover all modules in this directory
for _, module_name, _ in pkgutil.iter_modules(__path__):
    # Don't import if the module is the abstract base class itself
    if module_name == "enrichmentABC":
        continue

    # Import the target module dynamically
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Inspect module for subclasses of EnrichmentABC and register them
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, EnrichmentABC) and obj is not EnrichmentABC:
            STRATEGY_REGISTRY[module_name] = obj
