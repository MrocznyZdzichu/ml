import os
from fastapi import FastAPI, HTTPException
from MLOps.ModelManager import register_model, get_registered_models_list
from MLOps import DBManager

app = FastAPI()
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



