import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

from ..DataGoverner import *
from ..Model import Model


def _fetch_dataset_metadata(dbm, dataset_name):
    """
    Fetch dataset details from the database based on the dataset name.

    :param dbm: Instance of DBManager to interact with the database
    :param dataset_name: Name of the dataset to fetch metadata for
    :return: List of column details (column_name, datatype, datarole, datalevel, column_order)
    """
    query = """
    SELECT COLUMN_NAME, DATATYPE, DATAROLE, DATALEVEL
    FROM MLAPP.DATASET_DETAILS_TAB
    WHERE DATASET_NAME = :dataset_name
    ORDER BY COLUMN_ORDER
    """
    
    result = dbm.run_query(query, {'dataset_name': dataset_name})
    return result


def create_model(dbm, model_name, dataset_name, model_class, model_params, target_column=None, test_size=0.2, random_state=42):
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
    
    metadata_query = """
    SELECT COLUMN_NAME, DATAROLE
    FROM MLAPP.DATASET_DETAILS_TAB
    WHERE DATASET_NAME = :dataset_name
    ORDER BY COLUMN_ORDER
    """
    metadata = dbm.run_query(metadata_query, {'dataset_name': dataset_name})
    
    # Prepare feature columns and identify the target column
    feature_columns = []
    for column_name, datarole in metadata:
        if datarole.upper() == 'TARGET':
            target_column = column_name
        else:
            feature_columns.append(column_name)
    
    if not target_column:
        raise ValueError("Target column not found. Please specify the target_column or ensure it is marked in the database.")
    
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
                  features_names= feature_columns, target_name=target_column)
    
    return model