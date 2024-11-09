from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import requests
import json

from MLOps import DBManager
from MLOps.DataGoverner import register_dataset, add_tab_details

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_manager = DBManager(dev_db=True, in_docker=True)

# Define the data-repository service URL
DATA_REPOSITORY_URL  = "http://mlops-data-repository-1:4042"
PHYSICAL_STORAGE_DIR = "/app/data-repository'"
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main page displaying the form for dataset registration.
    """
    # Fetch available files from the data repository service
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
    file_name: str = Form(...),  # File name selected by the user
    json_file_name: str = Form(...)  # JSON file name selected by the user
):
    columns_data = []

    # Fetch the main file from the data repository
    file_url = f"{DATA_REPOSITORY_URL}/download/{file_name}"
    response_file = requests.get(file_url)
    if not response_file.ok:
        raise HTTPException(status_code=404, detail="File not found in repository")

    # Fetch and parse the JSON file for column details
    json_file_url = f"{DATA_REPOSITORY_URL}/download/{json_file_name}"
    response_json = requests.get(json_file_url)
    if response_json.ok:
        json_data = response_json.json()
        for item in json_data:
            columns_data.append({
                "column_name": item['column_name'],
                "datatype": item['datatype'],
                "datalevel": item['datalevel'],
                "column_order": item['column_order']
            })
    else:
        raise HTTPException(status_code=404, detail="JSON file not found in repository")

    try:
        # Register the dataset and add details in the database
        register_dataset(db_manager, name, type, file_url, has_header, is_structured, is_tabelaric, description)
        add_tab_details(db_manager, name, columns_data)
        message = f"Dataset '{name}' registered successfully with file at {file_url}!"
    except Exception as e:
        message = f"Error: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})
