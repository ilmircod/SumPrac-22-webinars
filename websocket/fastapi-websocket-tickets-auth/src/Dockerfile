FROM python:3.9.6-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
  && pip install --upgrade pip \
  && pip install poetry==1.1.6

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY . .