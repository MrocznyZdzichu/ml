import os
import requests
from fastapi import HTTPException


def log_batchscore_generation(metadata_server_url, model_name, status, details):
    url = f"{metadata_server_url}/models/{model_name}/batchscores/log_generation?status={status}"
    if details != None:
        url += f'&details={details}' 
    try:
        response = requests.post(url, json={"details": details})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to log batchscore generation: {e}")

def _if_file_exist(filepath):
    """
    Checks if a file exists at the given filepath.

    :param filepath: Path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    return os.path.isfile(filepath)

def check_batchfile_created(model_name):
    """
    Checks if the batch scoring file exists for a given model.

    :param model_name: Name of the model to check for.
    :return: True if the file exists, False otherwise.
    """
    path = os.path.join('model-repository', model_name, 'score_batch.py')
    return _if_file_exist(path)
