FROM python:3.12-slim

RUN ln -snf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && echo "Europe/Warsaw" > /etc/timezone

WORKDIR /app

ENV IN_DOCKER=Yes

COPY ["./requirements.txt", "/app"]
RUN ["pip", "install", "--no-cache-dir", "-r", "/app/requirements.txt"]

COPY ["./MLOps", "/app/MLOps"]
COPY ["./mlops-services/ModelManager/", "/app"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5003"]
