class ModelCreatorAbst:
    def create_model(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")
        