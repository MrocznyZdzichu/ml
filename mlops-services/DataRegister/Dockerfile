FROM python:3.12-slim

WORKDIR /app

COPY ["./requirements.txt", "/app"]
RUN ["pip", "install", "--no-cache-dir", "-r", "/app/requirements.txt"]

COPY ["./MLOps", "/app/MLOps"]
COPY ["./mlops-services/DataRegister/", "/app"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]