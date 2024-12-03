from datetime import datetime


def register_dataset(dbm, name, type, location, has_header, is_structured=None, is_tabelaric=None, description=None):
    """
    Registers a new dataset in the database by inserting its details into the 'DATASETS' table.

    Args:
        dbm: Database manager or connection object used to execute the query.
        name (str): The name of the dataset.
        type (str): The type of the dataset (e.g., 'csv', 'json', etc.).
        location (str): The location or path where the dataset is stored.
        is_structured (int, optional): Flag indicating if the dataset is structured (1 for True, 0 for False). 
                                       Defaults to None.
        is_tabelaric (int, optional): Flag indicating if the dataset is tabular. If not provided, 
                                      defaults to the value of `is_structured`. Defaults to None.
        description (str, optional): A description of the dataset. Defaults to None.

    Returns:
        None

    Side Effects:
        Executes an INSERT SQL query, adding a new record to the 'DATASETS' table with the provided details.

    Notes:
        - If `is_structured` is not equal to 1, the value of `is_tabelaric` is set to the same value as `is_structured`.
        - The dataset is marked as active (`IS_ACTIVE` = 1) by default.
    """
    
    if is_structured != 1:
        is_tabelaric = is_structured

    insert_query = """
            INSERT INTO DATASETS (NAME, TYPE, LOCATION, IS_STRUCTURED, IS_TABELARIC, HEADERS_IN_SOURCE, DESCRIPTION, IS_ACTIVE)
            VALUES (:name, :type, :location, :is_structured, :is_tabelaric, :has_header, :description, :is_active)
    """
    data_dict = {
        'name': name,
        'type': type,
        'location': location,
        'has_header': has_header,
        'is_structured': is_structured,
        'is_tabelaric': is_tabelaric,
        'description': description,
        'is_active' : 1
    }

    dbm.execute_insert(insert_query, data_dict)