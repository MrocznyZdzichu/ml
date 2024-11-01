import os
import json
import joblib

from MLOps.CodeGeneration import BatchScoreCodeGenerator, OnlineScoreCodeGenerator, DockerScoreCodeGenerator
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

    def generate_batch_score_code(self):
        """Generates a scoring script using BatchScoreCodeGenerator."""
        # Select columns with the role 'input'
        required_features = [feature for feature, role in self.__dataroles.items() if role == 'input']
        target_name       = [feature for feature, role in self.__dataroles.items() if role == 'target'][0]
        
        # Create a BatchScoreCodeGenerator object
        code_generator = BatchScoreCodeGenerator(self.__name, required_features, target_name)
        
        # Generate code
        code = code_generator.generate_code()
        
        # Define the path to save the generated script
        script_path = os.path.join(_model_store_dir, self.__name, 'score_batch.py')
        
        # Write the code to the script file
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Print information with environment activation and deactivation for PowerShell
        print(f"Batch scoring script generated at: \"{script_path}\"")
        print("To run the script, please activate your virtual environment located in 'mlops-env', execute the script, and then deactivate the environment as follows:")
        print(f".\\mlops-env\\Scripts\\Activate\npython \"{script_path}\" \"<path/to/input_data.csv>\" [--no-headers]\ndeactivate")

    def generate_online_score_code(self):
        """Generates an online scoring script using OnlineScoreCodeGenerator."""
        # Select columns with the role 'input'
        required_features = [feature for feature, role in self.__dataroles.items() if role == 'input']
        target_name = [feature for feature, role in self.__dataroles.items() if role == 'target'][0]
        
        # Create an OnlineScoreCodeGenerator object
        code_generator = OnlineScoreCodeGenerator(self.__name, required_features, target_name)
        
        # Generate code
        code = code_generator.generate_code()
        
        # Define the path to save the generated script
        script_path = os.path.join(_model_store_dir, self.__name, 'online_service.py')
        
        # Write the code to the script file
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Print information with environment activation and deactivation for PowerShell
        print(f"Online scoring service script generated at: \"{script_path}\"")
        print("To run the service, activate your virtual environment located in 'mlops-env' and execute the script as follows:")
        print(f".\\mlops-env\\Scripts\\Activate\npython \"{script_path}\" --port <port_number>\ndeactivate")

    def generate_docker_score_code(self, container_port=8000):
        """Generates a Dockerized scoring service script using DockerScoreCodeGenerator with a specified container port."""
        required_features = [feature for feature, role in self.__dataroles.items() if role == 'input']
        target_name = [feature for feature, role in self.__dataroles.items() if role == 'target'][0]

        code_generator = DockerScoreCodeGenerator(self.__name, required_features, target_name, container_port)
        
        code_generator.generate_code()

        model_dir = os.path.join(_model_store_dir, self.__name)
        dockerfile_path = os.path.join(model_dir, 'Dockerfile')
        app_script_path = os.path.join(model_dir, 'app.py')
        docker_compose_path = os.path.join(model_dir, 'docker-compose.override.yml')
        
        service_name = self.__name.replace(" ", "-").lower()
        
        print(f"Dockerized scoring service generated for model '{self.__name}' in 'ModelsRepository\\{self.__name}'.")
        print("Files generated:")
        print(f"- Dockerfile: ModelsRepository\\{self.__name}\\Dockerfile")
        print(f"- FastAPI app script: ModelsRepository\\{self.__name}\\app.py")
        print(f"- Docker Compose override configuration: ModelsRepository\\{self.__name}\\docker-compose.override.yml")
        print("To deploy the service in Docker, build the image and start the container with Docker Compose:")
        print(f'docker-compose -f "ModelsRepository\\{self.__name}\\docker-compose.override.yml" up --build "{service_name}-service"')
        print('or use run_compose.py script to run all overrides')


