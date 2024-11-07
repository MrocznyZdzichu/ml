from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")
_model_store_dir = "/app/model-repository"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not os.path.exists(_model_store_dir):
        os.makedirs(_model_store_dir)
    model_names = [name for name in os.listdir(_model_store_dir) if os.path.isdir(os.path.join(_model_store_dir, name))]
    
    return templates.TemplateResponse("index.html", {"request": request, "model_names": model_names})


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