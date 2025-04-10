import html
from data_formulator.agents.client_utils import Client

def get_client(model_config):
    for key in model_config:
        model_config[key] = model_config[key].strip()

    client = Client(
        model_config["endpoint"],
        model_config["model"],
        model_config["api_key"] if "api_key" in model_config else None,
        html.escape(model_config["api_base"]) if "api_base" in model_config else None,
        model_config["api_version"] if "api_version" in model_config else None)

    return client
