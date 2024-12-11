import os
import requests
import logging
import subprocess
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from MLOps import ModelManager
from MLOps import DBManager
import addons

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
async def api_generate_batch_scoring(request: Request, model_name: str, replace: bool = False):
    logger.info(f"Generating batch score code for {model_name}")
    reg_models = await registered_models()
    
    if model_name not in reg_models:
        message = "Requested model is not registered."
        return templates.TemplateResponse("index.html", {"request": request, "registered_models": reg_models, "message": message},status_code=404)
    
    scorefile_path = os.path.join('model-repository', model_name, 'score_batch.py')
    if os.path.exists(scorefile_path) and not replace:
        logger.info(f"Score batch file already exists for {model_name}.")
        return JSONResponse(
            {"requires_confirmation": True, "message": f"Batch scoring code already exists for {model_name}. Replace?"},
            status_code=200
        )
    
    try:
        model = ModelManager.load_model(model_name, in_docker=IN_DOCKER)
        model.generate_batch_score_code()
    except Exception as e:
        logger.error("Error during batch scoring code generation", exc_info=True)
        message = f"Error generating batch scoring code for {model_name}: {e}"
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "registered_models": reg_models, "message": message},
            status_code=500
        )
    
    if not addons.check_batchfile_created(model_name):
        message = 'Generator method did not fail but batchscore does not exist.'
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "registered_models": reg_models, "message": message},
            status_code=500
        )
    
    message = f"Successfully generated batch scoring code for {model_name}."
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "registered_models": reg_models, "message": message},
        status_code=200
    )


@app.post("/{model_name}/execute-batch-scoring")
async def api_execute_batch_scoring(request: Request, model_name: str, has_headers: bool, file: UploadFile = File(...)):
    logger.info(f'Executing a batch scoring for {model_name}')
    logger.info(f'Input batch file contains headers? {has_headers}')

    reg_models = await registered_models()

    if model_name not in reg_models:
        message = "Requested model is not registered."
        return templates.TemplateResponse("index.html",{"registered_models": reg_models, "message": message},)
    
    base_path        = os.path.join('model-repository', model_name)
    batch_inputs_dir = os.path.join(base_path, 'inputs', 'batch')
    scorecode_path   = os.path.join(base_path, 'score_batch.py')

    os.makedirs(batch_inputs_dir, exist_ok=True)

    input_file_path = os.path.join(batch_inputs_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S_")+file.filename)
    with open(input_file_path, "wb") as f:
        f.write(file.file.read())

    if not os.path.exists(scorecode_path):
        logger.error('Scoring file not found')
        raise HTTPException(status_code=404, detail=f"Scoring script not found for model {model_name}")
    
    if has_headers:
        command = ["python", scorecode_path, input_file_path]
    else:
        command = ["python", scorecode_path, input_file_path, '--no-headers']

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        return templates.TemplateResponse("index.html", {"request": request, "registered_models": reg_models, "message": result.stderr}, status_code=500)
    
    message = f"Batch scoring executed successfully for {model_name}.\nOutput: {result.stdout}"
    return templates.TemplateResponse("index.html", {"request": request, "registered_models": reg_models, "message": message})