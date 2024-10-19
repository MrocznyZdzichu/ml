import json
from datetime import datetime

def register_model(dbm, model):
    """
    Insert a trained model's metadata into the MLAPP.MODELS table.
    
    :param dbm: Instance of DBManager to interact with the database
    :param model: Instance of the trained model (Model class)
    :return: None
    """
    
    # Prepare data for insert using getters
    model_name = model.get_name()
    estimator_class = model.get_estimator_class().__name__
    dataset_name = model.get_dataset_name()
    estimator_parameters = json.dumps(model.get_estimator_parameters())  # Serialize parameters to JSON
    features = json.dumps(model.get_features())  # Serialize feature list to JSON
    target_column = model.get_target()
    created_at = datetime.now()
    deleted_at = None  # By default, model is not deleted (DELETED_AT is NULL)
    
    # Insert query
    insert_query = """
    INSERT INTO MLAPP.MODELS 
    (MODEL_NAME, ESTIMATOR_CLASS, DATASET_NAME, ESTIMATOR_PARAMETERS, FEATURES, TARGET_COLUMN, CREATED_AT, DELETED_AT)
    VALUES (:model_name, :estimator_class, :dataset_name, :estimator_parameters, :features, :target_column, :created_at, :deleted_at)
    """
    
    # Execute insert
    dbm.execute_insert(insert_query, {
        'model_name': model_name,
        'estimator_class': estimator_class,
        'dataset_name': dataset_name,
        'estimator_parameters': estimator_parameters,
        'features': features,
        'target_column': target_column,
        'created_at': created_at,
        'deleted_at': deleted_at
    })
