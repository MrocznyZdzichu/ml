def get_datasets_list(dbm):
    dataset_query = """
    SELECT NAME
    FROM DATASETS 
    """
    datasets = [row[0] for row in dbm.run_query(dataset_query)]
    return datasets