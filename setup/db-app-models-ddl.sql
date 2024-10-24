CREATE TABLE MLAPP.MODELS (
    MODEL_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    MODEL_NAME VARCHAR2(100) NOT NULL UNIQUE,
    ESTIMATOR_CLASS VARCHAR2(255) NOT NULL,
    DATASET_NAME VARCHAR2(64) NOT NULL,  -- Powi�zane z tabel� DATASETS
    ESTIMATOR_PARAMETERS CLOB,  -- JSON or serialized parameters
    FEATURES CLOB,  -- JSON or serialized list of feature column names
    TARGET_COLUMN VARCHAR2(255) NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP,
    DELETED_AT TIMESTAMP,  -- Kolumna oznaczaj�ca usuni�cie modelu
    CONSTRAINT FK_MODELS_DATASET_NAME FOREIGN KEY (DATASET_NAME)
        REFERENCES MLAPP.DATASETS (NAME)  -- Klucz obcy do tabeli DATASETS
);


CREATE OR REPLACE TRIGGER trg_update_model_timestamp
BEFORE UPDATE ON MLAPP.MODELS
FOR EACH ROW
BEGIN
    :NEW.UPDATED_AT := CURRENT_TIMESTAMP;
END;
/