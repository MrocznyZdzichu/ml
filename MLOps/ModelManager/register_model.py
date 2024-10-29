import json
from datetime import datetime


def register_model(dbm, model):
    """
    Insert a trained model's metadata into the MLAPP.MODELS table.
    
    :param dbm: Instance of DBManager to interact with the database
    :param model: Instance of the trained model (Model class)
    :return: None
    """

    model.save_model()
    _insert_models_table(dbm, model)
    _insert_dataroles(dbm, model)

def _insert_models_table(dbm, model):
    insert_query = """
    INSERT INTO MODELS 
    (MODEL_NAME, ESTIMATOR_CLASS, DATASET_NAME, ESTIMATOR_PARAMETERS, LOCALIZATION, CREATED_AT, DELETED_AT)
    VALUES (:model_name, :estimator_class, :dataset_name, :estimator_parameters, :localization, :created_at, :deleted_at)
    """
    insert_model_params = {
        'model_name': model.get_name(),
        'estimator_class': model.get_estimator_class().__name__,
        'dataset_name': model.get_dataset_name(),
        'estimator_parameters': json.dumps(model.get_estimator_parameters()),
        'localization' : model.get_storage_localization(),
        'created_at': datetime.now(),
        'deleted_at': None
    }
    
    dbm.execute_insert(insert_query, insert_model_params)

def _get_model_id(dbm, model):
    """
    Retrieves the MODEL_ID for the given model from the MLAPP.MODELS table.
    """
    select_query = """
    SELECT MODEL_ID 
    FROM MLAPP.MODELS 
    WHERE MODEL_NAME = :model_name
    """
    result = dbm.run_query(select_query, {'model_name': model.get_name()})
    return result[0][0] if result else None


def _get_model_column_id(dbm, model, column):
    """
    Retrieves the DETAIL_ID from the MLAPP.DATASET_DETAILS_TAB for a specific dataset and column.
    """
    select_query = """
    SELECT DETAIL_ID 
    FROM MLAPP.DATASET_DETAILS_TAB 
    WHERE DATASET_NAME = :dataset_name 
    AND COLUMN_NAME = :column_name
    """
    result = dbm.run_query(select_query, {
        'dataset_name': model.get_dataset_name(),
        'column_name': column
    })
    return result[0][0] if result else None


def _insert_dataroles(dbm, model):
    """
    Inserts data roles for each column associated with the model into MLAPP.COLUMNS_ROLES_MODEL.
    """
    roles_insert_query = """
    INSERT INTO MLAPP.COLUMNS_ROLES_MODEL (
        DETAIL_ID, MODEL_ID, DATAROLE, DATE_FROM, DATE_TO, IS_ACTIVE
    ) VALUES (
        :detail_id, :model_id, :datarole, :date_from, :date_to, :is_active
    )
    """

    model_id = _get_model_id(dbm, model)
    
    for column, role in model.get_dataroles().items():
        detail_id = _get_model_column_id(dbm, model, column)
        
        if detail_id is not None:
            roles_insert_params = {
                'detail_id': detail_id,
                'model_id': model_id,
                'datarole': role,
                'date_from': datetime.now(),
                'date_to': None,
                'is_active': 1 
            }
            dbm.execute_insert(roles_insert_query, roles_insert_params)