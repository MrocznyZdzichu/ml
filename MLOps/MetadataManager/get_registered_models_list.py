def get_registered_models_list(dbm):
    models_query = """
    SELECT MODEL_NAME
    FROM MODELS
    """
    models = [row[0] for row in dbm.run_query(models_query)]
    return models