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
import hashlib
from datetime import datetime

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__))))
if not os.path.exists('score-results'):
    os.makedirs('score-results')
if not os.path.exists(os.path.join('score-results', 'batch')):
    os.makedirs(os.path.join('score-results', 'batch'))

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.getcwd())

OUTPUT_FILE = 'batch_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")
MODEL_PATH  = os.path.join('model-repository', '{self.model_name}', '{self.model_name}_model_object.joblib')
OUTPUT_PATH = os.path.join('model-repository', '{self.model_name}', 'score-results', 'batch', OUTPUT_FILE)

REQUIRED_FEATURES = {self.required_features}

def load_model():
    model = joblib.load(MODEL_PATH)
    return model

def validate_input_data(data):
    missing_features = [feature for feature in REQUIRED_FEATURES if feature not in data.columns]
    if missing_features:
        raise ValueError(f"Input data is missing the following required features: {{missing_features}}")
    return data[REQUIRED_FEATURES]

def generate_row_id(row):
    row_string = '_'.join(str(v) for v in row)
    print(row_string)
    return hashlib.md5(row_string.encode('utf-8')).hexdigest()

def score_batch(input_data_path, has_headers=True):
    if has_headers:
        data = pd.read_csv(input_data_path)
    else:
        data = pd.read_csv(input_data_path, header=None)
        if data.shape[1] != len(REQUIRED_FEATURES):
            raise ValueError(f"The number of columns in the CSV ({{data.shape[1]}}) does not match the number of required input features ({{len(REQUIRED_FEATURES)}}).")
        print("Warning: The provided CSV does not contain headers. Assuming the columns are in the correct order.")
        data.columns = REQUIRED_FEATURES
    row_ids = data.apply(generate_row_id, axis=1)
    data = validate_input_data(data)
    model = load_model()
    predictions = model.predict(data)
    output_df = pd.DataFrame({{
        'row_id': row_ids,
        '{self.target}': predictions
    }})
    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Predictions saved to {{OUTPUT_PATH}}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch scoring")
    parser.add_argument("input_data_path", type=str, help="Path to input data CSV")
    parser.add_argument("--no-headers", action='store_true', help="Specify if the input CSV does not contain headers")
    args = parser.parse_args()
    score_batch(args.input_data_path, has_headers=not args.no_headers)

"""
        return code