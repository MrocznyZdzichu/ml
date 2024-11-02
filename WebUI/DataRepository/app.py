import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define the directory where files will be stored
DATA_DIRECTORY = Path("data-repository")
DATA_DIRECTORY.mkdir(exist_ok=True)  # Create the data directory if it doesn't exist

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main page displaying the form for dataset registration.
    """
    return templates.TemplateResponse("index.html", {"request": request})  # Make sure to include the request here

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a new file to the server.
    """
    file_location = DATA_DIRECTORY / file.filename
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"info": f"File '{file.filename}' uploaded successfully."}

@app.get("/files")
async def list_files():
    """
    List files in the data repository directory.
    """
    directory = Path("data-repository")  # Upewnij się, że podajesz poprawną ścieżkę do katalogu
    files = [f.name for f in directory.iterdir() if f.is_file()]
    return {"files": files}
    
@app.delete("/delete_file")
async def delete_file(file_name: str):
    """
    Delete a file from the data repository.
    """
    file_path = Path("data-repository") / file_name
    if file_path.is_file():
        file_path.unlink()  # Remove the file
        return {"message": f"File '{file_name}' deleted."}
    else:
        return {"error": "File not found."}, 404

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    """
    Download a file from the data repository.
    
    Args:
        file_name (str): The name of the file to be downloaded.
        
    Returns:
        FileResponse: The requested file.
    """
    file_path = DATA_DIRECTORY / file_name
    if file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found.")
