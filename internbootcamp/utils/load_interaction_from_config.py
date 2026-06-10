import importlib
from internbootcamp.src.base_interaction import BaseInteraction

def load_interaction_from_config(config: dict) -> BaseInteraction:
    class_name = config["class_name"]
    config = config.get("config", {})
    module_path = ".".join(class_name.split(".")[:-1])
    class_name = class_name.split(".")[-1]
    module = importlib.import_module(module_path)
    interaction_class = getattr(module, class_name)
    return interaction_class(config)