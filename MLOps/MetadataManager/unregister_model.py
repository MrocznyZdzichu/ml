def unregister_model(dbm, model_id):
    _delete_dataroles(dbm, model_id)
    _delete_model_meta(dbm, model_id)

def _delete_dataroles(dbm, model_id):
    sql = """
    delete from COLUMNS_ROLES_MODEL where MODEL_ID = :model_id
    """
    params = {'model_id' : model_id}
    dbm.execute_delete(sql, params)

def _delete_model_meta(dbm, model_id):
    sql = """
    delete from MODELS where MODEL_ID = :model_id
    """
    params = {'model_id' : model_id}
    dbm.execute_delete(sql, params)