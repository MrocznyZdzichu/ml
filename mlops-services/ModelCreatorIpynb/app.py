from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from MLOps.ModelManager import ModelCreatorIpynb

import tempfile
import shutil

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create-model")
async def create_model(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ipynb") as temp_notebook:
        temp_path = temp_notebook.name
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    model_creator = ModelCreatorIpynb(temp_path)
    model = model_creator.create_model()
    model.save_model()

    return {"message": "Model created and saved successfully."}
