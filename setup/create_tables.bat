@echo off
setlocal

set "WORK_DIR=%cd%"

cd %WORK_DIR%

set "DB_DEV_CONTAINER=mlops-db-dev-1"
set "DB_PROD_CONTAINER=mlops-db-prod-1"

docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-dataset-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-datasets-hist.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-datasetdetailstab-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-models-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-data-roles-models.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-models_hist.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-columns-roles-model-hist.sql