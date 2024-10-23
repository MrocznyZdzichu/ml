class Model:
    def __init__(self, name, estimator_class, dataset_name, estimator_parameters,
                 estimator, features_names, dataroles):
        self.__estimator_class = estimator_class
        self.__dataset_name = dataset_name
        self.__estimator_parameters = estimator_parameters
        self.__estimator_object = estimator
        self.__features = features_names
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

    def get_features(self):
        return self.__features

    def get_target(self):
        return self.__target
