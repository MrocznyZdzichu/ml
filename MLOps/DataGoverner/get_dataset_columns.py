def get_datasets_columns(dbm, dataset_name, details=False):
    sql_addon = ", DATATYPE, DATALEVEL" if details else ""
    dataset_query = f"""
    SELECT COLUMN_NAME{sql_addon}
    FROM DATASET_DETAILS_TAB
    where DATASET_NAME = :dataset_name
    order by COLUMN_ORDER
    """
    if details:
        dataset_columns = [row for row in dbm.run_query(dataset_query, {'dataset_name' : dataset_name})]
    else:
        dataset_columns = [row[0] for row in dbm.run_query(dataset_query, {'dataset_name' : dataset_name})]
        
    return dataset_columns