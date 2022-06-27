FROM python:3.8.5

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VERBOSITY -1

RUN apt update
RUN apt install netcat -y
RUN apt install -y gettext libgettextpo-dev

RUN pip install --upgrade pip
RUN pip install poetry==1.0.10
COPY pyproject.toml /usr/src/app/pyproject.toml
COPY poetry.lock /usr/src/app/poetry.lock
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

ARG CI_COMMIT_SHA
ARG CI_COMMIT_REF_NAME

ENV CI_COMMIT_SHA="${CI_COMMIT_SHA}"
ENV CI_COMMIT_REF_NAME="${CI_COMMIT_REF_NAME}"

COPY . /usr/src/app/.
RUN chmod 777 /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
