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

    def generate_batch_score_code(self):
        """Generates a score_batch.py file for batch scoring."""
        
        # Wybierz kolumny o roli 'input'
        required_features = [feature for feature, role in self.__dataroles.items() if role == 'input']
        
        code = f"""
import os
import pandas as pd
import joblib
import sys

# Change working directory two levels up to access required packages
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.getcwd())  # Add the new working directory to sys.path

# Define paths
MODEL_PATH = os.path.join('{_model_store_dir}', '{self.__name}', '{self.__name}_model_object.joblib')
OUTPUT_PATH = os.path.join('{_model_store_dir}', '{self.__name}', '{self.__name}_batch_predictions.csv')

# Required features
REQUIRED_FEATURES = {required_features}

def load_model():
    # Load the model from file
    model = joblib.load(MODEL_PATH)
    return model

def validate_input_data(data):
    # Validate the input data for required features.
    missing_features = [feature for feature in REQUIRED_FEATURES if feature not in data.columns]
    if missing_features:
        raise ValueError(f"Input data is missing the following required features: {{missing_features}}")
    
    return data[REQUIRED_FEATURES]

def score_batch(input_data_path, has_headers=True):
    # Load input data
    if has_headers:
        data = pd.read_csv(input_data_path)
    else:
        # Load CSV without headers
        data = pd.read_csv(input_data_path, header=None)

        # Check if the number of columns matches the number of required features
        if data.shape[1] != len(REQUIRED_FEATURES):
            raise ValueError(f"The number of columns in the CSV ({{data.shape[1]}}) does not match the number of required input features ({{len(REQUIRED_FEATURES)}}).")

        # Print a warning about missing headers
        print("Warning: The provided CSV does not contain headers. Assuming the columns are in the correct order.")

        # Create a DataFrame with required feature names
        data.columns = REQUIRED_FEATURES  # Set column names to match required features

    # Validate and filter input data
    data = validate_input_data(data)
    
    # Load the model
    model = load_model()

    # Make predictions
    predictions = model.predict(data)
    
    # Save predictions to CSV
    output_df = pd.DataFrame(predictions, columns=['prediction'])
    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Predictions saved to {{OUTPUT_PATH}}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch scoring")
    parser.add_argument("input_data_path", type=str, help="Path to input data CSV")
    parser.add_argument("--no-headers", action='store_true', help="Specify if the input CSV does not contain headers")
    args = parser.parse_args()

    # Determine if the CSV has headers based on the command-line argument
    score_batch(args.input_data_path, has_headers=not args.no_headers)
"""
        # Define the path to save the generated script
        script_path = os.path.join(_model_store_dir, self.__name, 'score_batch.py')
        
        # Write the code to the script file
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Print information with environment activation and deactivation for PowerShell
        print(f"Batch scoring script generated at: \"{script_path}\"")
        print("To run the script, please activate your virtual environment located in 'mlops-env', execute the script, and then deactivate the environment as follows:")
        print(f".\\mlops-env\\Scripts\\Activate\npython \"{script_path}\" \"<path/to/input_data.csv>\" [--no-headers]\ndeactivate")
