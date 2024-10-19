python -m venv mlops-env
mlops-env\Scripts\activate
pip install jupyter ipykernel
python -m ipykernel install --user --name mlops-env --display-name "Python (mlops-env)"
