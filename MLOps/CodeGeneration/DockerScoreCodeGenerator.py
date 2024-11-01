import os
from .CodeGenerator import CodeGenerator  

_model_store_dir = 'ModelsRepository'


class DockerScoreCodeGenerator(CodeGenerator):
    def __init__(self, model_name, required_features, target, container_port):
        super().__init__()  
        self.model_name = model_name
        self.required_features = required_features
        self.target = target
        self.container_port = container_port

    def generate_code(self):
        model_dir = os.path.join(_model_store_dir, self.model_name)
        self.__generate_dockerfile(model_dir)
        self.__generate_app_script(model_dir)
        self.__generate_docker_compose_override(model_dir)

    def __generate_dockerfile(self, model_dir):
        dockerfile_content = f"""
FROM python:3.12-slim

WORKDIR /app

COPY ["./ModelsRepository/{self.model_name}/", "/app"]
COPY ["./requirements.txt", "/app"]
COPY ["./MLOps", "/app/MLOps"]
RUN ["pip", "install", "--no-cache-dir", "-r", "/app/requirements.txt"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{self.container_port}"]
"""
        dockerfile_path = os.path.join(model_dir, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
    
    def __generate_app_script(self, model_dir):
        app_script_content = f"""
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import pandas as pd

app = FastAPI()

# Path to model
MODEL_PATH = "/app/{self.model_name}_model_object.joblib"

# Required features
REQUIRED_FEATURES = {self.required_features}

# Load the model
model = joblib.load(MODEL_PATH)

# Define the data schema
class PredictionRequest(BaseModel):
    data: Union[List[List[float]], List[dict]]

@app.post("/predict/")
async def predict(request: PredictionRequest):
    if isinstance(request.data[0], dict):
        data = pd.DataFrame(request.data)
        missing_features = [feature for feature in REQUIRED_FEATURES if feature not in data.columns]
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Missing features: {{missing_features}}")
        data = data[REQUIRED_FEATURES]
    elif isinstance(request.data[0], list):
        data = pd.DataFrame(request.data, columns=REQUIRED_FEATURES)
    else:
        raise HTTPException(status_code=400, detail="Invalid input format.")

    predictions = model.predict(data)
    return {{"predictions": predictions.tolist()}}
"""
        app_script_path = os.path.join(model_dir, 'app.py')
        with open(app_script_path, 'w') as f:
            f.write(app_script_content)

    def __generate_docker_compose_override(self, model_dir):
        service_name = self.model_name.replace(" ", "-").lower()

        docker_compose_content = f"""
services:
  {service_name}-service:
    build:
      context: ..
      dockerfile: "ModelsRepository/{self.model_name}/Dockerfile"
    ports:
      - "{self.container_port}:{self.container_port}"
    environment:
      - PORT={self.container_port}
"""

        docker_compose_path = os.path.join(model_dir, 'docker-compose.override.yml')
        with open(docker_compose_path, 'w') as f:
            f.write(docker_compose_content)
