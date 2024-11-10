from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional

import os
import requests
import json

from MLOps import DBManager
from MLOps.DataGoverner import register_dataset, add_tab_details

IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_manager = DBManager(dev_db=True, in_docker=IN_DOCKER)

METADATA_SERVICE_URL = "http://mlops-metadata-server-1:4044"
DATA_REPOSITORY_URL  = "http://mlops-data-repository-1:4042"
PHYSICAL_STORAGE_DIR = "/app/data-repository'"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main page displaying the form for dataset registration.
    """
    try:
        response = requests.get(f"{DATA_REPOSITORY_URL}/files")
        response.raise_for_status()
        files = response.json().get("files", [])
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail="Unable to fetch files from data repository")

    return templates.TemplateResponse("index.html", {"request": request, "files": files})

@app.post("/register_dataset")
async def register_dataset_form(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    has_header: int = Form(...),
    is_structured: Optional[int] = Form(None),
    is_tabelaric: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    file_name: str = Form(...), 
    json_file_name: str = Form(...) 
):
    data = {
        "name": name,
        "type": type,
        "has_header": has_header,
        "is_structured": is_structured,
        "is_tabelaric": is_tabelaric,
        "description": description,
        "file_name": file_name,
        "json_file_name": json_file_name
    }

    try:
        response = requests.post(f"{METADATA_SERVICE_URL}/datasets/register", data=data)
        response.raise_for_status()
        message = f"Dataset '{name}' registered successfully!"
    except requests.RequestException as e:
        message = f"Error: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})
