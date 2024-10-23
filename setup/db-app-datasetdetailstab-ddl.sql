CREATE TABLE MLAPP.DATASET_DETAILS_TAB (
    DETAIL_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    DATASET_NAME VARCHAR2(64),
    COLUMN_NAME VARCHAR2(64) NOT NULL,
    DATATYPE VARCHAR2(64) NOT NULL,
    DATALEVEL VARCHAR2(20) CHECK (DATALEVEL IN ('category', 'ranking', 'value', null)),
    COLUMN_ORDER number not null
);

ALTER TABLE MLAPP.DATASET_DETAILS_TAB
ADD CONSTRAINT FK_DATASET_NAME
FOREIGN KEY (DATASET_NAME) REFERENCES MLAPP.DATASETS (NAME);

ALTER TABLE MLAPP.DATASET_DETAILS_TAB
ADD CONSTRAINT UNQ_DATASET_COLUMN UNIQUE (DATASET_NAME, COLUMN_NAME);

ALTER TABLE MLAPP.DATASET_DETAILS_TAB
ADD CONSTRAINT UNQ_DATASET_COLUMN_ORDER UNIQUE (DATASET_NAME, COLUMN_ORDER );
