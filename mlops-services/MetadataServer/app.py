from fastapi import FastAPI, HTTPException, Query, Form
from pydantic import BaseModel
from typing import List, Optional
import requests

from MLOps.DBManager import DBManager 
from MLOps.DataGoverner import get_datasets_list, get_datasets_columns, register_dataset, add_tab_details

app = FastAPI()

dbm = DBManager(dev_db=True, in_docker=True)

@app.get("/datasets")
async def list_datasets():
    return get_datasets_list(dbm)

@app.get("/datasets/{dataset_name}/columns")
async def list_dataset_columns(dataset_name: str, details: bool = Query(False)):
    try:
        dataset_columns = get_datasets_columns(dbm, dataset_name, details)
        return dataset_columns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ColumnData(BaseModel):
    column_name: str
    datatype: str
    datalevel: str
    column_order: int

@app.post("/datasets/register")
async def register_dataset_endpoint(
    name: str = Form(...),
    type: str = Form(...),
    has_header: int = Form(...),
    is_structured: Optional[int] = Form(None),
    is_tabelaric: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    file_name: str = Form(...), 
    json_file_name: str = Form(...) 
):
    columns_data = []
    
    file_url = f"http://mlops-data-repository-1:4042/download/{file_name}"
    response_file = requests.get(file_url)
    if not response_file.ok:
        raise HTTPException(status_code=404, detail="File not found in repository")

    json_file_url = f"http://mlops-data-repository-1:4042/download/{json_file_name}"
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
        register_dataset(dbm, name, type, file_url, has_header, is_structured, is_tabelaric, description)
        add_tab_details(dbm, name, columns_data)
        return {"message": f"Dataset '{name}' registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/datasets/{dataset_name}/columns")
async def add_columns_details(
    dataset_name: str,
    columns: List[ColumnData]
):
    try:
        columns_dict = [column.dict() for column in columns]
        add_tab_details(dbm, dataset_name, columns_dict)
        return {"message": f"Columns for dataset '{dataset_name}' added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")