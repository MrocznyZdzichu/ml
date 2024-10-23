import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

from ..DataGoverner import *
from ..Model import Model


def _is_target_definiton_missing(datarole_mapping):
    return len([col_name for col_name in datarole_mapping if datarole_mapping[col_name].lower() == 'target']) != 1


def create_model(dbm, model_name, dataset_name, model_class, model_params, datarole_mapping, test_size=0.2, random_state=42):
    """
    Fetch dataset metadata, prepare the dataset, and create a machine learning model.

    :param dbm: Instance of DBManager to interact with the database
    :param dataset_name: Name of the dataset to be used for the model
    :param model_class: Scikit-learn model class (e.g., sklearn.linear_model.LogisticRegression)
    :param model_params: Dictionary of model parameters to be passed to the model
    :param target_column: Name of the target column (optional, inferred from 'DATAROLE' if not provided)
    :param test_size: Fraction of the dataset to be used as the test set
    :param random_state: Random state for reproducibility of train-test split
    :return: Trained model and performance metric (accuracy or MSE)
    """
    
    df = load_tabular_dataset(dbm, dataset_name)
    
    if _is_target_definiton_missing(datarole_mapping):
        raise ValueError("Target column not found. Please specify exactly one target_column.")

    target_column   = [col_name for col_name in datarole_mapping if datarole_mapping[col_name].lower() == 'target']
    feature_columns = [col_name for col_name in datarole_mapping if datarole_mapping[col_name].lower() == 'input']
    
    # Define features (X) and target (y)
    X = df[feature_columns]
    y = df[target_column]

    # Split the dataset into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    # Initialize the model with the given parameters
    estimator = model_class(**model_params)
    estimator.fit(X_train, y_train)

    model = Model(model_name, estimator_class=model_class, dataset_name=dataset_name, 
                  estimator_parameters=model_params, estimator=estimator,
                  features_names= feature_columns, dataroles=datarole_mapping)
    
    return model