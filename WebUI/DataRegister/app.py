from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Optional

from MLOps import DBManager
from MLOps.DataGoverner import register_dataset, add_tab_details


app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_manager = DBManager(dev_db=True, in_docker=True)

UPLOAD_DIRECTORY = Path("uploaded_files")
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
    column_names: List[str] = Form(...),
    data_types: List[str] = Form(...),
    data_levels: List[Optional[str]] = Form(...),
    column_orders: List[int] = Form(...)
):
    """
    Handle the dataset registration form with the attached file and column details.
    """
    file_location = UPLOAD_DIRECTORY / file.filename  # Set path for saving the file on the server
    with open(file_location, "wb") as f:
        f.write(await file.read())  # Save the file to the server

    try:
        register_dataset(db_manager, name, type, str(file_location), has_header, is_structured, is_tabelaric, description)
        
        # Prepare column details data for insertion
        columns_data = []
        for col_name, data_type, data_level, col_order in zip(column_names, data_types, data_levels, column_orders):
            columns_data.append({
                "column_name": col_name,
                "datatype": data_type,
                "datalevel": data_level,
                "column_order": col_order
            })
        
        # Add column details to the database
        add_tab_details(db_manager, name, columns_data)
        message = f"Dataset '{name}' registered successfully with file at {file_location}!"
    except Exception as e:
        message = f"Error: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})