def log_batchscore_generation(dbm, model_name, status, details=None):
    insert_query = """
    insert into BATCHSCORE_GENERATIONS (MODEL_NAME, STATUS, DETAILS)
    values (:model_name, :status, :details)
    """
    params = {
        "model_name" : model_name,
        "status"     : status,
        "details"    : details
    }
    dbm.execute_insert(insert_query, params)