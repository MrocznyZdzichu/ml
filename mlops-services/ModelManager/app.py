from fastapi import FastAPI, HTTPException
from MLOps.ModelManager import register_model
from MLOps import DBManager
import os

app = FastAPI()
IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'
dbm = DBManager(dev_db=True, in_docker=IN_DOCKER)

@app.post("/register-model/{model_name}")
async def register_model_endpoint(model_name: str):
    try:
        # Load the model and register it in the database
        from MLOps.ModelManager import load_model
        model = load_model(model_name=model_name, in_docker=IN_DOCKER)
        register_model(dbm, model=model, do_save=False)
        return {"message": f"Model '{model_name}' successfully registered in the database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering model: {e}")
