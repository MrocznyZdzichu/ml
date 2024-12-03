def add_tab_details(dbm, dataset_name, columns_dict):
    """
    Adds column details to the MLAPP.DATASETDETAILSTAB table.

    :param db_manager: Instance of the DBManager class
    :param dataset_name: Name of the dataset
    :param columns_dict: List of dictionaries containing column information
    """
    
    insert_query = """
    INSERT INTO MLAPP.DATASET_DETAILS_TAB (DATASET_NAME, COLUMN_NAME, DATATYPE, DATALEVEL, COLUMN_ORDER)
    VALUES (:dataset_name, :column_name, :datatype, :datalevel, :column_order)
    """

    for column in columns_dict:
        if 'column_name' not in column:
            raise ValueError("Each column must have 'column_name' keys.")

        data_dict = {
            'dataset_name': dataset_name,
            'column_name': column['column_name'],
            'datatype': column.get('datatype'),
            'datalevel': column.get('datalevel') ,
            'column_order': column['column_order']
        }

        dbm.execute_insert(insert_query, data_dict)
