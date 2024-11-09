import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

from ..DataGoverner import *
from ..Model import Model

from .ModelCreatorAbst import ModelCreatorAbst


class ModelCreatorBasic(ModelCreatorAbst):
    def __init__(self, model_name, dataset_name, model_class, model_params, datarole_mapping, test_size=0.2, random_state=42):
        self.__model_name       = model_name
        self.__dataset_name     = dataset_name
        self.__model_class      = model_class
        self.__model_params     = model_params
        self.__datarole_mapping = datarole_mapping
        self.__test_size        = test_size
        self.__random_state     = random_state
    
    def __is_target_definiton_missing(self, datarole_mapping):
        return len([col_name for col_name in datarole_mapping if datarole_mapping[col_name].lower() == 'target']) != 1
        
    def create_model(self, dbm, in_docker=False):
        df = load_tabular_dataset(dbm, self.__dataset_name, in_docker=in_docker)
    
        if self.__is_target_definiton_missing(self.__datarole_mapping):
            raise ValueError("Target column not found. Please specify exactly one target_column.")
    
        target_column   = [col_name for col_name in self.__datarole_mapping if self.__datarole_mapping[col_name].lower() == 'target']
        feature_columns = [col_name for col_name in self.__datarole_mapping if self.__datarole_mapping[col_name].lower() == 'input']
        
        # Define features (X) and target (y)
        X = df[feature_columns]
        y = df[target_column]
    
        # Split the dataset into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.__test_size, random_state=self.__random_state)
        
        # Initialize the model with the given parameters
        estimator = self.__model_class(**self.__model_params)
        estimator.fit(X_train, y_train)
    
        model = Model(
            name                 = self.__model_name,
            estimator_class      = self.__model_class, 
            dataset_name         = self.__dataset_name, 
            estimator_parameters = self.__model_params, 
            estimator            = estimator,
            features_names       = feature_columns, 
            dataroles            = self.__datarole_mapping\
        )
        
        return model