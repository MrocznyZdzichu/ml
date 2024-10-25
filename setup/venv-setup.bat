@echo off
setlocal

set "WORK_DIR=%cd%"

cd %WORK_DIR%

cd ..

echo Creating a Python virtual environment mlops-env in %cd%
python -m venv mlops-env
call mlops-env\Scripts\activate

echo Installing Python libraries
pip install -r requirements.txt

echo Registering the venv as a Jupyter kernel
pip install ipykernel
jupyter kernelspec remove -f -y mlops-env
python -m ipykernel install --user --name=mlops-env

echo Creating databases
cd compose

docker compose up -d
timeout /t 60 /nobreak

echo Configuring the databases
cd ..\setup

set "DB_DEV_CONTAINER=mlops-db-dev-1"
set "DB_PROD_CONTAINER=mlops-db-prod-1"

docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-user.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-dataset-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-datasetdetailstab-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-models-ddl.sql
docker exec -i %DB_DEV_CONTAINER% sqlplus sys/admin as sysdba < db-app-data-roles-models.sql

docker exec -i %DB_PROD_CONTAINER% sqlplus sys/admin as sysdba < db-app-user.sql
docker exec -i %DB_PROD_CONTAINER% sqlplus sys/admin as sysdba < db-app-dataset-ddl.sql
docker exec -i %DB_PROD_CONTAINER% sqlplus sys/admin as sysdba < db-app-datasetdetailstab-ddl.sql
docker exec -i %DB_PROD_CONTAINER% sqlplus sys/admin as sysdba < db-app-models-ddl.sql
docker exec -i %DB_PROD_CONTAINER% sqlplus sys/admin as sysdba < db-app-data-roles-models.sql