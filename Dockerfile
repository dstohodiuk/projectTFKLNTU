FROM python:3.12-slim

WORKDIR /code

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /code/

RUN poetry install --no-root --no-interaction --no-ansi

COPY . /code/

EXPOSE 8000