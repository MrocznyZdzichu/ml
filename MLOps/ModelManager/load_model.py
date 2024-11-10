import os
import joblib
import requests
import zipfile
import shutil
from io import BytesIO


def load_model(model_name, in_docker=False):
    """
    Loads a saved model by its name by downloading it from the model repository.

    Parameters:
    model_name (str): The name of the model to load.
    in_docker (bool): True if function is called within docker-compose container. It matters because of different hostname
    Returns:
    Model: The loaded Model object.
    """
    HOSTNAME             = 'localhost' if in_docker==False else 'mlops-model-repository-1'
    MODEL_REPOSITORY_URL = f"http://{HOSTNAME}:4043"
    download_url = f"{MODEL_REPOSITORY_URL}/download_model/{model_name}"
    
    response = requests.get(download_url)
    if response.status_code != 200:
        raise FileNotFoundError(f"Model '{model_name}' not found in the model repository.")
    
    zip_file_path = os.path.join(f"{model_name}.zip")
    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(response.content)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(model_name))
    
    model_path = os.path.join(model_name, f"{model_name}_model_object.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_name}_model_object.joblib' not found in the downloaded model directory.")
    
    model = joblib.load(model_path)
    print(f"Model '{model_name}' loaded successfully from the repository.")

    os.remove(zip_file_path)
    shutil.rmtree(model_name)
    
    return model
