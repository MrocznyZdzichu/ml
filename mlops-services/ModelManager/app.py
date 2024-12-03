import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from MLOps import ModelManager
from MLOps import DBManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'
dbm = DBManager(dev_db=True, in_docker=IN_DOCKER)

METADATA_SERVER_URL = "http://mlops-metadata-server-1:4044"
    
@app.get("/registered-models")
async def registered_models():
    response = requests.get(f"{METADATA_SERVER_URL}/models/get_registered_models")
    return response.json()

@app.post("/{model_name}/register-model")
async def register_model(model_name: str):
    try:
        model = ModelManager.load_model(model_name=model_name, in_docker=IN_DOCKER)
        model_data = {
            "name": model.get_name(),
            "estimator_class": model.get_estimator_class().__name__,
            "dataset_name": model.get_dataset_name(),
            "estimator_parameters": model.get_estimator_parameters(),
            "dataroles": model.get_dataroles(),
        }
        print(model_data)

        response = requests.post(f'{METADATA_SERVER_URL}/models/register_model', json=model_data)

        if response.status_code == 200:
            return {"message": f"Model '{model_name}' successfully registered in metadata-server."}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Metadata-server error: {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering model: {e}")
        
@app.get("/{model_name}/model-metadata")
async def model_metadata(model_name: str):
    try:
        url = f"{METADATA_SERVER_URL}/models/{model_name}/get_metadata"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from metadata-server: {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model metadata: {e}")
