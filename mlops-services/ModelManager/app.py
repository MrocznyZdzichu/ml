import os
import requests
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from MLOps import ModelManager
from MLOps import DBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'
dbm = DBManager(dev_db=True, in_docker=IN_DOCKER)

METADATA_SERVER_URL = "http://mlops-metadata-server-1:4044"

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    reg = await registered_models()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "registered_models": reg,
            "message": "", 
        }
    )


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


@app.post("/{model_name}/unregister-model")
async def api_unregister_model(model_name: str):
    try:
        url = f"{METADATA_SERVER_URL}/models/{model_name}/unregister-model"
        response = requests.post(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from metadata-server: {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model metadata: {e}")
    

@app.post("/{model_name}/generate-batch-scoring")
async def api_generate_batch_scoring(model_name: str):
    logger.info(f"Generating batch score code for {model_name}")
    reg_models = await registered_models()
    
    if model_name not in reg_models:
        raise HTTPException(status_code=404, detail="Requested model is not registered")
    try:
        model = ModelManager.load_model(model_name, in_docker=IN_DOCKER)
    except:
        logger.error("Error loading model", exc_info=True)
        raise HTTPException(status_code = 500, detail="Requested model not loaded")
    
    try:
        model.generate_batch_score_code()
    except:
        logger.error("Error generating batch scoring code", exc_info=True)
        raise HTTPException(status_code=500, detail="Failure during generating a score code")
    
    return {"message": "Successfully generated a batch scoring code"}