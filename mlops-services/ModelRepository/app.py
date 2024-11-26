from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")
_model_store_dir = "/app/model-repository"

async def get_registered_models():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://mlops-model-manager-1:5003/registered-models")
        response.raise_for_status()
        return response.json()  
    except httpx.RequestError as e:
        print(f"Error fetching registered models: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not os.path.exists(_model_store_dir):
        os.makedirs(_model_store_dir)
    model_names = [
        name for name in os.listdir(_model_store_dir)
        if os.path.isdir(os.path.join(_model_store_dir, name)) and name != ".ipynb_checkpoints"
    ]
    registered_models = await get_registered_models()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "model_names": model_names,
            "registered_models": registered_models,
        },
    )

@app.post("/delete-model/{model_name}")
async def delete_model(model_name: str):
    model_path = os.path.join(_model_store_dir, model_name)
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not found.")
    
    try:
        shutil.rmtree(model_path)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {e}")

@app.get("/download_model/{model_name}")
async def download_model(model_name: str):
    model_path = os.path.join(_model_store_dir, model_name)

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not found.")

    zip_file_path = f"/tmp/{model_name}.zip"

    try:
        shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', model_path)
        return FileResponse(zip_file_path, media_type="application/zip", filename=f"{model_name}.zip")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating zip archive: {e}")