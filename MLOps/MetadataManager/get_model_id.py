def get_model_id(dbm, model_name):
    models_query = """
    SELECT MODEL_ID
    FROM MODELS
    WHERE MODEL_NAME = :model_name
    """
    model_id = [row[0] for row in dbm.run_query(models_query, {'model_name' : model_name})][0]
    return model_id