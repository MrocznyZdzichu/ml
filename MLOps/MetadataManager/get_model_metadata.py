from .get_model_id import get_model_id
import oracledb
import ast

def get_model_metadata(dbm, model_name):
    id = get_model_id(dbm, model_name)

    model_info_query = """
select
    MODEL_NAME,
    ESTIMATOR_CLASS,
    DATASET_NAME,
    ESTIMATOR_PARAMETERS,
    CREATED_AT
from MODELS
where
    MODEL_ID = :model_id
    """
    model_dataroles_query = """
select 
    COLUMN_NAME,
    DATATYPE,
    DATALEVEL,
    DATAROLE
from COLUMNS_ROLES_MODEL ROLES
    left join DATASET_DETAILS_TAB DET
        on ROLES.DETAIL_ID = DET.DETAIL_ID
where
    ROLES.MODEL_ID = :model_id
    """ 
    models_info      =  list(dbm.run_query(model_info_query, {'model_id' : id})[0])
    models_dataroles = list([list(row) for row in dbm.run_query(model_dataroles_query, {'model_id' : id})])

    parameters_dict_index = 3
    models_info[parameters_dict_index] = ast.literal_eval(models_info[parameters_dict_index])
    
    return models_info, models_dataroles