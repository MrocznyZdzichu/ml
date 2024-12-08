CREATE TABLE MLAPP.DATASET_DETAILS_TAB_HIST (
    HIST_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    DETAIL_ID NUMBER,
    DATASET_NAME VARCHAR2(64),
    COLUMN_NAME VARCHAR2(64),
    DATATYPE VARCHAR2(64),
    DATALEVEL VARCHAR2(20),
    COLUMN_ORDER NUMBER,
    OPERATION_TYPE VARCHAR2(10) CHECK (OPERATION_TYPE IN ('INSERT', 'UPDATE', 'DELETE')),
    OPERATION_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE TRIGGER MLAPP.TRG_DATASET_DETAILS_HISTORY
AFTER INSERT OR UPDATE OR DELETE ON MLAPP.DATASET_DETAILS_TAB
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO MLAPP.DATASET_DETAILS_TAB_HIST (
            DETAIL_ID, DATASET_NAME, COLUMN_NAME, DATATYPE, DATALEVEL, 
            COLUMN_ORDER, OPERATION_TYPE, OPERATION_TIMESTAMP
        )
        VALUES (
            :NEW.DETAIL_ID, :NEW.DATASET_NAME, :NEW.COLUMN_NAME, :NEW.DATATYPE, 
            :NEW.DATALEVEL, :NEW.COLUMN_ORDER, 'INSERT', CURRENT_TIMESTAMP
        );
    ELSIF UPDATING THEN
        INSERT INTO MLAPP.DATASET_DETAILS_TAB_HIST (
            DETAIL_ID, DATASET_NAME, COLUMN_NAME, DATATYPE, DATALEVEL, 
            COLUMN_ORDER, OPERATION_TYPE, OPERATION_TIMESTAMP
        )
        VALUES (
            :NEW.DETAIL_ID, :NEW.DATASET_NAME, :NEW.COLUMN_NAME, :NEW.DATATYPE, 
            :NEW.DATALEVEL, :NEW.COLUMN_ORDER, 'UPDATE', CURRENT_TIMESTAMP
        );
    ELSIF DELETING THEN
        INSERT INTO MLAPP.DATASET_DETAILS_TAB_HIST (
            DETAIL_ID, DATASET_NAME, COLUMN_NAME, DATATYPE, DATALEVEL, 
            COLUMN_ORDER, OPERATION_TYPE, OPERATION_TIMESTAMP
        )
        VALUES (
            :OLD.DETAIL_ID, :OLD.DATASET_NAME, :OLD.COLUMN_NAME, :OLD.DATATYPE, 
            :OLD.DATALEVEL, :OLD.COLUMN_ORDER, 'DELETE', CURRENT_TIMESTAMP
        );
    END IF;
END;
/

ALTER TRIGGER MLAPP.TRG_DATASET_DETAILS_HISTORY ENABLE;