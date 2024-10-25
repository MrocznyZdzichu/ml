import os
import json
import joblib


_model_store_dir = 'ModelsRepository'


class Model:
    def __init__(self, name, estimator_class, dataset_name, estimator_parameters,
                 estimator, features_names, dataroles):
        self.__estimator_class = estimator_class
        self.__dataset_name = dataset_name
        self.__estimator_parameters = estimator_parameters
        self.__estimator_object = estimator
        self.__name = name
        self.__dataroles = dataroles

    def predict(self, X):
        return self.__estimator_object.predict(X)

    # Getter methods
    def get_name(self):
        return self.__name

    def get_estimator_class(self):
        return self.__estimator_class

    def get_dataset_name(self):
        return self.__dataset_name

    def get_estimator_parameters(self):
        return self.__estimator_parameters

    def get_storage_localization(self):
        return self.__localization

    def set_storage_localization(self, store_dir):
        self.__localization = store_dir

    def get_dataroles(self):
        return self.__dataroles
        
    def save_model(self):
        self.__create_model_dir()
        model_path = os.path.join(_model_store_dir, self.__name, f'{self.__name}_model_object.joblib')
        joblib.dump(self, model_path)

        metadata = {
            "name": self.__name,
            "estimator_class": self.__estimator_class.__name__,
            "dataset_name": self.__dataset_name,
            "estimator_parameters": self.__estimator_parameters,
            "dataroles": self.__dataroles
        }
        
        metadata_path = os.path.join(_model_store_dir, self.__name, f'{self.__name}_metadata.json')
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        self.set_storage_localization(os.path.join(_model_store_dir, self.__name))
    
    def __create_model_dir(self):
        if not os.path.exists(_model_store_dir):
            os.makedirs(_model_store_dir)

        specific_dir = os.path.join(_model_store_dir, self.__name)
        if not os.path.exists(os.path.join(specific_dir)):
            os.makedirs(specific_dir)