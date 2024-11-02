from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Optional
import json

from MLOps import DBManager
from MLOps.DataGoverner import register_dataset, add_tab_details

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_manager = DBManager(dev_db=True, in_docker=True)

# Change the upload directory to the desired location in the container
UPLOAD_DIRECTORY = Path("/app/data-repository")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)  # Create the upload directory on the server if it doesn't exist

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main page displaying the form for dataset registration.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register_dataset")
async def register_dataset_form(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    has_header: int = Form(...),
    is_structured: Optional[int] = Form(None),
    is_tabelaric: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    json_file: UploadFile = File(None),  # Add this line to handle the JSON file
    column_names: List[str] = Form(...),
    data_types: List[str] = Form(...),
    data_levels: List[Optional[str]] = Form(...),
    column_orders: List[int] = Form(...)
):
    print("Rejestracja datasetu została wywołana")  # Debug log
    full_file_path = UPLOAD_DIRECTORY / file.filename  # Set full path for saving the file on the server
    with open(full_file_path, "wb") as f:
        f.write(await file.read())  # Save the file to the server

    columns_data = []

    # Check if a JSON file was provided
    if json_file:
        # Read the JSON file and parse the contents
        json_content = await json_file.read()
        json_data = json.loads(json_content)
        print("Dane z JSON:", json_data)  # Debug log

        for item in json_data:  # Iterate through each item in the JSON data
            columns_data.append({
                "column_name": item['column_name'],
                "datatype": item['datatype'],
                "datalevel": item['datalevel'],
                "column_order": item['column_order']
            })
    else:
        # If no JSON file, use the manually entered columns
        for col_name, data_type, data_level, col_order in zip(column_names, data_types, data_levels, column_orders):
            columns_data.append({
                "column_name": col_name,
                "datatype": data_type,
                "datalevel": data_level,
                "column_order": col_order
            })

    try:
        # Register the dataset with the full file path
        register_dataset(db_manager, name, type, str(full_file_path), has_header, is_structured, is_tabelaric, description)
        
        # Add column details to the database
        add_tab_details(db_manager, name, columns_data)
        message = f"Dataset '{name}' registered successfully with file at {full_file_path}!"
    except Exception as e:
        message = f"Error: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})
