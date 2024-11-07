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

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import os
import inspect
import json

from MLOps.ModelManager import ModelCreatorBasic
from MLOps.DBManager import DBManager 
from MLOps.DataGoverner import get_datasets_list

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
        "KMeans": KMeans,  # KMeans is a clustering model but often used for classification tasks too
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
        "SGDRegressor": SGDClassifier,  # SGDRegressor is similar to SGDClassifier
        "EllipticEnvelope": EllipticEnvelope,  # Robust regression model
    }
}

app = FastAPI()

templates = Jinja2Templates(directory="templates")
model_repository_dir = "/app/model-repository"

dbm = DBManager(dev_db=True, in_docker=True)

@app.get("/", response_class=HTMLResponse)
async def create_model_form(request: Request):
    datasets = get_datasets_list(dbm)
    return templates.TemplateResponse("index.html", {"request": request, "datasets": datasets, "models": available_models})

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

    model_type, model_class_name = model_class.split(".", 1)
    if model_type not in available_models or model_class_name not in available_models[model_type]:
        return {"error": "Invalid model class selected"}

    model_class_instance = available_models[model_type][model_class_name](**model_params)

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
