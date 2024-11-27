import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from MLOps.ModelManager import register_model, get_registered_models_list, get_model_metadata
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

@app.get("/registered-models")
async def registered_models():
    return get_registered_models_list(dbm)
    
@app.post("/register-model/{model_name}")
async def register_model_endpoint(model_name: str):
    try:
        from MLOps.ModelManager import load_model
        model = load_model(model_name=model_name, in_docker=IN_DOCKER)
        register_model(dbm, model=model, do_save=False)
        return {"message": f"Model '{model_name}' successfully registered in the database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering model: {e}")


@app.get("/model-metadata/{model_name}")
async def model_metadata(model_name: str):
    try:
        print(model_name)
        model_info, model_dataroles = get_model_metadata(dbm, model_name)
        print(model_info)
        print(model_dataroles)
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
