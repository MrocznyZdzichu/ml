from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from MLOps.ModelManager import ModelCreatorBasic
from MLOps.DBManager import DBManager 

app = FastAPI()

templates = Jinja2Templates(directory="templates")
model_repository_dir = "/app/model-repository"

@app.get("/", response_class=HTMLResponse)
async def create_model_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create_model")
async def create_model(
    request: Request,
    model_name: str = Form(...),
    dataset_name: str = Form(...),
    model_class: str = Form(...),
    model_params: str = Form(...),
    datarole_mapping: str = Form(...)
):
    model_params = eval(model_params)
    datarole_mapping = eval(datarole_mapping)

    dbm = DBManager(dev_db=True, in_docker=True)

    ModelClass = eval(model_class)

    model_creator = ModelCreatorBasic(
        model_name=model_name,
        dataset_name=dataset_name,
        model_class=ModelClass,
        model_params=model_params,
        datarole_mapping=datarole_mapping
    )
    
    model = model_creator.create_model(dbm)
    model.save_model()

    return RedirectResponse(url="/", status_code=303)
