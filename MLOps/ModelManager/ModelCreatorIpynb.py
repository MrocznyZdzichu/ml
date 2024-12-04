import nbformat
from nbconvert import PythonExporter
import tempfile
import os
import runpy
from .ModelCreatorAbst import ModelCreatorAbst

class ModelCreatorIpynb(ModelCreatorAbst):
    """
    Class for creating a machine learning model based on a Jupyter notebook (.ipynb),
    converting it to a Python script and executing the script to retrieve the model object.

    Assumptions for the converted notebook:
    - The notebook uses `IN_DOCKER = os.getenv('IN_DOCKER') == 'Yes'` as an `in_docker` argument.
    - The notebook creates an object of the `Model` class named `model`. This object is expected
      to be defined at the end of the model creation process.
    - Data for the model is registered in metadata and loaded using the `load_tabular_dataset`
      function from the `MLOps.MetadataManager` module.

    Args:
        notebook_path (str): Path to the notebook (.ipynb) file to be converted.
        out_var_name (str, optional): Name of the model variable to be returned.
                                      Default is 'model'.

    Attributes:
        __notebook_path (str): Path to the notebook (.ipynb) file.
        __out_var_name (str): Name of the model variable in the notebook.
        __script_path (str): Path to the temporary .py file after notebook conversion.
    """

    def __init__(self, notebook_path, out_var_name='model'):
        self.__notebook_path = notebook_path
        self.__out_var_name  = out_var_name
        self.__script_path   = None

    def create_model(self):
        """
        Creates a model from the notebook by converting it to a Python script
        and executing the script.

        Returns:
            object: The created model object, expected to be `self.__out_var_name`.

        Raises:
            ValueError: If `self.__out_var_name` variable was not created in the notebook.
        """
        self.__script_path = self.__notebook_to_script()
        model = self.__run_script_and_get_model()
        self.__delete_script()
        return model

    def __notebook_to_script(self):
        """
        Converts the notebook (.ipynb) to a Python script (.py).

        Returns:
            str: Path to the temporary .py file.
        """
        with open(self.__notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)
    
        exporter = PythonExporter()
        python_code, _ = exporter.from_notebook_node(notebook_content)   

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w', encoding='utf-8') as temp_file:
            temp_file.write(python_code)
            temp_file_path = temp_file.name

        return temp_file_path

    def __delete_script(self):
        """
        Deletes the temporary .py file created during notebook conversion.
        """
        os.remove(self.__script_path)
        self.__script_path = None

    def __run_script_and_get_model(self):
        """
        Executes the Python script and retrieves the created model object.

        Returns:
            object: The created model object.

        Raises:
            ValueError: If the variable `self.__out_var_name` was not created in the script.
        """
        variables = runpy.run_path(self.__script_path)
        model = variables.get(self.__out_var_name)

        if model is None:
            raise ValueError(f"The variable '{self.__out_var_name}' was not created in the notebook.")

        return model
