import pandas as pd

def load_tabular_dataset(dbm, dataset_name):
    """
    Loads a dataset into a pandas DataFrame based on metadata from the DATASETS and DATASET_DETAILS_TAB tables.

    Args:
        dbm: Database manager object to interact with the database.
        dataset_name (str): The name of the dataset to be loaded.
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing the loaded dataset.
    """

    dataset_query = """
    SELECT LOCATION, HEADERS_IN_SOURCE 
    FROM MLAPP.DATASETS 
    WHERE NAME = :dataset_name
    """
    dataset_info = dbm.run_query(dataset_query, {'dataset_name': dataset_name})[0]
    dataset_location = dataset_info[0]
    headers_in_source = dataset_info[1]

    columns_query = """
    SELECT COLUMN_NAME, DATATYPE 
    FROM MLAPP.DATASET_DETAILS_TAB 
    WHERE DATASET_NAME = :dataset_name
    ORDER BY COLUMN_ORDER
    """
    columns_info = dbm.run_query(columns_query, {'dataset_name': dataset_name})
    
    column_names = [col[0] for col in columns_info]
    dtypes = {col[0]: col[1] for col in columns_info}

    dtype_mapping = {'float': 'float64', 'string': 'object', 'int': 'float64'}
    pandas_dtypes = {col: dtype_mapping[dtypes[col]] for col in dtypes}

    if headers_in_source == 1:
        df = pd.read_csv(dataset_location, dtype=pandas_dtypes, header=0) 
    else:
        df = pd.read_csv(dataset_location, names=column_names, dtype=pandas_dtypes)

    return df
