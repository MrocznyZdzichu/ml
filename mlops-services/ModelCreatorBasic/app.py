from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, VotingClassifier, BaggingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet, BayesianRidge, SGDClassifier, PassiveAggressiveClassifier, Perceptron
from sklearn.svm import SVC, SVR, LinearSVC
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.gaussian_process import GaussianProcessClassifier, GaussianProcessRegressor
from sklearn.covariance import EllipticEnvelope
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.isotonic import IsotonicRegression

from fastapi import FastAPI, Request, Form, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
from pydantic import BaseModel

import os
import json
import requests

from MLOps.ModelManager import ModelCreatorBasic
from MLOps.DBManager import DBManager 

available_models = {
    "classifiers": {
        "RandomForestClassifier": RandomForestClassifier,
        "GradientBoostingClassifier": GradientBoostingClassifier,
        "AdaBoostClassifier": AdaBoostClassifier,
        "VotingClassifier": VotingClassifier,
        "BaggingClassifier": BaggingClassifier,
        "HistGradientBoostingClassifier": HistGradientBoostingClassifier,
        "LogisticRegression": LogisticRegression,
        "SVC": SVC,
        "KNeighborsClassifier": KNeighborsClassifier,
        "DecisionTreeClassifier": DecisionTreeClassifier,
        "GaussianNB": GaussianNB,
        "MultinomialNB": MultinomialNB,
        "BernoulliNB": BernoulliNB,
        "GaussianProcessClassifier": GaussianProcessClassifier,
        "SGDClassifier": SGDClassifier,
        "PassiveAggressiveClassifier": PassiveAggressiveClassifier,
        "Perceptron": Perceptron,
        "LinearDiscriminantAnalysis": LinearDiscriminantAnalysis,
        "QuadraticDiscriminantAnalysis": QuadraticDiscriminantAnalysis,
        "MLPClassifier": MLPClassifier,
        "KMeans": KMeans,
        "SpectralClustering": SpectralClustering,
    },
    "regressors": {
        "Ridge": Ridge,
        "Lasso": Lasso,
        "ElasticNet": ElasticNet,
        "SVR": SVR,
        "KNeighborsRegressor": KNeighborsRegressor,
        "DecisionTreeRegressor": DecisionTreeRegressor,
        "GaussianProcessRegressor": GaussianProcessRegressor,
        "BayesianRidge": BayesianRidge,
        "LinearSVC": LinearSVC,
        "MLPRegressor": MLPRegressor,
        "IsotonicRegression": IsotonicRegression,
        "SGDRegressor": SGDClassifier,
        "EllipticEnvelope": EllipticEnvelope,
    }
}

IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'

app = FastAPI()

templates = Jinja2Templates(directory="templates")
model_repository_dir = "/app/model-repository"

dbm = DBManager(dev_db=True, in_docker=IN_DOCKER)

def get_datasets_list_from_metadata_service():
    response = requests.get("http://mlops-metadata-server-1:4044/datasets")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching datasets list")
    return response.json()

def get_dataset_columns_from_metadata_service(dataset_name: str, details: bool = False):
    response = requests.get(f"http://mlops-metadata-server-1:4044/datasets/{dataset_name}/columns", params={"details": details})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching dataset columns")
    return response.json()

@app.get("/", response_class=HTMLResponse)
async def create_model_form(request: Request):
    datasets = get_datasets_list_from_metadata_service()
    return templates.TemplateResponse("index.html", {"request": request, "datasets": datasets, "models": available_models})

@app.get("/get_dataset_columns")
async def get_dataset_columns(dataset_name: str):
    columns = get_dataset_columns_from_metadata_service(dataset_name, details=True)
    return [{"name": col[0], "datatype": col[1], "datalevel": col[2]} for col in columns]

class ModelCreateRequest(BaseModel):
    model_name: str
    dataset_name: str
    model_class: str
    model_params: str
    datarole_mapping: Dict[str, str]
    test_size: float = 0.2
    random_state: int = 42
    
@app.post("/create_model")
async def create_model(request: Request, model: ModelCreateRequest = Body(...)):
    model_params = json.loads(model.model_params) if model.model_params.strip() else {}
    datarole_mapping_dict = {
        column: role for column, role in model.datarole_mapping.items() if role != "ignore"
    }

    model_type, model_class_name = model.model_class.split(".", 1)

    if model_type not in available_models or model_class_name not in available_models[model_type]:
        return {"error": "Invalid model class selected"}

    model_class_instance = available_models[model_type][model_class_name]
    
    model_creator = ModelCreatorBasic(
        model_name=model.model_name,
        dataset_name=model.dataset_name,
        model_class=model_class_instance,
        model_params=model_params,
        datarole_mapping=datarole_mapping_dict,
        test_size=model.test_size,
        random_state=model.random_state
    )
    
    model_instance = model_creator.create_model(dbm, in_docker=IN_DOCKERs)
    model_instance.save_model()

    return RedirectResponse(url="/?message=Model created successfully!", status_code=303)
