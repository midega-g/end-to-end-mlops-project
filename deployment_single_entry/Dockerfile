FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./README.md /code/README.md

COPY ../src/ /code/src/

COPY ../setup.py /code/setup.py

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./mlflow_runs.db /code/mlflow_runs.db

COPY ./app /code/

EXPOSE 9696

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9696" ]