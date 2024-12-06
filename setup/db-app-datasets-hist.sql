CREATE TABLE MLAPP.DATASETS_HIST (
    HIST_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    DATASET_ID VARCHAR2(64) NOT NULL,
    NAME VARCHAR2(64),
    TYPE VARCHAR2(64),
    LOCATION VARCHAR2(512),
    ADDED TIMESTAMP,
    DELETED TIMESTAMP,
    IS_STRUCTURED NUMBER,
    IS_TABELARIC NUMBER,
    HEADERS_IN_SOURCE NUMBER,
    DESCRIPTION VARCHAR2(1024),
    ROW_MOD_DTTM TIMESTAMP,
    IS_ACTIVE NUMBER,
    OPERATION_TYPE VARCHAR2(10) CHECK (OPERATION_TYPE IN ('INSERT', 'UPDATE', 'DELETE')) NOT NULL,
    CHANGED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE OR REPLACE TRIGGER MLAPP.TRG_DATASETS_HISTORY
AFTER INSERT OR UPDATE OR DELETE ON MLAPP.DATASETS
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO MLAPP.DATASETS_HIST (
            DATASET_ID, NAME, TYPE, LOCATION, ADDED, DELETED, 
            IS_STRUCTURED, IS_TABELARIC, HEADERS_IN_SOURCE, 
            DESCRIPTION, ROW_MOD_DTTM, IS_ACTIVE, OPERATION_TYPE
        )
        VALUES (
            :NEW.ID, :NEW.NAME, :NEW.TYPE, :NEW.LOCATION, :NEW.ADDED, :NEW.DELETED,
            :NEW.IS_STRUCTURED, :NEW.IS_TABELARIC, :NEW.HEADERS_IN_SOURCE,
            :NEW.DESCRIPTION, :NEW.ROW_MOD_DTTM, :NEW.IS_ACTIVE, 'INSERT'
        );
    ELSIF UPDATING THEN
        INSERT INTO MLAPP.DATASETS_HIST (
            DATASET_ID, NAME, TYPE, LOCATION, ADDED, DELETED, 
            IS_STRUCTURED, IS_TABELARIC, HEADERS_IN_SOURCE, 
            DESCRIPTION, ROW_MOD_DTTM, IS_ACTIVE, OPERATION_TYPE
        )
        VALUES (
            :NEW.ID, :NEW.NAME, :NEW.TYPE, :NEW.LOCATION, :NEW.ADDED, :NEW.DELETED,
            :NEW.IS_STRUCTURED, :NEW.IS_TABELARIC, :NEW.HEADERS_IN_SOURCE,
            :NEW.DESCRIPTION, :NEW.ROW_MOD_DTTM, :NEW.IS_ACTIVE, 'UPDATE'
        );
    ELSIF DELETING THEN
        INSERT INTO MLAPP.DATASETS_HIST (
            DATASET_ID, NAME, TYPE, LOCATION, ADDED, DELETED, 
            IS_STRUCTURED, IS_TABELARIC, HEADERS_IN_SOURCE, 
            DESCRIPTION, ROW_MOD_DTTM, IS_ACTIVE, OPERATION_TYPE
        )
        VALUES (
            :OLD.ID, :OLD.NAME, :OLD.TYPE, :OLD.LOCATION, :OLD.ADDED, :OLD.DELETED,
            :OLD.IS_STRUCTURED, :OLD.IS_TABELARIC, :OLD.HEADERS_IN_SOURCE,
            :OLD.DESCRIPTION, :OLD.ROW_MOD_DTTM, :OLD.IS_ACTIVE, 'DELETE'
        );
    END IF;
END;
/

ALTER TRIGGER MLAPP.TRG_DATASETS_HISTORY ENABLE;