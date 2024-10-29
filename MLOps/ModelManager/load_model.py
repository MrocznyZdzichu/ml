import os
import joblib

_model_store_dir = 'ModelsRepository'


def load_model(model_name):
    """
    Loads a saved model by its name.
    
    Parameters:
    model_name (str): The name of the model to load.

    Returns:
    Model: The loaded Model object.
    """
    model_path = os.path.join(_model_store_dir, model_name, f'{model_name}_model_object.joblib')
    
    # Check if the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found in {_model_store_dir}.")
    
    # Load the model object
    model = joblib.load(model_path)
    print(f"Model '{model_name}' loaded successfully.")
    return model