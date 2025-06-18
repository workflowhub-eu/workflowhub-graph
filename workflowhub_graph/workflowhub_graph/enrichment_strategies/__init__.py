import importlib
import pkgutil
import inspect
from .enrichmentABC import EnrichmentABC

STRATEGY_REGISTRY = {}

# Discover all modules in this directory
for _, module_name, _ in pkgutil.iter_modules(__path__):
    # Don't import the base module itself
    if module_name == "EnrichmentABC":
        continue

    module = importlib.import_module(f".{module_name}", package=__name__)

    # Inspect module for subclasses of EnrichmentABC
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, EnrichmentABC) and obj is not EnrichmentABC:
            STRATEGY_REGISTRY[module_name] = obj

# Print the discovered strategies for debugging purposes
print("Discovered enrichment strategies:")
for strategy_name in STRATEGY_REGISTRY:
    print(f" - {strategy_name}")
    
