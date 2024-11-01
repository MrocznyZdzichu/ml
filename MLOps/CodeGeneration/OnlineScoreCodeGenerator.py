from datetime import datetime
from .CodeGenerator import CodeGenerator

_model_store_dir = 'ModelsRepository'


class OnlineScoreCodeGenerator(CodeGenerator):
    def __init__(self, model_name, required_features, target):
        self.model_name = model_name
        self.required_features = required_features
        self.target = target

    def generate_code(self):
        """Generates the code for an online scoring service using FastAPI and Uvicorn."""
        code = f"""
import os
import sys
import joblib
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import pandas as pd

# Initialize logging
logging.basicConfig(level=logging.WARNING)

app = FastAPI()

# Define paths
MODEL_PATH = os.path.join('{_model_store_dir}', '{self.model_name}', '{self.model_name}_model_object.joblib')

# Change working directory two levels up to access required packages
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.getcwd())  # Add the new working directory to sys.path

# Load the model
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

# Define the data schema for input validation
class PredictionRequest(BaseModel):
    data: Union[List[List[float]], List[dict]]

# Required features for validation
REQUIRED_FEATURES = {self.required_features}

# Prediction endpoint
@app.post("/predict/")
async def predict(request: PredictionRequest):
    # Check if input data is a list of dictionaries or a list of lists
    if isinstance(request.data[0], dict):
        # If input is a list of dictionaries, convert to DataFrame
        data = pd.DataFrame(request.data)

        # Validate for required features
        missing_features = [feature for feature in REQUIRED_FEATURES if feature not in data.columns]
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Missing required features: {{missing_features}}")

        # Select only required features
        data = data[REQUIRED_FEATURES]

    elif isinstance(request.data[0], list):
        # If input is a list of lists, validate each entry's length
        required_feature_count = len(REQUIRED_FEATURES)

        # Check the length of each entry
        for entry in request.data:
            if len(entry) != required_feature_count:
                raise HTTPException(
                    status_code=400,
                    detail=f"Each entry in data should have {{required_feature_count}} features, but received {{len(entry)}}."
                )

        # Log a warning about non-dictionary input format
        logging.warning("Received input in non-dictionary format. Assuming order of features matches model input order.")

        # Convert list of lists to DataFrame
        data = pd.DataFrame(request.data, columns=REQUIRED_FEATURES)
    else:
        raise HTTPException(status_code=400, detail="Invalid input format. Provide a list of dictionaries or list of lists.")

    # Generate predictions
    predictions = model.predict(data)

    # Return predictions in response
    return {{ "predictions": predictions.tolist() }}

# Run Uvicorn server
if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Port number for the service.")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
"""
        return code
