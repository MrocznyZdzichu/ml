from fastapi import FastAPI, HTTPException, Query, Form
from pydantic import BaseModel
from typing import List, Optional

import requests
import os

from MLOps.DBManager import DBManager 
from MLOps import MetadataManager
from MLOps import Model

IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'

app = FastAPI()

dbm = DBManager(dev_db=True, in_docker=IN_DOCKER)

################### datasets ###################

@app.get("/datasets")
async def list_datasets():
    return MetadataManager.get_datasets_list(dbm)

@app.get("/datasets/{dataset_name}/columns")
async def list_dataset_columns(dataset_name: str, details: bool = Query(False)):
    try:
        dataset_columns = MetadataManager.get_datasets_columns(dbm, dataset_name, details)
        return dataset_columns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ColumnData(BaseModel):
    column_name: str
    datatype: str
    datalevel: str
    column_order: int

@app.post("/datasets/{dataset_name}/columns")
async def add_columns_details(
    dataset_name: str,
    columns: List[ColumnData]
):
    try:
        columns_dict = [column.dict() for column in columns]
        MetadataManager.add_tab_details(dbm, dataset_name, columns_dict)
        return {"message": f"Columns for dataset '{dataset_name}' added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        
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
        MetadataManager.register_dataset(dbm, name, type, file_url, has_header, is_structured, is_tabelaric, description)
        MetadataManager.add_tab_details(dbm, name, columns_data)
        return {"message": f"Dataset '{name}' registered successfully!"}
    except Exception as e:
        print('ERROR:\t', str(e))
        raise HTTPException(status_code=500, detail=str(e)
    )

################### models ###################
@app.get("/models/get_registered_models")
async def get_registered_models():
    return MetadataManager.get_registered_models_list(dbm)

@app.post("/models/register_model")
async def model_register(model_data: dict):
    try:
        model = Model(
            name=model_data["name"],
            estimator_class=model_data["estimator_class"],
            dataset_name=model_data["dataset_name"],
            estimator_parameters=model_data["estimator_parameters"],
            estimator=None,  # Estimator object not needed in metadata
            features_names=[],  
            dataroles=model_data["dataroles"]
        )
        MetadataManager.register_model(dbm, model, do_save=False)

        return {"message": f"Model '{model.get_name()}' successfully registered in the database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering model: {e}")

@app.get("/models/{model_name}/get_metadata")
async def api_get_model_metadata(model_name: str):
    try:
        model_info, model_dataroles = MetadataManager.get_model_metadata(dbm, model_name)
        return {
            "model_info": {
                "model_name": model_info[0],
                "estimator_class": model_info[1],
                "dataset_name": model_info[2],
                "estimator_parameters": model_info[3],
                "created_at": model_info[4],
            },
            "model_dataroles": [
                {
                    "column_name": role[0],
                    "datatype": role[1],
                    "datalevel": role[2],
                    "datarole": role[3],
                }
                for role in model_dataroles
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model metadata: {e}")


@app.post("/models/{model_name}/unregister-model")
async def api_unregister_model(model_name: str):
    model_id = MetadataManager.get_model_id(dbm, model_name)
    MetadataManager.unregister_model(dbm, model_id)


@app.post("/models/{model_name}/batchscores/log_generation")
async def api_log_batchscore_generation(model_name: str, status: str, details: str = ''):
    try:
        MetadataManager.log_batchscore_generation(dbm, model_name, status, details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"detail" : "Generation of batchscore code logged successfully."}