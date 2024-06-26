import yaml
import os

class Credential:
    def __init__(self, client_id, client_secret, ru_name):
        self.client_id = client_id
        self.client_secret = client_secret
        self.ru_name = ru_name

def load(config_path):
    """
    Load the configuration from a yaml file.
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    
    with open(config_path, 'r') as stream:
        config_data = yaml.safe_load(stream)
        
    # Extract credentials from the nested dictionary
    credentials = next(iter(config_data.values()))
        
    return Credential(
        client_id=credentials.get('appid'),
        client_secret=credentials.get('certid'),
        ru_name=credentials.get('ru_name')
    )

def get_credentials(env_type):
    """
    Retrieves credentials for the specified environment type (sandbox or production).
    """
    config_file = f'/Users/ebay_env/ebaysdk-python-master/config/{env_type.lower()}_credentials.yaml'
    credentials = load(config_file)
    if not credentials:
        raise Exception(f"Could not load credentials for environment: {env_type}")
    return credentials