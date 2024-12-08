from datetime import datetime

from .CodeGenerator import CodeGenerator
_model_store_dir = 'model-repository'


class BatchScoreCodeGenerator(CodeGenerator):
    def __init__(self, model_name, required_features, target):
        self.model_name = model_name
        self.required_features = required_features
        self.target = target

    def generate_code(self):
        """Generates the batch scoring script code."""
        code = f"""
import os
import pandas as pd
import joblib
import sys

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__))))
if not os.path.exists('score-results'):
    os.makedirs('score-results')
if not os.path.exists(os.path.join('score-results', 'batch')):
    os.makedirs(os.path.join('score-results', 'batch'))

# Change working directory two levels up to access required packages
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.getcwd())  # Add the new working directory to sys.path

# Define paths
MODEL_PATH = os.path.join('{_model_store_dir}', '{self.model_name}', '{self.model_name}_model_object.joblib')
OUTPUT_PATH = os.path.join('{_model_store_dir}', '{self.model_name}', 'score-results', 'batch', f'batch_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv')

# Required features
REQUIRED_FEATURES = {self.required_features}

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
    output_df = pd.DataFrame(predictions, columns=[f'{self.target}'])
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
        return code