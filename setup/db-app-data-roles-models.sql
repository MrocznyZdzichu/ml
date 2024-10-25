CREATE TABLE MLAPP.COLUMNS_ROLES_MODEL (
    ROLE_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    DETAIL_ID NUMBER NOT NULL,
    MODEL_ID NUMBER NOT NULL,
    DATAROLE VARCHAR2(20) NOT NULL CHECK (DATAROLE IN ('input', 'target', 'id', 'time')),
    DATE_FROM TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    DATE_TO TIMESTAMP,
    IS_ACTIVE NUMBER(1) NOT NULL CHECK (IS_ACTIVE IN (0, 1)),
    CONSTRAINT FK_DETAIL_ID FOREIGN KEY (DETAIL_ID) REFERENCES MLAPP.DATASET_DETAILS_TAB (DETAIL_ID),
    CONSTRAINT FK_MODEL_ID FOREIGN KEY (MODEL_ID) REFERENCES MLAPP.MODELS (MODEL_ID),
    CONSTRAINT UNQ_DETAIL_MODEL UNIQUE (DETAIL_ID, MODEL_ID)
);
