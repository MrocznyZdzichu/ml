from fastapi import FastAPI, HTTPException, Query
from MLOps.DBManager import DBManager 
from MLOps.DataGoverner import get_datasets_list, get_datasets_columns

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
